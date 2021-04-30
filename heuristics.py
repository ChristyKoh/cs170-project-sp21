import networkx as nx
import numpy as np

def dijsktra_path(G):
    node_count = len(G.nodes)
    path = nx.dijkstra_path(G, 0, node_count - 1)
    print(path)
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

    for u, v, prop in edges:
        conn.append(Gg.degree[u] + Gg.degree[v] - 2)
        weight.append(prop['weight'])
        if (u,v) in dj_path:
            in_shortest_path.append(0.5) #tune this weight
        else:
            in_shortest_path.append(0)
    
    #normalize score 
    max_weight, max_conn = max(weight), max(conn)
    weight = [w/max_weight for w in weight] #less than 1
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
    np.delete(sorted_node, [0, len(Gg.nodes) - 1])

    return sorted_edge, sorted_node
    

def heuristics_greedy(G, cnum, knum):
    """
    Args:
        G: networkx.Graph
    Returns:
        c: list of cities to remove
        k: list of edges to remove
    """
    sorted_edge, sorted_node = heuristics(G)
    
    


    
