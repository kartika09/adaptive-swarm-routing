
import random
import networkx as nx


def edge_key(u, v):
    """Return a consistent key for an undirected edge."""
    return tuple(sorted((u, v)))


def get_active_edges(G):
    """Get all currently active edges."""
    return [
        (u, v, data)
        for u, v, data in G.edges(data=True)
        if data.get("active", True)
    ]


def initialize_pheromones(G, initial_pheromone=0.1):
    """Initialize pheromone values for active edges."""
    pheromones = {}

    for u, v, data in get_active_edges(G):
        pheromones[edge_key(u, v)] = initial_pheromone

    return pheromones


def adapt_pheromones(
    G,
    pheromones,
    initial_pheromone=0.1,
    adaptation_strength=0.5
):
    """Adapt active-edge pheromones after a topology change."""
    adapted_pheromones = pheromones.copy()

    for u, v, data in get_active_edges(G):
        key = edge_key(u, v)

        old_value = adapted_pheromones.get(
            key,
            initial_pheromone
        )

        adapted_pheromones[key] = (
            (1 - adaptation_strength) * old_value
            + adaptation_strength * initial_pheromone
        )

    return adapted_pheromones


def construct_ant_path(
    G,
    source,
    destination,
    pheromones,
    alpha=1.0,
    beta=2.0
):
    """Construct one ant's route using pheromone and edge weight."""

    current = source
    path = [source]
    visited = {source}
    total_cost = 0

    while current != destination:

        candidates = []

        for neighbor in G.neighbors(current):

            if neighbor in visited:
                continue

            edge_data = G[current][neighbor]

            if not edge_data.get("active", True):
                continue

            weight = edge_data["weight"]
            key = edge_key(current, neighbor)
            tau = pheromones.get(key, 0.1)

            desirability = (
                (tau ** alpha)
                * ((1.0 / weight) ** beta)
            )

            candidates.append(
                (neighbor, weight, desirability)
            )

        if not candidates:
            return None, float("inf")

        probabilities_total = sum(
            item[2] for item in candidates
        )

        if probabilities_total <= 0:
            return None, float("inf")

        probabilities = [
            item[2] / probabilities_total
            for item in candidates
        ]

        selected_index = random.choices(
            range(len(candidates)),
            weights=probabilities,
            k=1
        )[0]

        next_node, edge_weight, _ = candidates[selected_index]

        path.append(next_node)
        visited.add(next_node)
        total_cost += edge_weight
        current = next_node

    return path, total_cost


def run_aco(
    G,
    source,
    destination,
    ants=10,
    iterations=50,
    alpha=1.0,
    beta=2.0,
    evaporation=0.2,
    initial_pheromone=0.1,
    pheromones=None,
    adaptive=False,
    adaptation_strength=0.5,
    patience=10,
    seed=None
):
    """
    Run Ant Colony Optimization.

    Returns:
        best_path: Best route discovered.
        best_cost: Cost of the best route.
        pheromones: Updated pheromone dictionary.
        history: Best-so-far cost after each iteration.
        stagnation_iteration: First iteration at which the
                              patience threshold is reached.
    """

    # Set the random seed for reproducibility.
    if seed is not None:
        random.seed(seed)

    if pheromones is None:
        pheromones = initialize_pheromones(
            G,
            initial_pheromone
        )
    else:
        pheromones = pheromones.copy()

    if adaptive:
        pheromones = adapt_pheromones(
            G,
            pheromones,
            initial_pheromone,
            adaptation_strength
        )

    best_path = None
    best_cost = float("inf")

    history = []
    iterations_without_improvement = 0
    stagnation_iteration = None

    elite_weight = 2.0
    pheromone_min = 0.001
    pheromone_max = 10.0

    for iteration in range(iterations):

        # Capture previous best BEFORE constructing ants.
        previous_best = best_cost

        successful_paths = []

        # Construct routes for all ants.
        for _ in range(ants):

            path, cost = construct_ant_path(
                G,
                source,
                destination,
                pheromones,
                alpha,
                beta
            )

            if path is not None:
                successful_paths.append((path, cost))

                if cost < best_cost:
                    best_path = path
                    best_cost = cost

        # Evaporate pheromones on active edges.
        for u, v, data in get_active_edges(G):

            key = edge_key(u, v)

            old_value = pheromones.get(
                key,
                initial_pheromone
            )

            pheromones[key] = (
                (1 - evaporation) * old_value
            )

        # Deposit pheromones from successful ant routes.
        for path, cost in successful_paths:

            if cost <= 0:
                continue

            deposit = 1.0 / cost

            for i in range(len(path) - 1):

                key = edge_key(
                    path[i],
                    path[i + 1]
                )

                pheromones[key] = (
                    pheromones.get(key, initial_pheromone)
                    + deposit
                )

        # Reinforce the global best route.
        if best_path is not None and best_cost > 0:

            elite_deposit = elite_weight / best_cost

            for i in range(len(best_path) - 1):

                key = edge_key(
                    best_path[i],
                    best_path[i + 1]
                )

                pheromones[key] = (
                    pheromones.get(key, initial_pheromone)
                    + elite_deposit
                )

        # Keep pheromone values within stable limits.
        for key in pheromones:

            pheromones[key] = max(
                pheromone_min,
                min(pheromone_max, pheromones[key])
            )

        # Track stagnation correctly.
        if best_cost < previous_best:
            iterations_without_improvement = 0
        else:
            iterations_without_improvement += 1

        if (
            stagnation_iteration is None
            and iterations_without_improvement >= patience
        ):
            stagnation_iteration = iteration + 1

        # Store best-so-far cost.
        history.append(best_cost)

    return (
        best_path,
        best_cost,
        pheromones,
        history,
        stagnation_iteration
    )
