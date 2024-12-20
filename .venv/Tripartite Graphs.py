import math
import re
import numpy as np
# import oapackage
import pickle
import networkx as nx

# AHOY!!!!
# Meagan, you can change this to a number instead of having to type it in each time.
# Change it back to "0" without the quotes to have it ask each time.
MANUAL_PARTITE = 0


def getTripartiteEdges(vertexCount, partitionsList):
    sums = []
    for i, partitionValue in enumerate(partitionsList):
        if i == 0:
            sums.append(partitionValue)
        else:
            sums.append(sums[-1] + partitionValue)

    if sums[-1] != vertexCount:
        return f"Unfortunately, your values sum to be {sums[-1]} which is not equal to {vertexCount}. Try again! ○|￣|_"

    partitions = []
    for i in range(len(partitionsList)):
        if i > 0:
            partitions.append(range(sums[i - 1], sums[i]))
        else:
            partitions.append(range(sums[i]))

    # first = list(range(firstCount))
    # second = list(range(firstCount, firstCount + secondCount))
    # third = list(range(firstCount + secondCount, firstCount + secondCount + thirdCount))
    edges = []
    # Connect first verticies to all in the second and third partitions
    for startPartitionNum, startPartition in enumerate(partitions):
        for startVertex in startPartition:
            for endPartitionNum in range(startPartitionNum + 1, len(partitions)):
                for endVertex in partitions[endPartitionNum]:
                    edges.append((startVertex, endVertex))


    return edges


def inverse_permutation(perm):
    inverse = [0] * len(perm)
    for i, p in enumerate(perm):
        inverse[p] = i
    return inverse


def reduce(graph):
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
    for edge in edges:
        first = edge[0]
        second = edge[1]
        graph[first, second] = 1
    return np.maximum(graph, graph.T)  # make array symmetric


def removeVertex(original, vertex):
    return np.delete(np.delete(original, vertex, 0), vertex, 1)


def removeEdge(original, edge: (int, int)):
    newgraph = original.copy()
    newgraph[edge[0], edge[1]] = 0
    newgraph[edge[1], edge[0]] = 0
    return newgraph


def getVertexMoves(original):
    return list(range(len(original)))


def getEdgeMoves(original):
    height, width = original.shape
    edges = []
    for row in range(height):
        for col in range(row, width):
            if original[row, col] == 1:
                edges.append((row, col))
    return edges


def getNimValue(original):
    global graphs
    reduced = reduce(original)
    graphKey = str(reduced)
    nimValue = graphs.get(graphKey, None)

    if nimValue is not None:
        return nimValue

    childGraphs = []

    for vertex in getVertexMoves(reduced):
        childGraphs.append(removeVertex(reduced, vertex))

    for edgeMove in getEdgeMoves(reduced):
        childGraphs.append(removeEdge(reduced, edgeMove))

    childNimValues = set()

    for graph in childGraphs:
        childNimValues.add(getNimValue(graph))

    childNimValues = list(childNimValues)
    childNimValues.sort()

    for i in range(len(childNimValues)):
        if i != childNimValues[i]:
            graphs[graphKey] = i
            return i

    # add the next highest Nim Value in childNimValue
    graphs[graphKey] = len(childNimValues)
    return len(childNimValues)


def main():
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


