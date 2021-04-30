import networkx as nx
import numpy as np

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

    #remove s and t 
    sorted_node = sorted_node[sorted_node != 0]
    sorted_node = sorted_node[sorted_node != num_nodes - 1]


    return sorted_edge, sorted_node
    

def heuristics_greedy(G, cnum, knum):
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


# def remove_edge(G, edge):

# def remove_node(G, node):
#     """
#     Remove node from G if possible. 

#     Args:
#         G ([type]): [description]
#         node ([type]): [description]
#     """


            
    



    
