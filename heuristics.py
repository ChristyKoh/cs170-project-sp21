import networkx as nx
import numpy as np

def 

def score_edges(G):
    """
    heuristically calculate score of each edge
        G: networkx.Graph
    returns:
        s: score for each edge
    """
    for u,v in G.edges.data:
