import math
 # Dec 21, 2024 NDXC-- Moving the program to a Pygame window.
import pygame
import re
import numpy as np
# Dec 19, 2024 NDXC-- This is a package that is not installed by default. You can install it with pip install oapackage.
# It does not work, so I commented it out. Instead, I used networkx.

# import oapackage
import pickle
import networkx as nx

from TakeAway import radius

# Dec 21, 2024 NDXC-- Setting up the Pygame window ##############################
# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Nim Value Calculator")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Define fonts
font = pygame.font.Font(None, 36)

# Input fields
vertex_input = ""
edges_input = ""
edges = []
input_active = None
delete_mode = False

# Load or initialize the graphs dictionary
try:
    with open("graphs.dict", "rb") as file:
        graphs = pickle.load(file)
except FileNotFoundError:
    graphs = {}

def draw_text(text, x, y, color=BLACK, font_size=30):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

    return text_surface.get_width()

def draw_vertices(vertices):
    for i, vertex in enumerate(vertices):
        pygame.draw.circle(screen, BLUE, vertex, 15)
        draw_text(str(i), vertex[0] - 5, vertex[1] - 10, WHITE, font_size=18)

def draw_edges(edges, vertices):
    for edge in edges:
        start = vertices[edge[0]]
        end = vertices[edge[1]]
        pygame.draw.line(screen, BLACK, start, end, 2)

def get_vertex_at_pos(pos, vertices):
    for i, vertex in enumerate(vertices):
        if math.dist(vertex, pos) < 10:
            return i
    return None

def get_edge_at_pos(pos, vertices, edges):
    for i, edge in enumerate(edges):
        start = vertices[edge[0]]
        end = vertices[edge[1]]
        if point_near_line(pos, start, end):
            return i
    return None

def point_near_line(point, start, end, threshold=5):
    line_mag = math.dist(start, end)
    if line_mag < 0.000001:
        return False
    u = ((point[0] - start[0]) * (end[0] - start[0]) + (point[1] - start[1]) * (end[1] - start[1])) / (line_mag ** 2)
    if u < 0 or u > 1:
        return False
    intersection = (start[0] + u * (end[0] - start[0]), start[1] + u * (end[1] - start[1]))
    return math.dist(point, intersection) < threshold
################################################################################
# Dec 19, 2024 NDXC-- This variable allows the user to input the number of partitions they want to split the graph into.
# You can change this to a number instead of having to type it in each time.
# Change it back to "0" without the quotes to have it ask each time.
# MANUAL_PARTITE = 0
#
# def getTripartiteEdges(vertexCount, partitionsList):
#     """
#     Dec 19, 2024 NDXC-- This function generates the edges for a tripartite graph given the number of vertices and the number of partitions.
#     :param vertexCount: An integer representing the number of vertices in the graph
#     :param partitionsList: A list of integers representing the number of vertices in each partition. Each integer in the list represents a partition so the length of the list is the number of partitions.
#     :return: A list of tuples representing the edges in the graph
#     """
#     # Dec 19, 2024 NDXC-- This is a list of the sum of the vertices in each partition. This is used to determine the range of vertices in each partition.
#     sums = []
#     # Dec 19, 2024 NDXC-- This loop calculates the sum of the vertices in each partition by iterating through the partitionsList. The first partition is just the first value in the list. The rest are the sum of the previous partition and the current partition.
#     for i, partitionValue in enumerate(partitionsList):
#         if i == 0:
#             sums.append(partitionValue)
#         else:
#             sums.append(sums[-1] + partitionValue)
#
#     # Dec 19, 2024 NDXC-- This checks if the sum of the partitions is equal to the number of vertices. If it is not, it returns an error message.
#     if sums[-1] != vertexCount:
#         return f"Unfortunately, your values sum to be {sums[-1]} which is not equal to {vertexCount}. Try again! ○|￣|_"
#
#     # Dec 19, 2024 NDXC-- This creates a list of ranges for each partition. The first partition is just the range of
#     # the first partition value. The rest are the range of the sum of the previous partition and the current partition.
#     partitions = []
#     for i in range(len(partitionsList)):
#         if i > 0:
#             partitions.append(range(sums[i - 1], sums[i]))
#         else:
#             partitions.append(range(sums[i]))
#
#     # first = list(range(firstCount))
#     # second = list(range(firstCount, firstCount + secondCount))
#     # third = list(range(firstCount + secondCount, firstCount + secondCount + thirdCount))
#
#     # Dec 19, 2024 NDXC-- This is a list of edges that will be returned. It is empty at the start.
#     edges = []
#     # Connect first verticies to all in the second and third partitions
#
#     # Dec 19, 2024 NDXC-- This loop connects all the vertices in the first partition to all the vertices in the second
#     # and third partitions. The first loop is for the first partition. The second loop is for the second partition.
#     # The third loop is for the third partition. The fourth loop is for the vertices in the second and third partitions.
#     for startPartitionNum, startPartition in enumerate(partitions):
#         for startVertex in startPartition:
#             for endPartitionNum in range(startPartitionNum + 1, len(partitions)):
#                 for endVertex in partitions[endPartitionNum]:
#                     edges.append((startVertex, endVertex))
#
#
#     return edges

# def inverse_permutation(perm):
#     """
#     Dec 19, 2024 NDXC-- This function returns the inverse of a permutation. The inverse of a permutation is a permutation that undoes the effect of the original permutation.
#     :param perm: The permutation to find the inverse of as a list of integers representing the permutation
#     :return: The inverse of the permutation as a list of integers
#     """
#     inverse = [0] * len(perm)
#     for i, p in enumerate(perm):
#         inverse[p] = i
#     return inverse

def reduce(graph):
    """
    Dec 19, 2024 NDXC-- This function reduces the graph to its canonical form, which is defined as the graph with the smallest
    lexicographically ordered adjacency matrix. This means that the graph is reduced to its smallest form.

    :param graph: The graph to be reduced
    :return: The reduced graph
    """
    # Dec 19, 2024 NDXC-- This has been commented out because the need package cannot be installed.
    # tr = oapackage.reduceGraphNauty(graph, verbose=0)
    # tri = inverse_permutation(tr)
    #
    # graph_reduced = oapackage.transformGraphMatrix(graph, tri)
    # return graph_reduced
    G = nx.from_numpy_array(graph)
    G = nx.convert_node_labels_to_integers(G)
    adj_matrix = nx.to_numpy_array(G)
    return adj_matrix

def attachEdges(graph, edges: []):
    """
    Dec 19, 2024 NDXC-- This function attaches the edges to the graph which is represented as a numpy array.
    :param graph: The graph to attach the edges to as a numpy array
    :param edges: The edges to attach in the form of a list of tuples
    :return: The graph with the edges attached
    """
    for edge in edges:
        first = edge[0]
        second = edge[1]
        graph[first, second] = 1
    return np.maximum(graph, graph.T)  # make array symmetric


def removeVertex(original, vertex):
    """
    Dec 19, 2024 NDXC-- Given a vertex, this function removes the vertex from the graph.
    :param original: A numpy array representing the graph
    :param vertex: The vertex to remove as an integer
    :return: The graph with the vertex removed
    """
    return np.delete(np.delete(original, vertex, 0), vertex, 1)


def removeEdge(original, edge: (int, int)):
    """
    Dec 19, 2024 NDXC-- Given an edge, this function removes the edge from the graph.
    :param original: A numpy array representing the graph
    :param edge: The edge to remove as a tuple of two integers
    :return: The graph with the edge removed
    """
    newgraph = original.copy()
    newgraph[edge[0], edge[1]] = 0
    newgraph[edge[1], edge[0]] = 0
    return newgraph


def getVertexMoves(original):
    """
    Dec 19, 2024 NDXC-- This function gets the vertex moves for the graph. This is the list of vertices in the graph.
    :param original: A numpy array representing the graph
    :return: A list of vertices in the graph
    """
    return list(range(len(original)))


def getEdgeMoves(original):
    """
    Dec 19, 2024 NDXC-- This function gets the edge moves for the graph. This is the list of edges in the graph.
    :param original: A numpy array representing the graph
    :return: A list of edges in the graph each represented as a tuple of two integers
    """
    height, width = original.shape
    edges = []
    for row in range(height):
        for col in range(row, width):
            if original[row, col] == 1:
                edges.append((row, col))
    return edges


def getNimValue(original):
    """
    Dec 19, 2024 NDXC-- This function gets the nim value of the graph using the Sprague-Grundy theorem.
    :param original: A numpy array representing the graph
    :return: The nim value of the graph
    """
    # Dec 19, 2024 NDXC-- This is a dictionary that stores the nim values of the graphs. This is used to store the
    # nim values of the graphs that have already been calculated. Reduced is the reduced form of the graph. graphKey
    # is the string representation of the reduced graph. nimValue is the nim value of the graph.
    global graphs
    reduced = reduce(original)
    graphKey = str(reduced)
    nimValue = graphs.get(graphKey, None)

    # Dec 19, 2024 NDXC-- If the nim value of the graph has already been calculated, it returns the nim value.
    if nimValue is not None:
        return nimValue

    #  Dec 19, 2024 NDXC-- This is the base case for the Sprague-Grundy theorem. If the graph is empty, the nim value is 0.
    childGraphs = []

    # Dec 19, 2024 NDXC-- This is the recursive case for the Sprague-Grundy theorem. It calculates the nim value of the
    # graph by calculating the nim values of the child graphs. The nim value of the graph is the mex of the nim values of
    # the child graphs.

    # Dec 19, 2024 NDXC-- This loop gets the child graphs of the graph that are obtained by removing a vertex from the
    #graph. The child graphs are stored in the childGraphs list.
    for vertex in getVertexMoves(reduced):
        # childGraphs.append(removeVertex(reduced, vertex))
        # Dec 21, 2024 NDXC-- This is the list of child graphs that are obtained by removing a vertex from the graph.
        childGraphs.append(np.delete(np.delete(reduced, vertex, 0), vertex, 1))

    # Dec 21, 2024 NDXC-- These loops get the child graphs of the graph that are obtained by removing an edge from the
    # graph. If the edge is in the graph, the edge is removed and the new graph is added to the childGraphs list.
    for row in range(len(reduced)):
        for col in range(row, len(reduced)):
            if reduced[row, col] == 1:
                new_graph = reduced.copy()
                new_graph[row, col] = 0
                new_graph[col, row] = 0
                childGraphs.append(new_graph)
                # childGraphs.append(removeEdge(reduced, (row, col)))

    # Dec 19, 2024 NDXC-- This loop gets the child graphs of the graph obtained by removing an edge from the graph.
    # The child graphs are stored in the childGraphs list.
    # for edgeMove in getEdgeMoves(reduced):
    #     childGraphs.append(removeEdge(reduced, edgeMove))

    # Dec 19, 2024 NDXC-- This is the set of the nim values of the child graphs. This is used to calculate the mex of the
    # nim values of the child graphs.
    childNimValues = set()

    # Dec 19, 2024 NDXC-- This loop calculates the nim values of the child graphs and adds them to the set of nim values.
    for graph in childGraphs:
        childNimValues.add(getNimValue(graph))

    # Dec 19, 2024 NDXC-- childNimValues is converted to a list and sorted. This is used to find the mex of the nim values.
    childNimValues = list(childNimValues)
    childNimValues.sort()

    # Dec 19, 2024 NDXC-- This loop finds the mex of the nim values of the child graphs. The mex is the smallest non-negative

    for i in range(len(childNimValues)):
        if i != childNimValues[i]:
            graphs[graphKey] = i
            return i

    # add the next highest Nim Value in childNimValue
    graphs[graphKey] = len(childNimValues)
    return len(childNimValues)


def main():
    """
    Dec 19, 2024 NDXC-- This is the main function that allows the user to input the graph and then calculates the nim value of the graph.
    :return: None
    """
    global graphs, MANUAL_PARTITE
    # Dec 21, 2024 NDXC-- Variables for the input fields
    global vertex_input, edges_input, input_active, vertices, edges, selected_vertex, delete_mode
    running = True
    result = None
    vertices = []
    selected_vertex = None

    # Dec 21, 2024 NDXC-- Main loop
    while running:
        screen.fill(WHITE)
        # draw_text("Tripartite Graph Nim Value Calculator", 20, 20)
        vertices_text = "Number of vertices:"
        draw_text(vertices_text, 20, 20)
        pygame.draw.rect(screen, GRAY if input_active == "vertices" else WHITE, (300, 20, 200, 36))
        pygame.draw.rect(screen, GRAY, (300, 20, 200, 36),2)
        draw_text(vertex_input, 310, 30)

        nim_value_text = "Calculate Nim Value"
        nim_value_width = draw_text(nim_value_text, 30, 150, WHITE)
        pygame.draw.rect(screen, RED, (20, 140, nim_value_width+20, 50))
        draw_text(nim_value_text, 30, 150, WHITE)

        restart_text = "Restart"
        restart_width = draw_text(restart_text, 30 + nim_value_width+30, 150, WHITE)
        pygame.draw.rect(screen, GREEN, (30 + nim_value_width+20, 140, 20+restart_width, 50))
        draw_text(restart_text, 30 + nim_value_width+30, 150, WHITE)

        delete_text = "Delete Mode"
        delete_width = draw_text(delete_text, 30 + nim_value_width+30 + restart_width+30, 150, WHITE)
        pygame.draw.rect(screen, RED if delete_mode else GRAY, (30 + nim_value_width+30+restart_width+20, 140, 20+delete_width, 50))
        draw_text(delete_text, 30 + nim_value_width+30 + restart_width+30, 150, WHITE)

        pygame.draw.rect(screen, BLACK, (20, 200, 760, 380), 3)  # Box for vertices

        if vertices:
            draw_vertices(vertices)
            draw_edges(edges, vertices)

        if result is not None:
            draw_text(f"Nim Value: {result}", 20, 80)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 300 <= event.pos[0] <= 500 and 20 <= event.pos[1] <= 56:
                    input_active = "vertices"
                # Dec 21, 2024 NDXC-- Get Nim value button
                elif 20 <= event.pos[0] <= 20+10+nim_value_width+10 and 140 <= event.pos[1] <= 190:
                    if vertices:
                        graph = np.zeros((len(vertices), len(vertices)), dtype=int)
                        graph = attachEdges(graph, edges)
                        result = getNimValue(graph)
                        with open("graphs.dict", "wb") as file:
                            pickle.dump(graphs, file)
                # Dec 21, 2024 NDXC-- Restart button
                elif 20+10+nim_value_width+10+10 <= event.pos[0] <= 20+10+nim_value_width+10+10+10+restart_width+10  and 140 <= event.pos[1] <= 190:
                    vertices = []
                    edges = []
                    result = None
                # Dec 21, 2024 NDXC-- Delete mode button
                elif 20+10+nim_value_width+10+10+10+restart_width+10+10<= event.pos[0] <= 20+10+nim_value_width+10+10+10+restart_width+10+10+10+delete_width+10 and 140 <= event.pos[1] <= 190:
                    delete_mode = not delete_mode

                # Dec 21, 2024 NDXC-- Check if the click is inside the vertices box
                elif 20 <= event.pos[0] <= 780 and 200 <= event.pos[1] <= 580:
                    vertex = get_vertex_at_pos(event.pos, vertices)
                    if vertex is not None:
                        if delete_mode:
                            vertices.pop(vertex)
                            edges = [(v1, v2) for v1, v2 in edges if v1 != vertex and v2 != vertex]
                            edges = [(v1 - 1, v2 - 1) if v1 > vertex and v2 > vertex else (v1, v2) for v1, v2 in edges]
                        else:
                            if selected_vertex is None:
                                selected_vertex = vertex
                            else:
                                if selected_vertex != vertex:
                                    edges.append((selected_vertex, vertex))
                                selected_vertex = None
                else:
                    edge_index = get_edge_at_pos(event.pos, vertices, edges)
                    if edge_index is not None and delete_mode:
                        edges.pop(edge_index)

            elif event.type == pygame.KEYDOWN:
                if input_active == "vertices":
                    if event.key == pygame.K_BACKSPACE:
                        vertex_input = vertex_input[:-1]
                    else:
                        vertex_input += event.unicode
                    try:
                        size = int(vertex_input)
                        angle = 2 * math.pi / size
                        radius = 80
                        center_x, center_y = width // 2, 390
                        vertices = [(int(center_x + radius * math.cos(i * angle)), int(center_y + radius * math.sin(i * angle))) for i in range(size)]
                        edges = []
                        result = None
                    except ValueError:
                        pass
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':

    main()