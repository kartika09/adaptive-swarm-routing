
import pandas as pd

from simulation.network import create_network
from algorithms.dijkstra import run_dijkstra
from algorithms.aco import run_aco


# =====================================================
# EXPERIMENT CONFIGURATION
# =====================================================

NUMBER_OF_RUNS = 30

SOURCE = "A"
DESTINATION = "L"
FAILED_LINK = ("D", "G")

ALPHA = 1.0
BETA = 2.0
EVAPORATION = 0.2

INITIAL_PHEROMONE = 0.1
ADAPTATION_STRENGTH = 0.5

BUDGETS = {
    "Low": {"ants": 5, "iterations": 20},
    "Medium": {"ants": 10, "iterations": 50},
    "High": {"ants": 50, "iterations": 100},
}

individual_results = []


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def calculate_gap(cost, optimal_cost):

    if cost == float("inf") or optimal_cost == 0:
        return None

    return ((cost - optimal_cost) / optimal_cost) * 100


def route_to_string(path):

    return " -> ".join(path) if path else "No route"


# =====================================================
# RUN EXPERIMENTS
# =====================================================

for budget_name, budget in BUDGETS.items():

    ants = budget["ants"]
    iterations = budget["iterations"]

    print("\n" + "=" * 60)
    print(f"RUNNING {budget_name.upper()} BUDGET")
    print(f"Ants: {ants} | Iterations: {iterations}")
    print("=" * 60)

    for seed in range(NUMBER_OF_RUNS):

        print(f"{budget_name}: Run {seed + 1}/{NUMBER_OF_RUNS}")

        # ---------------------------------------------
        # PHASE 1: FRESH NETWORK AND PRE-FAILURE LEARNING
        # ---------------------------------------------

        G = create_network()

        _, _, learned_pheromones, _, _ = run_aco(
            G,
            SOURCE,
            DESTINATION,
            ants=ants,
            iterations=iterations,
            alpha=ALPHA,
            beta=BETA,
            evaporation=EVAPORATION,
            initial_pheromone=INITIAL_PHEROMONE,
            seed=seed
        )

        # ---------------------------------------------
        # PHASE 2: FAIL THE SELECTED LINK
        # ---------------------------------------------

        u, v = FAILED_LINK
        G[u][v]["active"] = False

        dijkstra_path, dijkstra_cost = run_dijkstra(
            G,
            SOURCE,
            DESTINATION
        )

        # ---------------------------------------------
        # PHASE 3: STANDARD ACO
        # ---------------------------------------------

        standard_path, standard_cost, _, _, standard_stagnation = (
            run_aco(
                G,
                SOURCE,
                DESTINATION,
                pheromones=learned_pheromones.copy(),
                ants=ants,
                iterations=iterations,
                alpha=ALPHA,
                beta=BETA,
                evaporation=EVAPORATION,
                initial_pheromone=INITIAL_PHEROMONE,
                adaptive=False,
                seed=1000 + seed
            )
        )

        # ---------------------------------------------
        # PHASE 4: ADAPTIVE ACO
        # ---------------------------------------------

        adaptive_path, adaptive_cost, _, _, adaptive_stagnation = (
            run_aco(
                G,
                SOURCE,
                DESTINATION,
                pheromones=learned_pheromones.copy(),
                ants=ants,
                iterations=iterations,
                alpha=ALPHA,
                beta=BETA,
                evaporation=EVAPORATION,
                initial_pheromone=INITIAL_PHEROMONE,
                adaptive=True,
                adaptation_strength=ADAPTATION_STRENGTH,
                seed=1000 + seed
            )
        )

        # ---------------------------------------------
        # PHASE 5: RECORD RESULTS
        # ---------------------------------------------

        if standard_cost < adaptive_cost:
            outcome = "Standard Win"
        elif adaptive_cost < standard_cost:
            outcome = "Adaptive Win"
        else:
            outcome = "Tie"

        individual_results.append({

            "Budget": budget_name,
            "Seed": seed,

            "Ants": ants,
            "Iterations": iterations,

            "Dijkstra Cost": dijkstra_cost,
            "Dijkstra Route": route_to_string(dijkstra_path),

            "Standard Cost": standard_cost,
            "Standard Gap (%)": calculate_gap(
                standard_cost, dijkstra_cost
            ),
            "Standard Route": route_to_string(standard_path),
            "Standard Stagnation": standard_stagnation,
            "Standard Optimal": standard_cost == dijkstra_cost,

            "Adaptive Cost": adaptive_cost,
            "Adaptive Gap (%)": calculate_gap(
                adaptive_cost, dijkstra_cost
            ),
            "Adaptive Route": route_to_string(adaptive_path),
            "Adaptive Stagnation": adaptive_stagnation,
            "Adaptive Optimal": adaptive_cost == dijkstra_cost,

            "Paired Outcome": outcome
        })


# =====================================================
# INDIVIDUAL RESULTS
# =====================================================

df = pd.DataFrame(individual_results)

print("\n\n========== INDIVIDUAL RESULTS ==========\n")
print(df.to_string(index=False))


# =====================================================
# SUMMARY STATISTICS
# =====================================================

summary_rows = []

for budget_name in BUDGETS:

    subset = df[df["Budget"] == budget_name]

    standard_costs = subset["Standard Cost"].replace(
        float("inf"), float("nan")
    )

    adaptive_costs = subset["Adaptive Cost"].replace(
        float("inf"), float("nan")
    )

    summary_rows.append({

        "Budget": budget_name,

        "Standard Mean Cost": standard_costs.mean(),
        "Adaptive Mean Cost": adaptive_costs.mean(),

        "Standard Mean Gap (%)": subset["Standard Gap (%)"].mean(),
        "Adaptive Mean Gap (%)": subset["Adaptive Gap (%)"].mean(),

        "Standard Optimal Rate (%)": (
            subset["Standard Optimal"].mean() * 100
        ),

        "Adaptive Optimal Rate (%)": (
            subset["Adaptive Optimal"].mean() * 100
        ),

        "Standard Std Dev": standard_costs.std(),
        "Adaptive Std Dev": adaptive_costs.std(),

        "Standard Mean Stagnation": (
            subset["Standard Stagnation"].mean()
        ),

        "Adaptive Mean Stagnation": (
            subset["Adaptive Stagnation"].mean()
        ),

        "Standard Wins": (
            subset["Paired Outcome"] == "Standard Win"
        ).sum(),

        "Adaptive Wins": (
            subset["Paired Outcome"] == "Adaptive Win"
        ).sum(),

        "Ties": (
            subset["Paired Outcome"] == "Tie"
        ).sum(),

        "Standard Failures": (
            subset["Standard Cost"] == float("inf")
        ).sum(),

        "Adaptive Failures": (
            subset["Adaptive Cost"] == float("inf")
        ).sum()
    })


summary = pd.DataFrame(summary_rows)

print("\n\n========== SUMMARY BY COMPUTATIONAL BUDGET ==========\n")
print(summary.to_string(index=False))


# =====================================================
# SAVE RESULTS
# =====================================================

df.to_csv("aco_multi_budget_individual.csv", index=False)

summary.to_csv("aco_multi_budget_summary.csv", index=False)

print("\n\nExperiment completed successfully.")

print("Saved:")
print("1. aco_multi_budget_individual.csv")
print("2. aco_multi_budget_summary.csv")
