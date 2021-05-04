import networkx as nx
import glob

def is_valid_solution(G, c, k):
    """
    Checks whether D is a valid mapping of G, by checking every room adheres to the stress budget.
    Args:
        G: networkx.Graph
        c: List of cities to remove
        k: List of edges to remove (List of tuples)
    Returns:
        bool: false if removing k and c disconnects the graph
    """
    size = len(G)
    H = G.copy()

    for road in k:
        assert H.has_edge(road[0], road[1]), "Invalid Solution: {} is not a valid edge in graph G".format(road)
    H.remove_edges_from(k)
    
    for city in c:
        assert H.has_node(city), "Invalid Solution: {} is not a valid node in graph G".format(city)
    H.remove_nodes_from(c)
    
    assert H.has_node(0), 'Invalid Solution: Source vertex is removed'
    assert H.has_node(size - 1), 'Invalid Solution: Target vertex is removed'

    return nx.is_connected(H)

def calculate_score(G, c, k):
    """
    Calculates the difference between the original shortest path and the new shortest path.
    Args:
        G: networkx.Graph
        c: list of cities to remove
        k: list of edges to remove
    Returns:
        float: total score
    """
    H = G.copy()
    assert is_valid_solution(H, c, k)
    node_count = len(H.nodes)
    original_min_dist = nx.dijkstra_path_length(H, 0, node_count-1)
    H.remove_edges_from(k)
    H.remove_nodes_from(c)
    final_min_dist = nx.dijkstra_path_length(H, 0, node_count-1)
    difference = final_min_dist - original_min_dist
    return difference

def diff_two_files(curr, prev, target):
    """
    Calculates the improvement between two most recent score files, 
    writes to diff file.
    Args:
        curr: path to most recent file
        prev: "             previous file
        target: "       diff file to write result to
    Returns:
        float: net gain
        float: net loss
    """
    

def diff_score_files(size):
    """
    Calculates the improvement between two most recent score files, 
    writes to diff file.
    Args:
        size: string (s/m/l)
    Returns:
        float: net gain
        float: net loss
    """
    # TODO implement
    inputs = sorted(glob.glob(f'outputs/{size}*'), reverse=True)[:2]
    print(inputs)
    # take the last 2 files

    last_file = open(inputs[0], 'r')
    prev_file = open(inputs[1], 'r')
    diff_file = open(f"outputs/diff_{size}.txt", 'w')

    gain, loss = 0, 0

    while last_file.readable() and prev_file.readable():
        lline, pline = last_file.readline().split(" "), prev_file.readline().split(" ")

        if len(lline) != 2 or len(pline) != 2:
            continue

        assert lline[0] == pline[0]

        # extract scores
        last_score = float(lline[1])
        prev_score = float(pline[1])
        diff = last_score - prev_score

        if diff >= 0:
            gain += diff
        else:
            loss += diff

        diff_file.write(f"{lline[0]} {diff}\n")

    last_file.close()
    prev_file.close()
    diff_file.close()

    print(f"total gain: {gain}, total loss: {loss}")
    print(f"net gain: {gain + loss}")
    return gain, loss