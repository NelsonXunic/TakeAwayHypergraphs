import math
import re
import numpy as np
# Dec 19, 2024 NDXC-- This is a package that is not installed by default. You can install it with pip install oapackage.
# It does not work, so I commented it out. Instead, I used networkx.

# import oapackage
import pickle
import networkx as nx

# Dec 19, 2024 NDXC-- This variable allows the user to input the number of partitions they want to split the graph into.
# You can change this to a number instead of having to type it in each time.
# Change it back to "0" without the quotes to have it ask each time.
MANUAL_PARTITE = 0

def getTripartiteEdges(vertexCount, partitionsList):
    """
    Dec 19, 2024 NDXC-- This function generates the edges for a tripartite graph given the number of vertices and the number of partitions.
    :param vertexCount: An integer representing the number of vertices in the graph
    :param partitionsList: A list of integers representing the number of vertices in each partition. Each integer in the list represents a partition so the length of the list is the number of partitions.
    :return: A list of tuples representing the edges in the graph
    """
    # Dec 19, 2024 NDXC-- This is a list of the sum of the vertices in each partition. This is used to determine the range of vertices in each partition.
    sums = []
    # Dec 19, 2024 NDXC-- This loop calculates the sum of the vertices in each partition by iterating through the partitionsList. The first partition is just the first value in the list. The rest are the sum of the previous partition and the current partition.
    for i, partitionValue in enumerate(partitionsList):
        if i == 0:
            sums.append(partitionValue)
        else:
            sums.append(sums[-1] + partitionValue)

    # Dec 19, 2024 NDXC-- This checks if the sum of the partitions is equal to the number of vertices. If it is not, it returns an error message.
    if sums[-1] != vertexCount:
        return f"Unfortunately, your values sum to be {sums[-1]} which is not equal to {vertexCount}. Try again! ○|￣|_"

    # Dec 19, 2024 NDXC-- This creates a list of ranges for each partition. The first partition is just the range of
    # the first partition value. The rest are the range of the sum of the previous partition and the current partition.
    partitions = []
    for i in range(len(partitionsList)):
        if i > 0:
            partitions.append(range(sums[i - 1], sums[i]))
        else:
            partitions.append(range(sums[i]))

    # first = list(range(firstCount))
    # second = list(range(firstCount, firstCount + secondCount))
    # third = list(range(firstCount + secondCount, firstCount + secondCount + thirdCount))

    # Dec 19, 2024 NDXC-- This is a list of edges that will be returned. It is empty at the start.
    edges = []
    # Connect first verticies to all in the second and third partitions

    # Dec 19, 2024 NDXC-- This loop connects all the vertices in the first partition to all the vertices in the second
    # and third partitions. The first loop is for the first partition. The second loop is for the second partition.
    # The third loop is for the third partition. The fourth loop is for the vertices in the second and third partitions.
    for startPartitionNum, startPartition in enumerate(partitions):
        for startVertex in startPartition:
            for endPartitionNum in range(startPartitionNum + 1, len(partitions)):
                for endVertex in partitions[endPartitionNum]:
                    edges.append((startVertex, endVertex))


    return edges

def inverse_permutation(perm):
    """
    Dec 19, 2024 NDXC-- This function returns the inverse of a permutation. The inverse of a permutation is a permutation that undoes the effect of the original permutation.
    :param perm: The permutation to find the inverse of as a list of integers representing the permutation
    :return: The inverse of the permutation as a list of integers
    """
    inverse = [0] * len(perm)
    for i, p in enumerate(perm):
        inverse[p] = i
    return inverse

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
        childGraphs.append(removeVertex(reduced, vertex))

    # Dec 19, 2024 NDXC-- This loop gets the child graphs of the graph obtained by removing an edge from the graph.
    # The child graphs are stored in the childGraphs list.
    for edgeMove in getEdgeMoves(reduced):
        childGraphs.append(removeEdge(reduced, edgeMove))

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
    while True:
        size = int(input("How many vertices does the graph have: "))
        if size < 0:
            quit()
        edges = input("What are the edges? (e.x. 1,2;3,4;5,6; or 'complete'): ")
        manualEntry = True
        inputError = None
        if edges.lower()[0] == "c":
            print("Ahhh, I see you're looking for a complete graph (ง •_•)ง")
            manualEntry = False
            numpartitions = MANUAL_PARTITE
            while numpartitions < 1 or numpartitions > size:
                numpartitions = int(input(f"How many partitions would you like to split your {size} vertices into: "))
            partitions = [0 for i in range(numpartitions)]
            extraNodes = size - numpartitions
            print(f"Currently generating a graph with {numpartitions} partitions...")
            for i in range(numpartitions):
                if i+1 % 10 == 1:
                    postfix = "st"
                elif i+1 % 10 == 2:
                    postfix = "nd"
                elif i+1 % 10 == 3:
                    postfix = "rd"
                else:
                    postfix = "th"
                response = -1
                while response < 1 or response - 1 > extraNodes:
                    response = int(input(f"How many verticies in the {i+1}{postfix} position: "))
                extraNodes -= response - 1
                partitions[i] = response
            ordered_edges = getTripartiteEdges(size, partitions)
            if isinstance(ordered_edges, str):
                inputError = ordered_edges


        if manualEntry:
            edgeExpression = r"[0-9]+"
            ordered_edges = []
            integers = re.findall(edgeExpression, edges)


            if len(integers) % 2 == 1:
                inputError = f"User entered {len(integers)} ends that the edges connect to. This cannot be odd."
            for edge_Number in range(len(integers)//2):
                first_num = int(integers[2 * edge_Number])
                second_num = int(integers[2 * edge_Number + 1])
                ordered_edges.append((first_num, second_num))
                if first_num >= size:
                    inputError = f"User error, {first_num} is not in the acceptable range of labels from 0 to {size - 1}. Try again!"
                if second_num >= size:
                    inputError = f"User error, {second_num} is not in the acceptable range of labels from 0 to {size - 1}. Try again!"

        if inputError is None:
            break
        print(inputError)

    graph = np.zeros((size, size), dtype=int)
    graph = attachEdges(graph, ordered_edges)

    refreshFile = False
    if refreshFile:
        graphs = {}
    else:
        with open("graphs.dict", "rb") as file:
            graphs = pickle.load(file)

    print(f"The nim value of \n{graph} \nis {getNimValue(graph)}")

    with open("graphs.dict", "wb") as file:
        pickle.dump(graphs, file)


if __name__ == '__main__':
    graphs = None
    print("Welcome to Meagan's tripartite graphs. I can find the nim values for any graph you can label!")
    print("Now, how can I help?")
    while True:
        try:
            main()
        except ValueError:
            print("You probably entered a letter where you wanted a number or you didn't type in the edges right. Try again!")


