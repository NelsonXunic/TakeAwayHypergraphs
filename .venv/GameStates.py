import os
import pickle

game_states = {}
nim_values = {}

def get_possible_moves(vertices, edges, hyperedges):
    possible_moves = []
    for i, vertex in enumerate(vertices):
        new_vertices = vertices[:i] + vertices[i+1:]
        new_edges = [edge for edge in edges if i not in edge]
        new_hyperedges = [hyperedge for hyperedge in hyperedges if i not in hyperedge]
        possible_moves.append((new_vertices, new_edges, new_hyperedges))
    for edge in edges:
        new_edges = edges[:]
        new_edges.remove(edge)
        new_hyperedges = [hyperedge for hyperedge in hyperedges if not (edge[0] in hyperedge and edge[1] in hyperedge)]
        possible_moves.append((vertices, new_edges, new_hyperedges))
    for hyperedge in hyperedges:
        new_hyperedges = hyperedges[:]
        new_hyperedges.remove(hyperedge)
        possible_moves.append((vertices, edges, new_hyperedges))
    return possible_moves

def calculate_nim_value(vertices, edges, hyperedges):
    """
    Calculate the Nim value (Grundy number) for a given game state.

    Args:
        vertices (list): List of vertex coordinates.
        edges (list): List of edges (pairs of vertex indices).
        hyperedges (list): List of hyperedges (sets of vertex indices).

    Returns:
        int: The Nim value of the game state.
    """
    ######## Use the function from Tripartite Graphs.py if there are no hyperedges
    if not hyperedges:
        return calculate_nim_value_without_hyperedges(vertices, edges)

    state = (tuple(vertices), tuple(map(tuple, edges)), tuple(map(tuple, hyperedges)))
    if state in nim_values:
        return nim_values[state]

    next_states = get_possible_moves(vertices, edges, hyperedges)
    next_nim_values = [calculate_nim_value(*next_state) for next_state in next_states]
    nim_value = mex(next_nim_values)
    nim_values[state] = nim_value
    return nim_value

##### DEC 19    ####################
def calculate_nim_value_without_hyperedges(vertices, edges):
    """
    Calculate the Nim value (Grundy number) for a game state without hyperedges.

    Args:
        vertices (list): List of vertex coordinates.
        edges (list): List of edges (pairs of vertex indices).

    Returns:
        int: The Nim value of the game state.
    """
    state = (tuple(vertices), tuple(map(tuple, edges)))
    if state in nim_values:
        return nim_values[state]

    next_states = get_possible_moves_without_hyperedges(vertices, edges)
    next_nim_values = [calculate_nim_value_without_hyperedges(*next_state) for next_state in next_states]
    nim_value = mex(next_nim_values)
    nim_values[state] = nim_value
    return nim_value

##### DEC 19
def get_possible_moves_without_hyperedges(vertices, edges):
    """
    Generate all possible next states by removing one vertex or one edge at a time.

    Args:
        vertices (list): List of vertex coordinates.
        edges (list): List of edges (pairs of vertex indices).

    Returns:
        list: List of possible next states.
    """
    possible_moves = []
    for i, vertex in enumerate(vertices):
        new_vertices = vertices[:i] + vertices[i+1:]
        new_edges = [edge for edge in edges if i not in edge]
        possible_moves.append((new_vertices, new_edges))
    for edge in edges:
        new_edges = edges[:]
        new_edges.remove(edge)
        possible_moves.append((vertices, new_edges))
    return possible_moves
########################################

def mex(values):
    """
    Calculate the minimum excluded (mex) of a set of values.

    Args:
        values (list): A list of non-negative integers.

    Returns:
        int: The smallest non-negative integer not in the list.
    """
    values_set = set(values)
    mex_value = 0
    while mex_value in values_set:
        mex_value += 1
    return mex_value

def save_game_state(vertices, edges, hyperedges):
    state = (tuple(vertices), tuple(map(tuple, edges)), tuple(map(tuple, hyperedges)))
    if state not in game_states:
        # nim_value = calculate_nim_value(vertices, edges, hyperedges)
        # game_states[state] = {
        #     'possible_moves': get_possible_moves(vertices, edges, hyperedges),
        #     'nim_value': nim_value
        # }
        game_states[state] = {
            'possible_moves': get_possible_moves(vertices, edges, hyperedges)
        }

def save_current_game_state(vertices, edges, hyperedges, player1, player2, current_player):
    game_over = not vertices and not edges and not hyperedges
    state = {
        'vertices': vertices,
        'edges': edges,
        'hyperedges': hyperedges,
        'player1': player1,
        'player2': player2,
        'current_player': current_player,
        'game_over': game_over
    }
    with open('current_game_state.pkl', 'wb') as f:
        pickle.dump(state, f)

def save_game_states_to_file(filename):
    with open(filename, 'wb') as f:
        # pickle.dump((game_states, nim_values), f)
        pickle.dump(game_states, f)

def load_game_states_from_file(filename):
    # global , nim_values
    global game_states
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            game_states = pickle.load(f)
            # data = pickle.load(f)
            # if isinstance(data, tuple) and len(data) == 2:
            #     game_states, nim_values = pickle.load(f)
            #     game_states = pickle.load(f)
            #
            # else:
            #     raise ValueError("Unexpected data format in the pickle file.")
    else:
        game_states = {}
      # nim_values = {}

def load_current_game_state():
    if os.path.exists('current_game_state.pkl'):
        with open('current_game_state.pkl', 'rb') as f:
            state = pickle.load(f)
            if not state['vertices'] and not state['edges'] and not state['hyperedges']:
                return None
            if state['game_over']:
                return None
            return state
    return None