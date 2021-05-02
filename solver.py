import networkx as nx
import time
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_score
import sys
from os.path import basename, normpath
import glob
from heuristics import heuristics_greedy
from naive import naive

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
    sizes = sys.argv[1]

    log_suffix = time.strftime("%d%b_%H:%M:%S", time.localtime()) + ".txt"

    starttime = time.time()

    if 's' in sizes:
        print("-------- RUNNING SMALL INPUTS --------")
        inputs = sorted(glob.glob('inputs/small/*'))
        log = open('outputs/sm_score_' + log_suffix, 'w+')
        for input_path in inputs:
            output_path = 'outputs/small/' + basename(normpath(input_path))[:-3] + '.out'
            G = read_input_file(input_path)
            c, k = solve(G)
            assert is_valid_solution(G, c, k)
            distance = calculate_score(G, c, k)
            log.write(f"{input_path}: {distance}\n")
            write_output_file(G, c, k, output_path)
        log.close()
        print(f"small inputs runtime: {(time.time() - starttime)} sec")
        starttime = time.time()

    if 'm' in sizes:
        print("-------- RUNNING MEDIUM INPUTS --------")
        inputs = glob.glob('inputs/medium/*')
        log = open('outputs/md_score_' + log_suffix, 'w+')
        for input_path in inputs:
            output_path = 'outputs/medium/' + basename(normpath(input_path))[:-3] + '.out'
            log.write(f"{input_path}: ")
            G = read_input_file(input_path)
            c, k = solve(G)
            assert is_valid_solution(G, c, k)
            distance = calculate_score(G, c, k)
            log.write(f"{distance}\n")
            write_output_file(G, c, k, output_path)
        log.close()
        print(f"medium inputs runtime: {(time.time() - starttime)} sec")
        starttime = time.time()

    if 'l' in sizes:
        print("-------- RUNNING LARGE INPUTS --------")
        inputs = sorted(glob.glob('inputs/large/*'))
        log = open('outputs/lg_score_' + log_suffix, 'w+')
        for input_path in inputs:
            output_path = 'outputs/large/' + basename(normpath(input_path))[:-3] + '.out'
            G = read_input_file(input_path)
            c, k = solve(G)
            assert is_valid_solution(G, c, k)
            distance = calculate_score(G, c, k)
            log.write(f"{input_path}: {distance}\n")
            write_output_file(G, c, k, output_path)
        log.close()
        print(f"large inputs runtime: {(time.time() - starttime)} sec")