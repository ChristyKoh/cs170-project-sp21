import networkx as nx
import numpy as np
from utils import calculate_score, is_valid_solution
import heapq
from itertools import permutations 

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
    # print(c)
    
    while len(k) < knum:
        
        sorted_edge = list(filter(lambda x: is_valid_solution(G, c, k + [x]), sorted_edge))
        if len(sorted_edge) == 0:
            break
        score_edge = max(sorted_edge, key=lambda x: calculate_score(G, c, k + [x]))
        k.append(score_edge)
        # print(len(k))
        sorted_edge.remove(score_edge)
    
    return c, k

def look_advace_small(G, cnum, knum, beamSize):
    
    
    G_cut = G.copy()
    sorted_edge, sorted_node = score_components(G_cut)
    sorted_node = sorted_node[:30]
    score_node = []
    c, k = [], []
    
    #for medium / large select more c 
    sorted_node = list(filter(lambda x: is_valid_solution(G, c + [x], k), sorted_node))
    score_node = heapq.nlargest(beamSize, sorted_node, key=lambda x: calculate_score(G, c + [x], k))
    
    beams = []# [list_of_edges, k, score, c]

    # Set up Basic edge
    if len(score_node) == 0:
        sorted_edge_ = list(filter(lambda x: is_valid_solution(G, [c], k + [x]), sorted_edge))
        nlargest = heapq.nlargest(beamSize ** 2, sorted_edge_, key=lambda x: calculate_score(G, [], k + [x]))
        beams.extend([[[x for x in sorted_edge_ if x != i], [i], calculate_score(G, [], [i]), []] for i in nlargest])
    
    else:
        for c in score_node:
            sorted_edge_ =list(filter(lambda e: e[0] != c and e[1] != c, sorted_edge))
            sorted_edge_ = list(filter(lambda x: is_valid_solution(G, [c], k + [x]), sorted_edge_))
            nlargest = heapq.nlargest(beamSize, sorted_edge_, key=lambda x: calculate_score(G, [c], k + [x]))
            beams.extend([[[x for x in sorted_edge_ if x != i], [i], calculate_score(G, [c], [i]), [c]] for i in nlargest])

    k_tracker = 0
    while k_tracker < knum - 1:
        new_beams = []
        # curate new beams 
        for b in beams:
            b[0] = list(filter(lambda x: is_valid_solution(G, b[3], b[1] + [x]), b[0]))
            if len(b[0]) == 0:
                new_beams.append(b)
            else:
                nlargest = heapq.nlargest(beamSize * 2, b[0], key=lambda x: calculate_score(G, b[3], b[1] + [x]))
                for i in nlargest:
                    new_beams.append([[x for x in b[0] if x != i], b[1] + [i], calculate_score(G, b[3], b[1] + [i]), b[3]])
        beams = heapq.nlargest(beamSize * 2, new_beams, key=lambda x: x[2])
                        
        k_tracker += 1

    if len(beams) == 0:
        return [], []

    best = max(beams, key=lambda x:x[2])

    
    return best[3], best[1]


def dj_beam_search(G, cnum, knum, beamSize):
    c, k = [], []
    edges = list(G.edges)
    node_count = len(G.nodes) 
    nodes = list(G.nodes)
    nodes.remove(0)
    nodes.remove(node_count - 1)
    
    
    G_copy = G.copy()
    beams = [[[], []]]  #[nodes to be removed, edges to be removed, score]
    k_count = 0
    # print('aye')

    # Phase 1: Populate Edges
    while k_count < knum - 1:
        # print(k_count)
        new_beams = []
        for b in beams:
            shortest = dijsktra_path_(G.copy(), b[0], b[1], 0, node_count - 1)
            shortest = list(filter(lambda x: is_valid_solution(G_copy, b[0], b[1] + [x]), shortest))
            best_edges = heapq.nlargest(beamSize, shortest, key=lambda x: calculate_score(G_copy, b[0], b[1] + [x]))
            for i in best_edges:
                new_beams.append([b[0], b[1] + [i], calculate_score(G_copy, b[0], b[1] + [i])])
            if len(best_edges) == 0:
                new_beams.append(b)
            
        beams = heapq.nlargest(beamSize, new_beams, key=lambda x: x[2]) #beamsize * 2?
        
        k_count += 1 
    
    # Phase 2: Populate Nodes
    new_beams = []
    for b in beams:
        overlap = {}
        
        edges = b[1]
        for i in edges:
            if i[0] not in overlap:
                overlap[i[0]] = 1
            else:
                overlap[i[0]] += 1

            if i[1] not in overlap:
                overlap[i[1]] = 1
            else:
                overlap[i[1]] += 1

        overlap.pop(0,None)
        overlap.pop(node_count - 1,None)
        
                
        sorted_node = heapq.nlargest(beamSize, overlap.keys(), key=lambda x: overlap[x])
        # print(sorted_node)
    
        node_perm = list(permutations(sorted_node, cnum))
        node_perm = list(filter(lambda x: is_valid_solution(G_copy, x, b[1]), node_perm)) #is solution valid
        sorted_node_perm = heapq.nlargest(beamSize, node_perm, key=lambda x: calculate_score(G_copy, x, edges)) #sort node perm

        for c in sorted_node_perm:
            new_beams.append([c, edges, calculate_score(G_copy, c, edges)])
        if len(sorted_node_perm) == 0:
            new_beams.append([[], edges, calculate_score(G_copy, [], edges)])
    
    beams = heapq.nlargest(beamSize * 2, new_beams, key=lambda x: x[2])
    # print('stage c')
    # print(beams)
    
    #remove edges that overlap with node
    for b in beams:
        b[1] =list(filter(lambda e: e[0] not in b[0] and e[1] not in b[0], b[1]))
#         print(is_valid_solution(G_copy, b[0], b[1]))
        # print(b[0], b[1])
        
    
    #add edge till limit is reached
    
    done = []
    # print(beams)
    
    while len(done) < beamSize:
        new_beams = []
        for b in beams:
            if len(b[1]) == knum:
                done.append(b)
            else:
                shortest = dijsktra_path_(G.copy(), b[0], b[1], 0, node_count - 1)
                shortest = list(filter(lambda x: is_valid_solution(G_copy, b[0], b[1] + [x]), shortest))
                shortest =list(filter(lambda e: e[0] not in b[0] and e[1] not in b[0], shortest))
                best_edges = heapq.nlargest(beamSize, shortest, key=lambda x: calculate_score(G_copy, b[0], b[1] + [x]))
                for i in best_edges:
                    new_beams.append([b[0], b[1] + [i], calculate_score(G_copy, b[0], b[1] + [i])])
                if len(best_edges) == 0:
                    new_beams.append(b)
        if beams == new_beams:
            done.extend(new_beams)
        beams = heapq.nlargest(beamSize * 2, new_beams, key=lambda x: x[2]) #beamsize * 2?
    
    
    best = max(done, key=lambda x:x[2])
    
    return best[0], best[1]

    
def dijsktra_path_(G, c , k, s, t):
    G.remove_edges_from(k)
    G.remove_nodes_from(c)
    path = nx.dijkstra_path(G, s, t)
    edge = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    return edge
            
    



    
