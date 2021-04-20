from parse import write_input_file, validate_file
from utils import calculate_score
import random
import networkx as nx
import time
import numpy

def gen_sm():
    # 20 <= |V| <= 30, k = 15, c = 1  
    return

def gen_md():
    # 31 <= |V| <= 50, k = 50, c = 3
    return

def gen_lg():
    # 51 <= |V| <= 100, k = 100, c = 5
    # TODO: add colors for visualization

    start_time = time.time()

    # 70 midsection nodes: fully connected nodes
    #       - mid-s: 35 connected to s (1-35)
    #       - mid-t: 35 connected to t (36-70)
    G = nx.complete_graph(range(1,71))
    nx.set_edge_attributes(G, values = 1, name = 'weight')

    # 2 endpoint nodes s and t
    G.add_nodes_from([0,99])
    G.add_edge(0, 99, weight=0.3)

    # 8 target nodes: heavy path of weight ~800
    nx.add_path(G, [0] + list(range(91, 100)), weight=99.999)

    # 20 jump/support nodes: 
    #       - jump-s: 5 jump nodes for s (71-75)
    #       - jump-t: 5 jump nodes for t (81-85)
    #       - 10 support nodes, 5 each endpt
    #           - support_s (76-80) support_t (86-90)
    G.add_nodes_from(range(71,76))
    G.add_nodes_from(range(81,86))


    # fully connect support nodes
    support_t = nx.complete_graph(range(76, 81))
    nx.set_edge_attributes(support_t, values = 1, name = 'weight')
    support_s = nx.complete_graph(range(86, 91))
    nx.set_edge_attributes(support_s, values = 1, name = 'weight')

    # union support with G
    nx.union(G, support_s)
    nx.union(G, support_t)
    # connect support to s and t
    for j in range(76, 81):
        G.add_edge(0,j, weight=.5)
    for j in range(86, 91):
        G.add_edge(99,j, weight=.5)
        G.add_edge(0,j, weight=.5)

    # connect jump nodes to support and endpts
    for i in range(71, 76):  # jump-s
        # connect to s and t
        G.add_edge(i, 0, weight=1)
        G.add_edge(i, 99, weight=1)
        # connect to support-s
        for j in range(76, 81):
            G.add_edge(i,j, weight=1)
    for i in range(81, 86):  # jump-t
        # connect to t
        G.add_edge(i, 99, weight=1)
        G.add_edge(i, 0, weight=1)
        # connect to support-t
        for j in range(86, 91):
            G.add_edge(i,j, weight=1)

    # connect mid nodes
    # mid-s to s weighted heavier so naive algorithms are tempted to cut jump node paths first
    for i in range(1, 36): # mid-s
        # conn mid-s to jump-t nodes
        for j in range(81,86):
            G.add_edge(j, i, weight=1)
        # conn mid-s to s/t
        G.add_edge(0, i, weight=(4 + round(random.random(),3)))
        G.add_edge(99, i, weight=(4 + round(random.random(),3)))
    for i in range(36, 71): # mid-t
        # conn mid-t to jump-s nodes
        for j in range(71, 76):
            G.add_edge(j, i, weight=1)
        # conn mid-t to s/t
        G.add_edge(i, 99, weight=(4 + round(random.random(),3)))
        G.add_edge(i, 0, weight=(4 + round(random.random(),3)))
    
    end_time = time.time()
    print("constructed graph: took " + str(end_time - start_time) + " sec")
    start_time = end_time

    write_input_file(G, "inputs/100.in")

    end_time = time.time()
    print("wrote input file: took " + str(end_time - start_time) + " sec")
    return G

def check_lg():
    # test graph construction
    start_time = time.time()
    G = gen_lg()

    end_time = time.time()
    print("generated graph: took " + str(end_time - start_time) + " sec")
    start_time = end_time

    assert G.number_of_nodes() == 100

    # correct degrees
    check_degrees = [0 for i in range(100)]
    # s/t = 35 m + 5 s + 5 j + 1 t
    check_degrees[0] = 46
    check_degrees[99] = 46
    # mid-s and mid-t
        #  = 1 e + 69 m + 5 j = 75
    check_degrees[1:71] = [75 for i in range(70)]
    # jump
        #  = 1 + 5 + 35
    check_degrees[71:76] = [41 for i in range(5)]
    check_degrees[81:86] = [41 for i in range(5)]
    # support
        #  = 1 + 4 + 1 = 6
    check_degrees[76:81] = [6 for i in range(5)]
    check_degrees[86:91] = [6 for i in range(5)]
    # 8 target nodes (91-98):
    check_degrees[91:99] = [2 for i in range(8)]

    # get actual degrees
    degrees = [val for (node, val) in sorted(G.degree(), key=lambda pair: pair[0])]
    assert all([val >= 2 for val in degrees])
    result = numpy.subtract(degrees, check_degrees)
    # print(result)
    assert sum(result == 0)
    
    # SOLVE G
    c = list(range(71,76))                  # rm jump-s
    k = [(0, i) for i in range(1,71)] + [(0, i) for i in range(81,91)] + [(0,99)]  # jump-t to t
        # + [(0,99)]
    assert len(c) <= 5
    assert len(k) <= 100
    print("FINAL SCORE: " + str(calculate_score(G, c, k)))
    # find path -- should only have one path.
    # assert nx.shortest_path_length(G, source=0, target=99, weight='weight') == 99.999*3

    assert validate_file("inputs/100.in")

    end_time = time.time()
    print("checked graph: took " + str(end_time - start_time) + " sec")

# def solve_lg(G):
#     # cut either 35 s or t edges
#     G.remove_edges_from([(0, i) for i in range(1,36)])
#     # G.remove_edges_from([(0, i) for i in range(36,71)])

#     # remove 5 of either s or t jump nodes
#     G.remove_nodes_from(list(range(71,76))) # jump-s
#     # G.remove_nodes_from(range(81,86))

check_lg()