import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_score
import sys
from os.path import basename, normpath
import glob
import heapq
from collections import Counter
import numpy as np


def solve(G):
    """
    Args:
        G: networkx.Graph
    Returns:
        c: list of cities to remove
        k: list of edges to remove
    """
    size = G.number_of_nodes()
    if size <= 30:
        return naive(G, 1, 15)
    elif size <= 50:
        return naive(G, 3, 50)
    else:
        return naive(G, 5, 100)

def naive(G, cnum, knum):
    """
    repeatedly find k-greedy min path.
    Args:
        G: networkx.Graph
        cnum: number of cities to rm
        knum: number of edges to rm
    returns:
        c: list of cities to remove
        k: list of edges to remove
    """
    c, k = [], []
    G_cut = G.copy()
    
    # start and end
    s, t = 0, G_cut.number_of_nodes() - 1

    nodes = [] # captures freq of nodes in shortest paths
    forbidden_edges = set() # cannot cuts
    stop_cutting = False

    while not stop_cutting and knum > 0: # make knum cuts
        path = nx.dijkstra_path(G_cut, s, t, weight="weight")

        u = 0
        edges = []
        for v in path[1:]:
            edges.append([u,v])
            if v != t:
                nodes.append(v)
            u = v

        # take min edge
        edges.sort(key=lambda e: G_cut[e[0]][e[1]]["weight"])
        # print(f"sorted edges: {edges}")

        for e in edges:
            # if all edges forbidden
            if len(forbidden_edges) == G_cut.number_of_edges():
                stop_cutting = True
                break
            
            # remove edge
            G_cut.remove_edge(e[0], e[1])
            if nx.is_connected(G_cut): 
                k.append(e)
                # print(f"{knum}: cutting edge {e}")
                knum -= 1
                break
            # if disconnects graph, add edge back
            G_cut.add_edge(e[0], e[1])
            forbidden_edges.append(e)

    counts = Counter(nodes)
    top_c = counts.most_common(cnum) # sort
    c = [v[0] for v in top_c]
    # print(f"counts: {counts}")

    G_cut.remove_nodes_from(c)

    # TODO iterate, add count from most common node to knum, rm edges from edges
    # TODO catch case where no more cuts can be made

    print(f"rm nodes: {c}")
    print(f"rm edges: {k}")
    return c, k




# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

# if __name__ == '__main__':
#     assert len(sys.argv) == 2
#     path = sys.argv[1]
#     G = read_input_file(path)
#     c, k = solve(G)
#     assert is_valid_solution(G, c, k)
#     print("Shortest Path Difference: {}".format(calculate_score(G, c, k)))
#     write_output_file(G, c, k, 'outputs/test.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
if __name__ == '__main__':
    inputs = glob.glob('inputs/*')
    for input_path in inputs:
        output_path = 'outputs/' + basename(normpath(input_path))[:-3] + '.out'
        G = read_input_file(input_path)
        c, k = solve(G)
        assert is_valid_solution(G, c, k)
        distance = calculate_score(G, c, k)
        write_output_file(G, c, k, output_path)
