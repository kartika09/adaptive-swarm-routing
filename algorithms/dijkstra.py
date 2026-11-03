"""Dijkstra shortest-path algorithm."""

import networkx as nx

def run_dijkstra(G, source, destination):

    # Create a temporary graph containing only active links
    active_graph = nx.Graph()
    active_graph.add_nodes_from(G.nodes(data=True))

    for u, v, data in G.edges(data=True):
        if data["active"]:
            active_graph.add_edge(
                u,
                v,
                weight=data["weight"]
            )

    try:
        path = nx.shortest_path(
            active_graph,
            source=source,
            target=destination,
            weight="weight",
            method="dijkstra"
        )

        cost = nx.path_weight(
            active_graph,
            path,
            weight="weight"
        )

        return path, cost

    except nx.NetworkXNoPath:
        return None, float("inf")
