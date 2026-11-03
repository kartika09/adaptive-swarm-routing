"""Network model for routing simulations."""

import networkx as nx

def create_network():
    """Create a temporary illustrative undirected network."""

    G = nx.Graph()

    nodes = list("ABCDEFGHIJKL")
    G.add_nodes_from(nodes)

    edges = [
        ("A", "B", 4),
        ("A", "C", 3),
        ("A", "D", 7),
        ("B", "C", 2),
        ("B", "E", 5),
        ("C", "D", 3),
        ("C", "F", 6),
        ("D", "F", 2),
        ("D", "G", 5),
        ("E", "F", 2),
        ("E", "H", 4),
        ("F", "G", 3),
        ("F", "I", 5),
        ("G", "J", 3),
        ("H", "I", 2),
        ("H", "K", 5),
        ("I", "J", 2),
        ("I", "L", 4),
        ("J", "L", 3),
        ("K", "L", 2),
    ]

    for u, v, weight in edges:
        G.add_edge(
            u,
            v,
            weight=weight,
            active=True
        )

    return G
