import networkx as nx
from collections import Counter
import numpy as np

def edge_score(e):
    """
    return score of an edge given edge
    Args:
        e: tuple (u, v, weight)
    returns:
        float: some heuristic score
    """

    # 0: trivial return weight
    return e[2]

    # 1: 
    # return 

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
    node_scores = [0 for _ in range(G_cut.number_of_nodes())] # score for nodes to cut
    edge_scores = [0 for _ in range(G_cut.number_of_nodes())] # score for nodes to cut
    forbidden_edges = set() # cannot cuts
    forbidden_nodes = set() # cannot rm
    stop_cutting = False

    while not stop_cutting and knum > 0 and cnum > 0: # make knum cuts, on 0 remove node
        path = nx.dijkstra_path(G_cut, s, t, weight="weight")

        u = 0
        edges = []
        # add edges to list
        for v in path[1:]:
            edges.append((u, v, G_cut[u][v]["weight"]))
            if v != t:
                nodes.append(v)
            u = v

        # take min edge
        edges.sort(key=edge_score) ## CAN CHANGE SCORING METHOD HERE
        # print(f"sorted edges: {edges}")

        all_edges_checked = True
        for e in edges:
            # if all edges forbidden
            # print(len(forbidden_edges))
            # print(G_cut.number_of_edges())
            if len(forbidden_edges) >= G_cut.number_of_edges():
                # print("all edges forbidden")
                stop_cutting = True
                break
            
            # remove edge
            G_cut.remove_edge(e[0], e[1])
            if nx.is_connected(G_cut):
                k.append(e)
                # print(f"{knum}: cutting edge {e}")
                knum -= 1
                all_edges_checked = False
                break
            # if disconnects graph, add edge back
            G_cut.add_edge(e[0], e[1], weight=e[2])
            forbidden_edges.add(e)
            # print(f"      adding back edge {e}")

        if all_edges_checked == True: 
            # this shortest path, cannot be altered
            break

        if knum == 0:
            if cnum == 0:   # finished removing all cnum nodes
                break

            # otherwise, remove a single node
            counts = Counter(nodes)
            top_c = counts.most_common(1)[0][0]
            # print(counts.most_common(5))

            adj_edges = G_cut.edges([top_c], data="weight")
            if (len(adj_edges) > 0):
                G_cut.remove_node(top_c)
            
            if nx.is_connected(G_cut):
                # node can be removed successfully
                # print(f"{knum}: cutting node {top_c}")
                c.append(top_c)
                cnum -= 1

                nodes = [n for n in nodes if n != top_c]

                # add back k shortest paths removed
                num_edges_before = len(k)
                k = [e for e in k if e[0] != top_c and e[1] != top_c]
                knum += num_edges_before - len(k)
                # print(knum)

                continue

            # if disconnects graph, add node back
            G_cut.add_node(top_c)
            G_cut.add_edges_from(adj_edges)
            forbidden_nodes.add(top_c)
    
    # print(f"counts: {counts}")

    G_cut.remove_nodes_from(c)

    # print(f"rm nodes: {c}")
    # print(f"rm edges: {k}")
    return c, k