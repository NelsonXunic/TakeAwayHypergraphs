import os
import pygame
import sys
import random
import pickle
from GameStates import save_game_state, save_current_game_state, save_game_states_to_file, load_game_states_from_file, load_current_game_state, calculate_nim_value
from AI import get_possible_moves
# Dec 20, 2024
# Set up the game window dimensions (These are pixels)
width = 700
height = 700

# Change the cell size (The space that stores the vertices)
cell_size = 75

# Radius of the vertices (How big do we want the vertices to be?)
radius = cell_size // 4

# Initialize Pygame
pygame.init()

# Create the game window
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

# Colors (We will use this for graphics; other color will be added to the list as needed)
# WHITE = (255, 255, 255)
WHITE = (218,232,252)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_RED = (255, 102, 102)

# Color palettes for different types of color blindness
color_palettes = {
    "normal": {"vertex": BLUE, "edge": BLACK, "hyperedge_fill": LIGHT_RED, "hyperedge_border": RED, "text": BLACK, "background": WHITE},
    "protanopia": {"vertex": (0, 0, 255), "edge": (0, 0, 0), "hyperedge_fill": (255, 255, 0), "hyperedge_border": (255, 165, 0), "text": (0, 0, 0), "background": (255, 255, 255)},
    "deuteranopia": {"vertex": (0, 0, 255), "edge": (0, 0, 0), "hyperedge_fill": (255, 179, 0), "hyperedge_border": (255, 0, 0), "text": (0, 0, 0), "background": (255, 255, 255)},
    "tritanopia": {"vertex": (0, 255, 0), "edge": (0, 0, 0), "hyperedge_fill": (255, 179, 0), "hyperedge_border": (255, 0, 0), "text": (0, 0, 0), "background": (255, 255, 255)}
}

nim_values = {}

# Default color palette
current_palette = color_palettes["normal"]

def draw_vertices_and_hyperedges(vertices, edges, hyperedges, offset_x, offset_y):
    """
    Draws the vertices and hyperedges.

    Args:
        vertices (list): List of vertex coordinates.
        edges (list): List of edges (pairs of vertex indices).
        hyperedges (list): List of hyperedges (sets of vertex indices).
        offset_x (int): Horizontal offset for centering the grid.
        offset_y (int): Vertical offset for centering the grid.
    """

    # Draw the vertices, edges, and hyperedges. The hyperedges are boxes filled with color.
    for hyperedge in hyperedges:
        # Get the coordinates of the four vertices that form the hyperedge (top-left, top-right, bottom-right, bottom-left)
        points = [(vertices[v][0] + offset_x, vertices[v][1] + offset_y) for v in hyperedge]
        pygame.draw.polygon(screen, current_palette["hyperedge_fill"], points)  # Fill the hyperedge with color

    # Draw the edges for each pair of vertices that are adjacent to each other
    for edge in edges:
        # Get the start and end positions of the edge
        start_pos = (vertices[edge[0]][0] + offset_x, vertices[edge[0]][1] + offset_y)
        end_pos = (vertices[edge[1]][0] + offset_x, vertices[edge[1]][1] + offset_y)
        pygame.draw.line(screen, current_palette["edge"], start_pos, end_pos, radius // 2)

    # Draw the vertices as circles
    for vertex in vertices:
        pygame.draw.circle(screen, current_palette["vertex"], (vertex[0] + offset_x, vertex[1] + offset_y), radius)

    font = pygame.font.Font(None, 36)
    save_button = font.render("Save Game", True, current_palette["text"])
    save_button_rect = pygame.Rect(width - 150, height - 50, save_button.get_width(), save_button.get_height())
    pygame.draw.rect(screen, current_palette["text"], save_button_rect, 2)
    screen.blit(save_button, (width - 150, height - 50))
    pygame.display.flip()

def distance(x1, y1, x2, y2):
    """
    Calculates the distance between two points.

    Args:
        x1 (int): The x-coordinate of the first point.
        y1 (int): The y-coordinate of the first point.
        x2 (int): The x-coordinate of the second point.
        y2 (int): The y-coordinate of the second point.

    Returns:
        float: The distance between the two points.
    """
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# Helper function to check if a point is near a line segment
def point_near_line(point, start, end, threshold=5):
    """
    Checks if a point is near a line segment by calculating the distance from the point to the line segment.
    The distance threshold is used to determine how close the point should be to the line.

    Args:
        point (tuple): The coordinates of the point to be checked.
        start (tuple): The coordinates of the start point of the line segment.
        end (tuple): The coordinates of the end point of the line segment.
        threshold (int, optional): The distance threshold to consider the point near the line. Defaults to 5.

    Returns:
        bool: True if the point is near the line segment, False otherwise.
    """

    # are the start and end points the same? this means the line is a point
    if start == end:

        # if so, check if the point is near the start point meaning it is the same point
        return distance(point[0], point[1], start[0], start[1]) <= threshold

    # calculate the distance from the start point to the end point
    line_mag = distance(start[0], start[1], end[0], end[1])

    # calculate the u parameter (scalar value that represents the point on the line segment closest to the point)
    u = ((point[0] - start[0]) * (end[0] - start[0]) + (point[1] - start[1]) * (end[1] - start[1])) / (line_mag ** 2)

    # if u is less than 0 or greater than 1, the point is not on the line segment.
    if u < 0 or u > 1:
        return False

    # calculate the intersection point
    intersection = (start[0] + u * (end[0] - start[0]), start[1] + u * (end[1] - start[1]))
    return distance(point[0], point[1], intersection[0], intersection[1]) <= threshold

def point_in_polygon(point, polygon):
    """
    Checks if a point is inside a polygon by using the ray-casting algorithm which counts the number of times a ray starting from the point and going in any fixed direction, intersects the edges of the polygon.

    Args:
        point (tuple): The coordinates of the point to be checked.
        polygon (list): List of vertex coordinates that form the polygon.

    Returns:
        bool: True if the point is inside the polygon, False otherwise.
    """
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]

    # Check if the point is inside the polygon using the ray-casting algorithm (https://en.wikipedia.org/wiki/Point_in_polygon)
    for i in range(n + 1):
        # Get the current vertex. The modulo operation ensures that after the last vertex, it wraps around to the first vertex.
        p2x, p2y = polygon[i % n]

        # For each edge of the polygon, check if the y coordinate of the point is within the y range of the edge
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):

                # If the y coordinate is within the y range, check if the x coordinate is to the left of the edge
                if x <= max(p1x, p2x):

                    # if the edge is not vertical (y-coordinates are different)
                    if p1y != p2y:
                        # calculate the x coordinate of the intersection of the ray with the edge
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x

                    # if the x coordinate of the intersection is to the left of the point, toggle the inside flag
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def display_main_menu():
    """
    Displays the main menu.
    """
    # Fill the screen with the background color
    screen.fill((218,232,252))
    font = pygame.font.Font(None, 74)
    play_text = font.render('Play', True, BLACK)
    instructions_text = font.render('Instructions', True, BLACK)
    settings_text = font.render('Settings', True, BLACK)
    quit_text = font.render('Quit', True, BLACK)
    nim_value_text = font.render('Calculate Nim Value', True, BLACK)

    game_state = load_current_game_state()
    continue_color = BLACK if game_state else (128, 128, 128)
    continue_text = font.render('Continue', True, continue_color)

    # Load and display the logo
    logo = pygame.image.load('Logo.png')
    # logo = pygame.transform.scale(logo, (200, 125))
    logo_rect = logo.get_rect(center=(width // 2, 50))
    screen.blit(logo, logo_rect)

    screen.blit(play_text, (width // 2 - play_text.get_width() // 2, height // 2 - 250))
    screen.blit(continue_text, (width // 2 - continue_text.get_width() // 2, height // 2 - 150))
    screen.blit(instructions_text, (width // 2 - instructions_text.get_width() // 2, height // 2 - 50))
    screen.blit(settings_text, (width // 2 - settings_text.get_width() // 2, height // 2 + 50))
    screen.blit(nim_value_text, (width // 2 - nim_value_text.get_width() // 2, height // 2 + 150))
    screen.blit(quit_text, (width // 2 - quit_text.get_width() // 2, height // 2 + 250))
    pygame.display.flip()

def display_instruction(index, instructions, images):
    """
    Displays a single instruction screen with navigation buttons.

    Args:
        index (int): The index of the current instruction.
        instructions (list): List of instruction texts.
        images (list): List of lists of instruction images.
    """
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)

    # Display the instruction text
    title = font.render("Instructions", True, BLACK)
    screen.blit(title, (width // 2 - title.get_width() // 2, 10))
    text = font.render(instructions[index], True, BLACK)
    screen.blit(text, (50, 50))

    # Display the instruction images in a grid (2 rows and 2 columns)
    image_width = 200
    image_height = 200
    padding = 20
    start_x = (width - (2 * image_width + padding)) // 2
    start_y = 100

    for i, image in enumerate(images[index]):
        resized_image = pygame.transform.scale(image, (image_width, image_height))
        x = start_x + (i % 2) * (image_width + padding)
        y = start_y + (i // 2) * (image_height + padding)
        screen.blit(resized_image, (x, y))

    # Display navigation buttons
    next_button = font.render("Next", True, BLACK)
    prev_button = font.render("Previous", True, BLACK)
    return_button = font.render("Return to Menu", True, BLACK)
    screen.blit(next_button, (width - 150, height - 50))
    screen.blit(prev_button, (50, height - 50))
    screen.blit(return_button, (width // 2 - return_button.get_width() // 2, height - 50))

    pygame.display.flip()

def display_instructions():
    """
    Displays the instructions screen with navigation meaning the user can go to the next or previous instruction.
    """
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)
    instructions = [
        "1. Click on vertices to remove them.",
        "2. Click on edges to remove them.",
        "3. Click inside squares to remove them.",
        "4. Remove all vertices, edges, and squares to win."
    ]

    # Load images for each instruction step
    images = [
        [pygame.image.load(f'instructionsImages/R-Vertex{i+1}.png') for i in range(4)],
        [pygame.image.load(f'instructionsImages/R-Edge{i+1}.png') for i in range(4)],
        [pygame.image.load(f'instructionsImages/R-Hyper{i+1}.png')for i in range(4)],
        [pygame.image.load(f'instructionsImages/R-All{i+1}.png') for i in range(4)]
    ]
    index = 0
    in_instructions = True

    while in_instructions:
        display_instruction(index, instructions, images)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.type == pygame.K_ESCAPE:
                    in_instructions = False
                # in_instructions = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if width - 150 < x < width - 50 and height - 50 < y < height:
                    index = (index + 1) % len(instructions)
                elif 50 < x < 150 and height - 50 < y < height:
                    index = (index - 1) % len(instructions)
                elif width // 2 - 100 < x < width // 2 + 100 and height - 50 < y < height:
                    in_instructions = False

def customize_palette():
    global in_settings, in_menu
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)
    instructions = [
        "Customize Palette",
        "Enter RGB values for each color component.",
        "Press Enter to save the palette."
    ]
    for i, line in enumerate(instructions):
        text = font.render(line, True, BLACK)
        screen.blit(text, (50, 50 + i * 40))

    # Initialize the color values for the custom palette. The values are stored as RGB tuples.
    color_names = ["vertex", "edge", "hyperedge_fill", "hyperedge_border", "text", "background"]
    color_values = {name: [0, 0, 0] for name in color_names}
    active_color = 0
    active_component = 0
    input_text = ""
    cursor_visible = True
    cursor_timer = pygame.time.get_ticks()

    # Create a button to return to the settings menu
    # return_button = font.render("Return to Settings", True, BLACK)
    # return_button_rect = return_button.get_rect(center=(width // 2, height - 50))
    # pygame.draw.rect(screen, BLACK, return_button_rect, 2)
    # screen.blit(return_button, return_button_rect.topleft)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_settings = True
                    in_menu = False
                    return
                elif event.key == pygame.K_RETURN:
                    try:
                        value = int(input_text)
                        if 0 <= value <= 255:
                            color_values[color_names[active_color]][active_component] = value
                            input_text = ""
                            active_component += 1
                            if active_component > 2:
                                active_component = 0
                                active_color += 1
                                if active_color >= len(color_names):
                                    color_palettes["custom"] = {name: tuple(values) for name, values in
                                                                color_values.items()}
                                    save_custom_palette()
                                    return
                        else:
                            input_text = ""
                    except ValueError:
                        input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     if return_button_rect.collidepoint(event.pos):
            #         in_settings = True
            #         in_menu = False
                    # return

        screen.fill(WHITE)
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (50, 50 + i * 40))

        for i, name in enumerate(color_names):
            color_text = font.render(f"{name}: {color_values[name]}", True, BLACK)
            screen.blit(color_text, (50, 200 + i * 40))

        input_prompt = font.render(f"Enter {['R', 'G', 'B'][active_component]} value for {color_names[active_color]}:", True, BLACK)
        input_value = font.render(input_text, True, BLACK)
        screen.blit(input_prompt, (50, 450))
        screen.blit(input_value, (50, 500))

        # pygame.draw.rect(screen, BLACK, return_button_rect, 2)
        # screen.blit(return_button, return_button_rect.topleft)

        # Draw the live preview square
        preview_color = list(color_values[color_names[active_color]])
        try:
            value = int(input_text)
            if 0 <= value <= 255:
                preview_color[active_component] = value
        except ValueError:
            pass
        preview_color = tuple(preview_color)
        pygame.draw.rect(screen, preview_color, (475, 475, 50, 50))

        # Draw the cursor
        if pygame.time.get_ticks() - cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer = pygame.time.get_ticks()
        if cursor_visible:
            cursor = font.render('|', True, BLACK)
            screen.blit(cursor, (50 + input_value.get_width(), 500))

        pygame.display.flip()


def display_settings():
    """
    Displays the settings screen.
    """

    global current_palette, in_settings, in_menu
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)
    settings = [
        "Settings",
        "Select the color palette"
    ]
    for i, line in enumerate(settings):
        text = font.render(line, True, BLACK)
        screen.blit(text, (50, 50 + i * 40))

    # Create buttons for each palette
    palettes = ["Normal", "Protanopia", "Deuteranopia", "Tritanopia", "Customized Palette"]
    buttons = []
    for i, palette in enumerate(palettes):
        if palette.lower() in color_palettes:
            color = RED if current_palette == color_palettes[palette.lower()] else BLACK
        else:
            color = RED if palette == "Customized Palette" and current_palette == color_palettes.get("custom",
                                                                                                     {}) else BLACK
        # Create a button for each palette
        button = font.render(palette, True, color)
        # Center the button on the screen
        button_rect = button.get_rect(center=(width // 2, 150 + i * 50))
        # Draw the button on the screen
        pygame.draw.rect(screen, color, button_rect, 2)
        # Display the button text
        screen.blit(button, button_rect.topleft)
        # Add the button and palette to the list of buttons
        buttons.append((button_rect, palette))

    # Create a button to return to the main menu
    return_button = font.render("Return to Menu", True, BLACK)
    return_button_rect = return_button.get_rect(center=(width // 2, height - 50))
    pygame.draw.rect(screen, BLACK, return_button_rect, 2)
    screen.blit(return_button, return_button_rect.topleft)
    pygame.display.flip()

    in_settings = True
    while in_settings:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button_rect, palette in buttons:
                    if button_rect.collidepoint(event.pos):
                        if palette == "Normal":
                            current_palette = color_palettes["normal"]
                        elif palette == "Protanopia":
                            current_palette = color_palettes["protanopia"]
                        elif palette == "Deuteranopia":
                            current_palette = color_palettes["deuteranopia"]
                        elif palette == "Tritanopia":
                            current_palette = color_palettes["tritanopia"]
                        elif palette == "Customized Palette":
                            customize_palette()
                            current_palette = color_palettes.get("custom", {})
                        in_settings = False
                        in_menu = True
                if return_button_rect.collidepoint(event.pos):
                    in_settings = False
                    in_menu = True

def display_winner(winner):
    """
    Displays the winner screen with options to play again or return to the menu.

    Args:
        winner (str): The username of the winner.
    """
    # Fill the screen with the background color
    screen.fill(current_palette["background"])
    font = pygame.font.Font(None, 74)
    winner_text = font.render(f"Congrats {winner}! You won!", True, current_palette["text"])

    # Adjust text size if it doesn't fit the screen
    while winner_text.get_width() > width - 20:
        font = pygame.font.Font(None, font.get_height() - 2)
        winner_text = font.render(f"Congrats {winner}! You won!", True, current_palette["text"])

    play_again_text = font.render("Play Again", True, current_palette["text"])
    return_menu_text = font.render("Return to Menu", True, current_palette["text"])

    # Calculate positions based on current window size
    winner_text_pos = (width // 2 - winner_text.get_width() // 2, height // 2 - 150)
    play_again_text_pos = (width // 2 - play_again_text.get_width() // 2, height // 2)
    return_menu_text_pos = (width // 2 - return_menu_text.get_width() // 2, height // 2 + 150)

    screen.blit(winner_text, winner_text_pos)
    screen.blit(play_again_text, play_again_text_pos)
    screen.blit(return_menu_text, return_menu_text_pos)
    pygame.display.flip()

def save_custom_palette():
    with open('custom_palette.pkl', 'wb') as f:
        pickle.dump(color_palettes["custom"], f)

def load_custom_palette():
    if os.path.exists('custom_palette.pkl'):
        with open('custom_palette.pkl', 'rb') as f:
            color_palettes["custom"] = pickle.load(f)

def get_usernames():
    """
    Prompts the user to enter the usernames for the two players.

    Returns:
        tuple: The usernames of the two players.
    """

    colors = ["Red", "Blue", "Green", "Yellow", "Purple", "Orange"]
    animals = ["Panda", "Tiger", "Elephant", "Lion", "Giraffe", "Zebra"]

    # Set up the input boxes and text
    font = pygame.font.Font(None, 36)
    input_box1 = pygame.Rect(width // 2 - 150, height // 2 - 85, 300, 50)
    input_box2 = pygame.Rect(width // 2 - 150, height // 2 + 15, 300, 50)
    default_button = pygame.Rect(width // 2 - 150, height // 2 + 100, 300, 50)
    random_button = pygame.Rect(width // 2 - 150, height // 2 + 175, 300, 50)
    active1 = False
    active2 = False
    text1 = ''
    text2 = ''
    done = False
    cursor_visible = True
    cursor_timer = pygame.time.get_ticks()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Check if the user clicked on the input boxes or buttons
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box1.collidepoint(event.pos):
                    active1 = not active1
                    active2 = False
                elif input_box2.collidepoint(event.pos):
                    active2 = not active2
                    active1 = False
                elif default_button.collidepoint(event.pos):
                    text1, text2 = "Player 1", "Player 2"
                    done = True
                elif random_button.collidepoint(event.pos):
                    text1, text2 = f"{random.choice(colors)}{random.choice(animals)}{random.randint(1, 100)}", f"{random.choice(colors)}{random.choice(animals)}{random.randint(1, 100)}"
                    done = True
                else:
                    active1 = False
                    active2 = False

            # Handle key presses for entering the usernames
            elif event.type == pygame.KEYDOWN:
                if active1:
                    if event.key == pygame.K_RETURN:
                        active1 = False
                    elif event.key == pygame.K_BACKSPACE:
                        text1 = text1[:-1]
                    else:
                        text1 += event.unicode
                elif active2:
                    if event.key == pygame.K_RETURN:
                        active2 = False
                    elif event.key == pygame.K_BACKSPACE:
                        text2 = text2[:-1]
                    else:
                        text2 += event.unicode
                if not active1 and not active2 and event.key == pygame.K_RETURN:
                    done = True

        # Display the input boxes and text on the screen
        screen.fill(current_palette["background"])
        message1 = font.render("Enter Player 1 Username", True, current_palette["text"])
        message2 = font.render("Enter Player 2 Username", True, current_palette["text"])

        # Display the messages for entering the usernames
        screen.blit(message1, (width // 2 - message1.get_width() // 2, height // 2 - 125))
        screen.blit(message2, (width // 2 - message2.get_width() // 2, height // 2 - 25))
        # Display the entered text for the usernames. Meaning the user can see what they are typing.
        txt_surface1 = font.render(text1, True, current_palette["text"])
        txt_surface2 = font.render(text2, True, current_palette["text"])
        # Adjust the width of the input boxes based on the length of the entered text.
        width_box1 = max(300, txt_surface1.get_width() + 10)
        width_box2 = max(300, txt_surface2.get_width() + 10)

        #
        input_box1.w = width_box1
        input_box2.w = width_box2

        screen.blit(txt_surface1, (input_box1.x + 5, input_box1.y + 5))
        screen.blit(txt_surface2, (input_box2.x + 5, input_box2.y + 5))
        # Draw the input boxes and buttons
        pygame.draw.rect(screen, current_palette["text"], input_box1, 2)
        pygame.draw.rect(screen, current_palette["text"], input_box2, 2)

        default_text = font.render("Use Default Usernames", True, current_palette["text"])
        random_text = font.render("Use Random Usernames", True, current_palette["text"])
        screen.blit(default_text, (default_button.x + 10, default_button.y + 10))
        screen.blit(random_text, (random_button.x + 10, random_button.y + 10))
        pygame.draw.rect(screen, current_palette["text"], default_button, 2)
        pygame.draw.rect(screen, current_palette["text"], random_button, 2)

        if active1:
            if pygame.time.get_ticks() - cursor_timer > 500:
                cursor_visible = not cursor_visible
                cursor_timer = pygame.time.get_ticks()
            if cursor_visible:
                cursor = font.render('|', True, current_palette["text"])
                screen.blit(cursor, (input_box1.x + txt_surface1.get_width() + 5, input_box1.y + 5))
        elif active2:
            if pygame.time.get_ticks() - cursor_timer > 500:
                cursor_visible = not cursor_visible
                cursor_timer = pygame.time.get_ticks()
            if cursor_visible:
                cursor = font.render('|', True, current_palette["text"])
                screen.blit(cursor, (input_box2.x + txt_surface2.get_width() + 5, input_box2.y + 5))

        pygame.display.flip()

    return text1, text2


def get_board_size():
    """
    Prompts the user to enter the number of rows and columns for the board.

    Returns:
        tuple: The number of rows and columns for the board.
    """
    cols: int
    rows, cols = 4, 4  # Default size

    # Set up the input boxes and default button
    box_width = 275
    button_width = 275
    input_box_rows = pygame.Rect((width - box_width) // 2, height // 2 - 85, box_width, 50)
    input_box_cols = pygame.Rect((width - box_width) // 2, height // 2 + 15, box_width, 50)
    default_button = pygame.Rect((width - button_width) // 2 , height // 2 + 100, button_width, 50)

    # Set up the text and cursor for entering the number of rows and columns
    font = pygame.font.Font(None, 36)
    active_rows = False
    active_cols = False
    text_rows = ''
    text_cols = ''
    done = False
    cursor_visible = True
    cursor_timer = pygame.time.get_ticks()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the user clicked on the input boxes or default button
                if input_box_rows.collidepoint(event.pos):
                    active_rows = not active_rows
                    active_cols = False
                elif input_box_cols.collidepoint(event.pos):
                    active_cols = not active_cols
                    active_rows = False
                elif default_button.collidepoint(event.pos):
                    done = True
                else:
                    active_rows = False
                    active_cols = False
            elif event.type == pygame.KEYDOWN:
                # Handle key presses for entering the number of rows and columns
                if active_rows:
                    # Check if the user pressed Enter to submit the number of rows
                    if event.key == pygame.K_RETURN:
                        # Try to convert the entered text to an integer
                        try:
                            rows = int(text_rows)
                            active_rows = False
                        # If the conversion fails, clear the text
                        except ValueError:
                            text_rows = ''
                    # Check if the user pressed Backspace to delete a character
                    elif event.key == pygame.K_BACKSPACE:
                        text_rows = text_rows[:-1]
                    # Add the entered character to the text
                    else:
                        text_rows += event.unicode
                # Handle key presses for entering the number of columns
                elif active_cols:
                    # Check if the user pressed Enter to submit the number of columns
                    if event.key == pygame.K_RETURN:
                        # Try to convert the entered text to an integer
                        try:
                            cols = int(text_cols)
                            active_cols = False
                        # If the conversion fails, clear the text
                        except ValueError:
                            text_cols = ''
                    # Check if the user pressed Backspace to delete a character
                    elif event.key == pygame.K_BACKSPACE:
                        text_cols = text_cols[:-1]
                    # Add the entered character to the text
                    else:
                        text_cols += event.unicode

                # Check if the user pressed Enter to submit the board size after entering both rows and columns
                if not active_rows and not active_cols and event.key == pygame.K_RETURN:
                    # Try to convert the entered text to integers
                    try:
                        if text_rows:
                            rows = int(text_rows)
                        if text_cols:
                            cols = int(text_cols)
                    # If the conversion fails, use the default size
                    except ValueError:
                        text_rows = ''
                        text_cols = ''
                    done = True

        screen.fill(current_palette["background"])

        # Display the messages for entering the number of rows and columns
        message_rows = font.render("Enter number of rows (max 9)", True, current_palette["text"])
        message_cols = font.render("Enter number of columns (max 9)", True, current_palette["text"])
        screen.blit(message_rows, (width // 2 - message_rows.get_width() // 2, height // 2 - 125))
        screen.blit(message_cols, (width // 2 - message_cols.get_width() // 2, height // 2 - 25))

        # Display the entered text for the number of rows and columns. Meaning the user can see what they are typing.
        txt_surface_rows = font.render(text_rows, True, current_palette["text"])
        txt_surface_cols = font.render(text_cols, True, current_palette["text"])

        # Adjust the width of the input boxes based on the length of the entered text.
        width_box_rows = max(box_width, txt_surface_rows.get_width() + 10)
        width_box_cols = max(box_width, txt_surface_cols.get_width() + 10)
        input_box_rows.w = width_box_rows
        input_box_cols.w = width_box_cols

        # Display the entered text in the input boxes. The text will be displayed in the top left corner of the input box.
        screen.blit(txt_surface_rows, (input_box_rows.x + 5, input_box_rows.y + 5))
        screen.blit(txt_surface_cols, (input_box_cols.x + 5, input_box_cols.y + 5))

        # Draw the input boxes and default button
        pygame.draw.rect(screen, current_palette["text"], input_box_rows, 4)
        pygame.draw.rect(screen, current_palette["text"], input_box_cols, 4)
        pygame.draw.rect(screen, current_palette["text"], default_button, 4)

        # Display the default button text
        default_text = font.render("Use default size (4X4)", True, current_palette["text"])
        screen.blit(default_text, (default_button.x + 10, default_button.y + 10))

        # Display the cursor for entering text for the number of rows
        if active_rows:
            # Toggle the cursor visibility every 500 milliseconds
            if pygame.time.get_ticks() - cursor_timer > 500:
                cursor_visible = not cursor_visible
                cursor_timer = pygame.time.get_ticks()

            # Display the cursor if it is visible
            if cursor_visible:
                cursor = font.render('|', True, current_palette["text"])
                screen.blit(cursor, (input_box_rows.x + txt_surface_rows.get_width() + 5, input_box_rows.y + 5))

        # Display the cursor for entering text for the number of columns
        elif active_cols:
            # Toggle the cursor visibility every 500 milliseconds
            if pygame.time.get_ticks() - cursor_timer > 500:
                cursor_visible = not cursor_visible
                cursor_timer = pygame.time.get_ticks()

            # Display the cursor if it is visible
            if cursor_visible:
                cursor = font.render('|', True, current_palette["text"])
                screen.blit(cursor, (input_box_cols.x + txt_surface_cols.get_width() + 5, input_box_cols.y + 5))

        # Update the display
        pygame.display.flip()

    return rows, cols

def display_nim_value(vertices, edges, hyperedges, nim_value, rows, cols):
    """
    Displays the board and the calculated Nim value on the screen.

    Args:
        vertices (list): List of vertex coordinates.
        edges (list): List of edges (pairs of vertex indices).
        hyperedges (list): List of hyperedges (sets of vertex indices).
        nim_value (int): The calculated Nim value.
        rows (int): Number of rows in the board.
        cols (int): Number of columns in the board.
    """
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    nim_value_text = font.render(f"Nim Value: {nim_value}", True, BLACK)
    screen.blit(nim_value_text, (width // 2 - nim_value_text.get_width() // 2, 50))

    # Calculate offsets to center the grid
    offset_x = (width - cols * cell_size) // 2
    offset_y = (height - rows * cell_size) // 2 + 100  # Adjust for Nim value text

    # Draw the vertices, edges, and hyperedges
    draw_vertices_and_hyperedges(vertices, edges, hyperedges, offset_x, offset_y)

    pygame.display.flip()
    pygame.time.wait(3000)  # Display the result for 3 seconds

def calculate_nim_value_menu():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)
    instructions = [
        "Enter the number of rows and columns for the board.",
        "Press Enter to calculate the Nim value."
    ]
    for i, line in enumerate(instructions):
        text = font.render(line, True, BLACK)
        screen.blit(text, (50, 50 + i * 40))

    input_box_rows = pygame.Rect((width - 275) // 2, height // 2 - 85, 275, 50)
    input_box_cols = pygame.Rect((width - 275) // 2, height // 2 + 15, 275, 50)
    active_rows = False
    active_cols = False
    text_rows = ''
    text_cols = ''
    done = False
    cursor_visible = True
    cursor_timer = pygame.time.get_ticks()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box_rows.collidepoint(event.pos):
                    active_rows = True
                    active_cols = False
                elif input_box_cols.collidepoint(event.pos):
                    active_rows = False
                    active_cols = True
                else:
                    active_rows = False
                    active_cols = False
            elif event.type == pygame.KEYDOWN:
                if active_rows:
                    if event.key == pygame.K_RETURN:
                        active_rows = False
                    elif event.key == pygame.K_BACKSPACE:
                        text_rows = text_rows[:-1]
                    else:
                        text_rows += event.unicode
                elif active_cols:
                    if event.key == pygame.K_RETURN:
                        active_cols = False
                    elif event.key == pygame.K_BACKSPACE:
                        text_cols = text_cols[:-1]
                    else:
                        text_cols += event.unicode
                elif event.key == pygame.K_RETURN:
                    rows = int(text_rows)
                    cols = int(text_cols)
                    vertices = [(col * cell_size + cell_size // 2, row * cell_size + cell_size // 2) for row in range(rows) for col in range(cols)]
                    edges = [(row * cols + col, row * cols + col + 1) for row in range(rows) for col in range(cols - 1)] + [(row * cols + col, (row + 1) * cols + col) for row in range(rows - 1) for col in range(cols)]
                    hyperedges = [(row * cols + col, row * cols + col + 1, (row + 1) * cols + col + 1, (row + 1) * cols + col) for row in range(rows - 1) for col in range(cols - 1)]
                    nim_value = calculate_nim_value(vertices, edges, hyperedges)
                    display_nim_value(vertices, edges, hyperedges, nim_value, rows, cols)
                    done = True

        screen.fill(WHITE)
        for i, line in enumerate(instructions):
            text = font.render(line, True, BLACK)
            screen.blit(text, (50, 50 + i * 40))

        txt_surface_rows = font.render(text_rows, True, BLACK)
        txt_surface_cols = font.render(text_cols, True, BLACK)
        width_box_rows = max(275, txt_surface_rows.get_width() + 10)
        width_box_cols = max(275, txt_surface_cols.get_width() + 10)
        input_box_rows.w = width_box_rows
        input_box_cols.w = width_box_cols

        screen.blit(txt_surface_rows, (input_box_rows.x + 5, input_box_rows.y + 5))
        screen.blit(txt_surface_cols, (input_box_cols.x + 5, input_box_cols.y + 5))
        pygame.draw.rect(screen, BLACK, input_box_rows, 2)
        pygame.draw.rect(screen, BLACK, input_box_cols, 2)

        if active_rows:
            if pygame.time.get_ticks() - cursor_timer > 500:
                cursor_visible = not cursor_visible
                cursor_timer = pygame.time.get_ticks()
            if cursor_visible:
                cursor = font.render('|', True, BLACK)
                screen.blit(cursor, (input_box_rows.x + txt_surface_rows.get_width() + 5, input_box_rows.y + 5))
        elif active_cols:
            if pygame.time.get_ticks() - cursor_timer > 500:
                cursor_visible = not cursor_visible
                cursor_timer = pygame.time.get_ticks()
            if cursor_visible:
                cursor = font.render('|', True, BLACK)
                screen.blit(cursor, (input_box_cols.x + txt_surface_cols.get_width() + 5, input_box_cols.y + 5))

        pygame.display.flip()

def delete_existing_game_states_file(filename):
    if os.path.exists(filename):
        os.remove(filename)

def delete_current_game_state():
    if os.path.exists('current_game_state.pkl'):
        os.remove('current_game_state.pkl')

def main():
    """
    Main function to run the game loop.
    """
    # delete_existing_game_states_file('game_states.pkl')
    delete_current_game_state()
    # Load the game states from a file when the game starts
    load_game_states_from_file('game_states.pkl')
    load_custom_palette()

    # Initialize game state variables
    global current_palette, width, height, screen
    running = True
    in_menu = True
    in_instructions = False
    in_game = False
    in_settings = False
    in_winner_screen = False
    in_nim_value = False
    player1, player2 = "", ""
    current_player = 1
    winner = ""
    vertices, edges, hyperedges = [], [], []
    loaded_from_saved_state = False # Flag to check if the game was loaded from a saved state

    # Initialize Pygame with double buffering
    pygame.init()
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE | pygame.DOUBLEBUF)

    while running:
        # Handle events for the main menu and instructions screens
        for event in pygame.event.get():
            # Check if the user closed the window
            if event.type == pygame.QUIT:
                running = False
            # Check if the user resized the window
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_menu = True
                    in_instructions = False
                    in_game = False
                    in_settings = False
                    in_winner_screen = False
                    in_nim_value = False
            # Check if the user clicked on the screen
            elif event.type == pygame.MOUSEBUTTONDOWN and in_menu:
                x, y = event.pos
                # Check if the click is within the buttons on the main menu
                if width // 2 - 100 < x < width // 2 + 100:
                    if height // 2 - 250 < y < height // 2 - 150:
                        in_menu = False
                        in_game = True
                        player1, player2 = get_usernames()
                        rows, cols = get_board_size()
                        vertices = [(col * cell_size + cell_size // 2, row * cell_size + cell_size // 2) for row in
                                    range(rows) for col in range(cols)]
                        edges = [(row * cols + col, row * cols + col + 1) for row in range(rows) for col in
                                 range(cols - 1)] + [(row * cols + col, (row + 1) * cols + col) for row in
                                                     range(rows - 1) for col in range(cols)]
                        hyperedges = [
                            (row * cols + col, row * cols + col + 1, (row + 1) * cols + col + 1, (row + 1) * cols + col)
                            for row in range(rows - 1) for col in range(cols - 1)]
                    elif height // 2 - 150 < y < height // 2 - 50:
                        game_state = load_current_game_state()
                        if game_state:
                            vertices, edges, hyperedges = game_state['vertices'], game_state['edges'], game_state[
                                'hyperedges']
                            player1, player2 = game_state['player1'], game_state['player2']
                            current_player = game_state['current_player']
                            in_menu = False
                            in_game = True
                            loaded_from_saved_state = True
                    elif height // 2 - 50 < y < height // 2 + 50:
                        in_menu = False
                        in_instructions = True
                    elif height // 2 + 50 < y < height // 2 + 150:
                        in_menu = False
                        in_settings = True
                    elif height // 2 + 150 < y < height // 2 + 250:
                        in_menu = False
                        in_nim_value = True
                    elif height // 2 + 250 < y < height // 2 + 350:
                        running = False

        #     Check if the user pressed a key to return to the main menu from the instructions or settings screens
        #     elif event.type == pygame.KEYDOWN and in_instructions:
        #         in_instructions = False
        #         in_menu = True
        #     elif event.type == pygame.KEYDOWN and in_settings:
        #         if event.key == pygame.K_ESCAPE:
        #             in_settings = False
        #             in_menu = True
        #     Check if the user pressed a key to return to the main menu from the settings screen
        #     elif event.type == pygame.KEYDOWN and in_settings:
        #         if event.key == pygame.K_1:
        #             current_palette = color_palettes["normal"]
        #         elif event.key == pygame.K_2:
        #             current_palette = color_palettes["protanopia"]
        #         elif event.key == pygame.K_3:
        #             current_palette = color_palettes["deuteranopia"]
        #         elif event.key == pygame.K_4:
        #             current_palette = color_palettes["tritanopia"]
        #         elif event.key == pygame.K_ESCAPE:
        #             in_settings = False
        #             in_menu = True
        # # Display the main menu, instructions, settings, game, or winner screen based on the current state
        if in_menu:
            display_main_menu()
        elif in_instructions:
            display_instructions()
            in_instructions = False
            in_menu = True
        elif in_settings:
            display_settings()
            in_settings = False
            in_menu = True
        elif in_game:
            offset_x = (width - cols * cell_size) // 2
            offset_y = (height - rows * cell_size) // 2
            # Get the usernames
            # if not player1 and not player2:
            #     player1, player2 = get_usernames()

            # Get board size from user
            # rows, cols = get_board_size()
            #
            # # Initialize game state
            # vertices = []
            # edges = []
            # hyperedges = []
            #
            # # Create vertices based on the board size
            # for row in range(rows):
            #     for col in range(cols):
            #         # Append the center of each cell as a vertex
            #         vertices.append((col * cell_size + cell_size // 2, row * cell_size + cell_size // 2))
            #
            # # Create edges based on the vertices. An edge connects two adjacent vertices (This will be the initial state)
            # # Horizontal edges(adjacent vertices in the same row)
            # for row in range(rows):
            #     for col in range(cols - 1):
            #         # Append the indices of the two vertices that form the edge
            #         edges.append((row * cols + col, row * cols + col + 1))
            #
            # # Vertical edges (adjacent vertices in the same column)
            # for row in range(rows - 1):
            #     for col in range(cols):
            #         # Append the indices of the two vertices that form the edge
            #         edges.append((row * cols + col, (row + 1) * cols + col))
            #
            # # Create hyperedges
            # # Hyperedges are formed by connecting four adjacent vertices (one from each corner of a cell)
            # for row in range(rows - 1):
            #     for col in range(cols - 1):
            #         # Append the indices of the four vertices that form the hyperedge. The order is top-left, top-right, bottom-right, bottom-left
            #         hyperedges.append((row * cols + col, row * cols + col + 1, (row + 1) * cols + col + 1, (row + 1) * cols + col))
            #
            # Calculate offsets to center the grid
            # offset_x = (width - cols * cell_size) // 2
            # offset_y = (height - rows * cell_size) // 2
            screen.fill(current_palette["background"])
            draw_vertices_and_hyperedges(vertices, edges, hyperedges, offset_x, offset_y)
            font = pygame.font.Font(None, 36)
            hide_color1 = RED if current_player == 1 else (220, 220, 220)
            hide_color2 = RED if current_player == 2 else (220, 220, 220)
            player1_text = font.render(f"{player1}'s turn", True, hide_color1)
            screen.blit(player1_text, (10, 10))
            player2_text = font.render(f"{player2}'s turn", True, hide_color2)
            screen.blit(player2_text, (width - player2_text.get_width() - 10, 10))
            pygame.display.update()
            while running and in_game:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save_current_game_state(vertices, edges, hyperedges, player1, player2, current_player)
                        in_game = False
                        in_menu = True
                        # running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            save_current_game_state(vertices, edges, hyperedges, player1, player2, current_player)
                            in_game = False
                            in_menu = True
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Check if the user clicked on a vertex, edge, or hyperedge to remove it
                        x, y = event.pos
                        # Check if the click is within the visible game grid
                        if offset_x <= x < offset_x + cols * cell_size and offset_y <= y < offset_y + rows * cell_size:
                            # Check if the click is inside a vertex
                            for i, vertex in enumerate(vertices[:]):
                                # Check if the click is within the radius of the vertex. If so, remove the vertex and its connected edges and hyperedges
                                if distance(x, y, vertex[0] + offset_x, vertex[1] + offset_y) <= radius:
                                    vertices.pop(i)
                                    # Remove edges connected to the vertex
                                    edges = [edge for edge in edges if i not in edge]
                                    # Remove hyperedges connected to the vertex
                                    hyperedges = [hyperedge for hyperedge in hyperedges if i not in hyperedge]
                                    # Update indices in edges and hyperedges
                                    edges = [(v1 if v1 < i else v1 - 1, v2 if v2 < i else v2 - 1) for v1, v2 in edges]
                                    hyperedges = [[v if v < i else v - 1 for v in hyperedge] for hyperedge in hyperedges]

                                    # Switch players
                                    current_player = 2 if current_player == 1 else 1

                                    # Save the game state by calling the save_game_state function
                                    save_game_state(vertices, edges, hyperedges)
                                    break

                            # Check if the click is on an edge
                            for edge in edges[:]:
                                # Get the start and end positions of the edge
                                start_pos = (vertices[edge[0]][0] + offset_x, vertices[edge[0]][1] + offset_y)
                                end_pos = (vertices[edge[1]][0] + offset_x, vertices[edge[1]][1] + offset_y)

                                # Check if the click is near the edge (within a threshold distance).
                                # If so, remove the edge and hyperedges connected to it.
                                if point_near_line((x, y), start_pos, end_pos):
                                    edges.remove(edge)
                                    # Remove hyperedges connected to the edge
                                    v1, v2 = edge
                                    hyperedges = [hyperedge for hyperedge in hyperedges if not (v1 in hyperedge and v2 in hyperedge)]

                                    # Switch players
                                    current_player = 2 if current_player == 1 else 1

                                    # Save the game state by calling the save_game_state function
                                    save_game_state(vertices, edges, hyperedges,)
                                    break

                            # Check if the click is inside a hyperedge
                            for hyperedge in hyperedges[:]:
                                # Get the vertices that form the hyperedge
                                points = [(vertices[v][0] + offset_x, vertices[v][1] + offset_y) for v in hyperedge]

                                # Check if the click is inside the polygon formed by the hyperedge vertices.
                                if point_in_polygon((x, y), points):
                                    # Remove the hyperedge
                                    hyperedges.remove(hyperedge)

                                    # Switch players
                                    current_player = 2 if current_player == 1 else 1

                                    # Save the game state by calling the save_game_state function
                                    save_game_state(vertices, edges, hyperedges)
                                    break
                        if width - 150 < x < width - 50 and height - 50 < y < height:
                            save_current_game_state(vertices, edges, hyperedges, player1, player2, current_player)
                            # save_game_states_to_file('game_states.pkl')
                            in_game = False
                            in_menu = True

                # screen.fill(current_palette["background"])
                # Check if the game is over (no vertices, edges, or hyperedges left)
                if not vertices and not edges and not hyperedges:
                    winner = player1 if current_player == 2 else player2
                    in_game = False
                    in_winner_screen = True
                    # save_game_states_to_file('game_states.pkl')
                    if loaded_from_saved_state:
                        delete_current_game_state()
                    print(f"Game over! {winner} wins!")
                screen.fill(current_palette["background"])
                draw_vertices_and_hyperedges(vertices, edges, hyperedges, offset_x, offset_y)
                font = pygame.font.Font(None, 36)
                hide_color1 =  RED if current_player == 1 else (220,220,220)
                hide_color2 =  RED if current_player == 2 else (220,220,220)
                player1_text = font.render(f"{player1}'s turn", True, hide_color1)
                screen.blit(player1_text, (10, 10))
                player2_text = font.render(f"{player2}'s turn", True, hide_color2)
                screen.blit(player2_text, (width - player2_text.get_width() - 10, 10))
                pygame.display.update()
                # if current_player == 1:
                #     player1_text = font.render(f"{player1}'s turn", True, current_palette["text"])
                #     screen.blit(player1_text, (10, 10))
                # else:
                #     player2_text = font.render(f"{player2}'s turn", True, current_palette["text"])
                #     screen.blit(player2_text, (width - player2_text.get_width() - 10, 10))
                # pygame.display.flip()
        elif in_winner_screen:
            display_winner(winner)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # in_winner_screen = False
                    # in_menu = True
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if width // 2 - 150 < x < width // 2 + 150:
                        if height // 2 < y < height // 2 + 100:
                            in_winner_screen = False
                            in_game = True
                        elif height // 2 + 150 < y < height // 2 + 250:
                            in_winner_screen = False
                            in_menu = True

        elif in_nim_value:
            calculate_nim_value_menu()
            in_nim_value = False
            in_menu = True

    # Save the game states to a file when the game ends
    save_game_states_to_file('game_states.pkl')

if __name__ == "__main__":
    main()



