import networkx as nx
import numpy as np
from utils import calculate_score, is_valid_solution
import heapq

def dijsktra_path(G):
    node_count = len(G.nodes)
    path = nx.dijkstra_path(G, 0, node_count - 1)
    edge = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    return edge

def score_components(Gg):
    """
    heuristically calculate score of each edge
        Gg: networkx.Graph
    returns:
        s: score for each edge
    """

    #set up
    dj_path = dijsktra_path(Gg)
    weight, conn, score, in_shortest_path = [], [], [], []
    edges = Gg.edges.data()
    num_nodes = len(Gg.nodes)

    for u, v, prop in edges:
        conn.append(Gg.degree[u] + Gg.degree[v] - 2)
        weight.append(prop['weight'])
        if (u,v) in dj_path:
            in_shortest_path.append(0.8) #tune this weight
        else:
            in_shortest_path.append(0)
    
    #normalize score 
    min_weight, max_conn = min(weight), max(conn)
    weight = [min_weight/w for w in weight] #less than 1
    conn  = [c/max_conn for c in conn] #less than 1
    
    #calculate edge score
    e_score = np.array([conn[i] + weight[i] + in_shortest_path[i] for i in range(len(edges))])

    #add attribute e_score to each edge
    nx.set_edge_attributes(Gg, {e: {'score': e_score[i]} for i,e in enumerate(Gg.edges)})

    #calc score of node based on collective sum of e_score 
    n_score = []
    for i, node in enumerate(Gg.nodes):
        prop = Gg.edges(node, data='score')
        score = sum(i[2] for i in prop) / len(prop)
        n_score.append(score)
    
    # rank edges:
    edges = list(Gg.edges)
    argsort = np.argsort(np.array(e_score))
    sorted_edge = [edges[i] for i in argsort]
    sorted_node = np.argsort(np.array(n_score))

    #remove s and t 
    sorted_node = sorted_node[sorted_node != 0]
    sorted_node = sorted_node[sorted_node != num_nodes - 1]


    return sorted_edge, sorted_node
    

def heuristics_plain(G, cnum, knum):
    """
    Args:
        G: networkx.Graph
    Returns:
        c: list of cities to remove
        k: list of edges to remove
    """
    G_cut = G.copy()
    sorted_edge, sorted_node = score_components(G_cut)
    c, k = [], []

    for n in sorted_node:
        copy = G_cut.copy()
        copy.remove_node(n)
        if nx.is_connected(copy):
            cnum -= 1
            c.append(n)
            G_cut = copy
        if cnum == 0:
            break

    for u, v in sorted_edge:
        if u not in c and v not in c:
            G_cut.remove_edge(u, v)
            if nx.is_connected(G_cut):
                knum -= 1 
                k.append((u, v))
            else:
                G_cut.add_edge(u, v)
        if knum == 0:
            break
    
    return c, k


def heuristics_greedy(G, cnum, knum):
    
    G_cut = G.copy()
    sorted_edge, sorted_node = score_components(G_cut)
    sorted_node = list(sorted_node)
    c, k = [], []
    
    while len(c) < cnum:
        sorted_node = list(filter(lambda x: is_valid_solution(G, c + [x], k), sorted_node))
        score_node = max(sorted_node, key=lambda x: calculate_score(G, c + [x], k))
        sorted_node.remove(score_node)
        c.append(score_node)
        
        if len(sorted_node) == 0:
            break
    
    sorted_edge =list(filter(lambda e: e[0] not in c and e[1] not in c, sorted_edge))
    print(c)
    
    while len(k) < knum:
        
        sorted_edge = list(filter(lambda x: is_valid_solution(G, c, k + [x]), sorted_edge))
        if len(sorted_edge) == 0:
            break
        score_edge = max(sorted_edge, key=lambda x: calculate_score(G, c, k + [x]))
        k.append(score_edge)
        print(len(k))
        sorted_edge.remove(score_edge)
    
    return c, k

def look_advace_small(G, cnum, knum, beamSize):
    
    
    G_cut = G.copy()
    sorted_edge, sorted_node = score_components(G_cut)
    sorted_node = sorted_node[:30]
    c, k = [], []
    
    while len(c) < cnum:
        score_node = max(sorted_node, key=lambda x: calculate_score(G, c + [x], k))
        c.append(score_node)
    
    sorted_edge =list(filter(lambda e: e[0] not in c and e[1] not in c, sorted_edge))
    sorted_edge = list(filter(lambda x: is_valid_solution(G, c, k + [x]), sorted_edge))
    nlargest = heapq.nlargest(beamSize, sorted_edge, key=lambda x: calculate_score(G, c, k + [x]))
    
    beams = [[[x for x in sorted_edge if x != i], [i], calculate_score(G, c, [i])] for i in nlargest] # [list_of_edges, k, score]
    
    k_tracker = 0
    while k_tracker < knum - 1:
        new_beams = []
        # curate new beams 
        for b in beams:
            b[0] = list(filter(lambda x: is_valid_solution(G, c, b[1] + [x]), b[0]))
            if len(b[0]) == 0:
                new_beams.append(b)
            else:
                nlargest = heapq.nlargest(beamSize, b[0], key=lambda x: calculate_score(G, c, b[1] + [x]))
                for i in nlargest:
                    new_beams.append([[x for x in b[0] if x != i], b[1] + [i], calculate_score(G, c, b[1] + [i])])
            beams = heapq.nlargest(beamSize, new_beams, key=lambda x: x[2])
                        
        k_tracker += 1
    
    best = max(beams, key=lambda x:x[2])
    print(best[1])
    print(len(best[1]))
    print(best[2])
    

    return c, best[1]
    
    
# look_advace_small(Gg, 1, 25, 3)

# def remove_edge(G, edge):

# def remove_node(G, node):
#     """
#     Remove node from G if possible. 

#     Args:
#         G ([type]): [description]
#         node ([type]): [description]
#     """


            
    



    
