import networkx as nx
import time
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_score, diff_score_files
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
        return heuristics_greedy(G, 1, 15)
    elif size <= 50:
        return heuristics_greedy(G, 3, 50)
    else:
        return heuristics_greedy(G, 5, 100)

def run_input(size):
    print(f"-------- RUNNING {size.upper()} INPUTS --------")
    starttime = time.time()
    inputs = sorted(glob.glob(f'inputs/{size}/*'))
    log = open(f'outputs/{size}_score_{log_suffix}', 'w+')
    for input_path in inputs:
        name = basename(normpath(input_path))
        output_path = f'outputs/{size}/{name[:-3]}.out'
        G = read_input_file(input_path)
        c, k = solve(G)
        assert is_valid_solution(G, c, k)
        distance = calculate_score(G, c, k)
        log.write(f"{name}: {distance}\n")
        write_output_file(G, c, k, output_path)
    log.close()
    print(f"runtime: {(time.time() - starttime)} sec")


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
    # size = ['small', 'medium', 'large']
    # size = ['medium']
    # for s in size:
    #     inputs = glob.glob('inputs/'+ s + '/*')
    #     for input_path in inputs:
    #         print(input_path)
    #         output_path = 'outputs/' + s + '/' + basename(normpath(input_path))[:-3] + '.out'
    #         G = read_input_file(input_path)
    #         c, k = solve(G)
    #         assert is_valid_solution(G, c, k)
    #         distance = calculate_score(G, c, k)
    #         write_output_file(G, c, k, output_path)
    #     print(s + ' complete')
    sizes = sys.argv[1]

    log_suffix = time.strftime("%d%m%y_%H:%M:%S", time.localtime()) + ".txt"

    if 's' in sizes:
        run_input('small')
        diff_score_files('small')

    if 'm' in sizes:
        run_input('medium')
        diff_score_files('medium')

    if 'l' in sizes:
        run_input('large')
        diff_score_files('large')
