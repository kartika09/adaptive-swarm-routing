
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import pandas as pd

from pathlib import Path

from simulation.network import create_network
from algorithms.dijkstra import run_dijkstra
from algorithms.aco import (
    run_aco,
    initialize_pheromones,
    adapt_pheromones,
    edge_key
)


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Adaptive Swarm Routing",
    page_icon="🐜",
    layout="wide"
)

st.title("🐜 Adaptive Swarm Routing")
st.caption(
    "Swarm Intelligence for Dynamic Network Routing"
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "network" not in st.session_state:
    st.session_state.network = create_network()

G = st.session_state.network

if "standard_pheromones" not in st.session_state:
    st.session_state.standard_pheromones = (
        initialize_pheromones(G)
    )

if "adaptive_pheromones" not in st.session_state:
    st.session_state.adaptive_pheromones = (
        initialize_pheromones(G)
    )

if "routing_results" not in st.session_state:
    st.session_state.routing_results = None

if "event_message" not in st.session_state:
    st.session_state.event_message = None


# ==========================================================
# SIDEBAR: NETWORK CONFIGURATION
# ==========================================================

st.sidebar.header("Network Configuration")

nodes = list(G.nodes())

source = st.sidebar.selectbox(
    "Source Router",
    nodes,
    index=0
)

destination = st.sidebar.selectbox(
    "Destination Router",
    nodes,
    index=len(nodes) - 1
)

st.sidebar.divider()


# ==========================================================
# SIDEBAR: ACO PARAMETERS
# ==========================================================

st.sidebar.subheader("ACO Parameters")

ants = st.sidebar.slider(
    "Number of Ants",
    min_value=5,
    max_value=100,
    value=50
)

iterations = st.sidebar.slider(
    "Iterations",
    min_value=10,
    max_value=200,
    value=100
)

alpha = st.sidebar.slider(
    "Pheromone Importance (α)",
    min_value=0.5,
    max_value=3.0,
    value=1.0
)

beta = st.sidebar.slider(
    "Heuristic Importance (β)",
    min_value=0.5,
    max_value=5.0,
    value=2.0
)

evaporation = st.sidebar.slider(
    "Evaporation Rate (ρ)",
    min_value=0.05,
    max_value=0.5,
    value=0.2
)

st.sidebar.divider()


# ==========================================================
# SIDEBAR: NETWORK EVENTS
# ==========================================================

st.sidebar.subheader("Network Events")

edges = list(G.edges())

edge_labels = [
    f"{u} - {v}"
    for u, v in edges
]

selected_edge = st.sidebar.selectbox(
    "Select a connection",
    edge_labels
)

if st.sidebar.button(
    "Simulate Link Failure",
    use_container_width=True
):

    u, v = selected_edge.split(" - ")

    if G[u][v]["active"]:

        G[u][v]["active"] = False

        # Adapt the Adaptive ACO pheromone state
        # immediately after the topology change.
        st.session_state.adaptive_pheromones = (
            adapt_pheromones(
                G,
                st.session_state.adaptive_pheromones,
                initial_pheromone=0.1,
                adaptation_strength=0.5
            )
        )

        st.session_state.routing_results = None

        st.session_state.event_message = (
            f"Link failure simulated: {u} - {v}"
        )

        st.rerun()

    else:
        st.sidebar.warning("This link is already inactive.")


if st.sidebar.button(
    "Restore All Links",
    use_container_width=True
):

    for u, v in G.edges():
        G[u][v]["active"] = True

    # Start a fresh experiment after restoring the network.
    st.session_state.standard_pheromones = (
        initialize_pheromones(G)
    )

    st.session_state.adaptive_pheromones = (
        initialize_pheromones(G)
    )

    st.session_state.routing_results = None

    st.session_state.event_message = (
        "All links restored. Pheromone states reset."
    )

    st.rerun()


# ==========================================================
# EVENT STATUS
# ==========================================================

if st.session_state.event_message:

    st.info(st.session_state.event_message)


# ==========================================================
# RUN ROUTING COMPARISON
# ==========================================================

st.subheader("Routing Simulation")

st.write(
    "Compare Dijkstra, Standard ACO, and Adaptive ACO "
    "on the current network topology."
)

run_button = st.button(
    "Run Routing Comparison",
    type="primary",
    use_container_width=True
)

if run_button:

    if source == destination:

        st.warning(
            "Source and destination must be different."
        )

    else:

        with st.spinner("Running routing algorithms..."):

            # ------------------------------------------
            # DIJKSTRA
            # ------------------------------------------

            dijkstra_path, dijkstra_cost = run_dijkstra(
                G,
                source,
                destination
            )

            # ------------------------------------------
            # STANDARD ACO
            # ------------------------------------------

            (
                standard_path,
                standard_cost,
                standard_pheromones,
                standard_history,
                standard_stagnation
            ) = run_aco(
                G,
                source,
                destination,
                ants=ants,
                iterations=iterations,
                alpha=alpha,
                beta=beta,
                evaporation=evaporation,
                pheromones=(
                    st.session_state.standard_pheromones
                ),
                adaptive=False,
                seed=42
            )

            # ------------------------------------------
            # ADAPTIVE ACO
            # ------------------------------------------

            (
                adaptive_path,
                adaptive_cost,
                adaptive_pheromones,
                adaptive_history,
                adaptive_stagnation
            ) = run_aco(
                G,
                source,
                destination,
                ants=ants,
                iterations=iterations,
                alpha=alpha,
                beta=beta,
                evaporation=evaporation,
                pheromones=(
                    st.session_state.adaptive_pheromones
                ),
                adaptive=False,
                seed=42
            )

            # ------------------------------------------
            # SAVE PHEROMONE STATES
            # ------------------------------------------

            st.session_state.standard_pheromones = (
                standard_pheromones
            )

            st.session_state.adaptive_pheromones = (
                adaptive_pheromones
            )

            # ------------------------------------------
            # SAVE RESULTS
            # ------------------------------------------

            st.session_state.routing_results = {
                "Dijkstra": {
                    "path": dijkstra_path,
                    "cost": dijkstra_cost,
                    "history": [],
                    "stagnation": None
                },
                "Standard ACO": {
                    "path": standard_path,
                    "cost": standard_cost,
                    "history": standard_history,
                    "stagnation": standard_stagnation
                },
                "Adaptive ACO": {
                    "path": adaptive_path,
                    "cost": adaptive_cost,
                    "history": adaptive_history,
                    "stagnation": adaptive_stagnation
                }
            }

            st.success("Routing comparison completed!")


# ==========================================================
# NETWORK METRICS
# ==========================================================

active_links = sum(
    1
    for _, _, data in G.edges(data=True)
    if data["active"]
)

failed_links = G.number_of_edges() - active_links

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Routers",
    G.number_of_nodes()
)

col2.metric(
    "Total Links",
    G.number_of_edges()
)

col3.metric(
    "Active Links",
    active_links
)

col4.metric(
    "Failed Links",
    failed_links
)


# ==========================================================
# ROUTING RESULTS
# ==========================================================

results = st.session_state.routing_results

selected_algorithm = st.selectbox(
    "Route to Highlight",
    [
        "Dijkstra",
        "Standard ACO",
        "Adaptive ACO"
    ]
)

selected_result = None

if results is not None:

    st.subheader("Algorithm Comparison")

    comparison_rows = []

    for name, result in results.items():

        route = result["path"]
        cost = result["cost"]

        if route is None:
            route_text = "No route"
            cost_text = "Unreachable"
        else:
            route_text = " → ".join(route)
            cost_text = f"{cost:.2f}"

        comparison_rows.append({
            "Algorithm": name,
            "Route": route_text,
            "Route Cost": cost_text
        })

    comparison_df = pd.DataFrame(comparison_rows)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    selected_result = results[selected_algorithm]

    st.subheader(
        f"{selected_algorithm} Routing Result"
    )

    if selected_result["path"] is not None:

        st.success("A valid route was found!")

        st.write(
            " → ".join(selected_result["path"])
        )

        st.metric(
            "Selected Route Cost",
            f"{selected_result['cost']:.2f}"
        )

        if selected_algorithm != "Dijkstra":

            stagnation = selected_result["stagnation"]

            if stagnation is not None:
                st.write(
                    f"**Stagnation indicator:** "
                    f"Iteration {stagnation}"
                )
            else:
                st.write(
                    "**Stagnation indicator:** "
                    "Not reached within the iteration limit"
                )

    else:

        st.error(
            "No available route between the selected routers."
        )

    if results["Dijkstra"]["path"] is not None:

        reference_cost = results["Dijkstra"]["cost"]

        if selected_result["path"] is not None:

            difference = (
                selected_result["cost"] - reference_cost
            )

            st.write(
                f"**Difference from Dijkstra:** "
                f"{difference:+.2f}"
            )

else:

    st.info(
        "Select your source and destination, then click "
        "'Run Routing Comparison' to calculate routes."
    )


# ==========================================================
# NETWORK VISUALIZATION
# ==========================================================

st.subheader("Network Topology")

positions = nx.spring_layout(
    G,
    seed=42,
    weight="weight"
)

fig = go.Figure()

if results is not None and selected_result is not None:
    highlighted_path = selected_result["path"]
else:
    highlighted_path = None

highlighted_edges = set()

if highlighted_path:

    for i in range(len(highlighted_path) - 1):

        highlighted_edges.add(
            edge_key(
                highlighted_path[i],
                highlighted_path[i + 1]
            )
        )


# ------------------------------------------
# DRAW EDGES
# ------------------------------------------

for u, v, data in G.edges(data=True):

    x0, y0 = positions[u]
    x1, y1 = positions[v]

    key = edge_key(u, v)

    active = data["active"]

    if not active:

        color = "#EF4444"
        width = 2
        dash = "dash"

    elif key in highlighted_edges:

        color = "#22C55E"
        width = 5
        dash = "solid"

    else:

        color = "#94A3B8"
        width = 1.5
        dash = "solid"

    if selected_algorithm == "Adaptive ACO":
        pheromone = st.session_state.adaptive_pheromones.get(
            key, 0.1
        )
    else:
        pheromone = st.session_state.standard_pheromones.get(
            key, 0.1
        )

    fig.add_trace(
        go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode="lines",
            line=dict(
                color=color,
                width=width,
                dash=dash
            ),
            hovertemplate=(
                f"{u} — {v}<br>"
                f"Cost: {data['weight']}<br>"
                f"Status: {'Active' if active else 'Failed'}<br>"
                f"Pheromone: {pheromone:.4f}"
                "<extra></extra>"
            ),
            showlegend=False
        )
    )

    # Edge weight labels.
    fig.add_annotation(
        x=(x0 + x1) / 2,
        y=(y0 + y1) / 2,
        text=str(data["weight"]),
        showarrow=False,
        font=dict(
            size=10,
            color="#64748B"
        ),
        bgcolor="rgba(255,255,255,0.8)"
    )


# ------------------------------------------
# DRAW NODES
# ------------------------------------------

node_colors = []

for node in nodes:

    if node == source:
        node_colors.append("#16A34A")

    elif node == destination:
        node_colors.append("#2563EB")

    else:
        node_colors.append("#64748B")


fig.add_trace(
    go.Scatter(
        x=[positions[n][0] for n in nodes],
        y=[positions[n][1] for n in nodes],
        mode="markers+text",
        text=nodes,
        textposition="middle center",
        marker=dict(
            size=32,
            color=node_colors,
            line=dict(
                color="white",
                width=2
            )
        ),
        hovertemplate="Router %{text}<extra></extra>",
        showlegend=False
    )
)


fig.update_layout(
    height=600,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    "Green: selected route | "
    "Grey: active link | "
    "Red dashed: failed link"
)


# ==========================================================
# ACO CONVERGENCE
# ==========================================================

if results is not None:

    st.subheader("ACO Convergence")

    convergence_fig = go.Figure()

    for name in ["Standard ACO", "Adaptive ACO"]:

        history = results[name]["history"]

        convergence_fig.add_trace(
            go.Scatter(
                x=list(range(1, len(history) + 1)),
                y=history,
                mode="lines",
                name=name
            )
        )

    convergence_fig.update_layout(
        xaxis_title="Iteration",
        yaxis_title="Best-so-far Route Cost",
        height=400,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(
        convergence_fig,
        use_container_width=True
    )

    st.caption(
        "The curves show the best route cost found up to "
        "each iteration. They do not imply a formal "
        "convergence guarantee."
    )


# ==========================================================
# EXPERIMENTAL RESULTS
# ==========================================================

st.divider()

st.header("Experimental Evaluation")

st.write(
    "Results from the multi-budget evaluation of "
    "Standard ACO and Adaptive ACO."
)

base_directory = Path(__file__).resolve().parent

summary_file = (
    base_directory / "aco_multi_budget_summary.csv"
)

individual_file = (
    base_directory / "aco_multi_budget_individual.csv"
)

if summary_file.exists():

    summary_df = pd.read_csv(summary_file)

    st.subheader("Multi-Budget Summary")

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )

    # Mean route cost comparison.
    required_columns = [
        "Budget",
        "Standard Mean Cost",
        "Adaptive Mean Cost"
    ]

    if all(col in summary_df.columns for col in required_columns):

        cost_fig = go.Figure()

        cost_fig.add_trace(
            go.Bar(
                x=summary_df["Budget"],
                y=summary_df["Standard Mean Cost"],
                name="Standard ACO"
            )
        )

        cost_fig.add_trace(
            go.Bar(
                x=summary_df["Budget"],
                y=summary_df["Adaptive Mean Cost"],
                name="Adaptive ACO"
            )
        )

        cost_fig.update_layout(
            title="Mean Route Cost by Ant Budget",
            xaxis_title="Ant Budget",
            yaxis_title="Mean Route Cost",
            barmode="group",
            height=400
        )

        st.plotly_chart(
            cost_fig,
            use_container_width=True
        )

    # Optimal rate comparison.
    optimal_columns = [
        "Budget",
        "Standard Optimal Rate (%)",
        "Adaptive Optimal Rate (%)"
    ]

    if all(col in summary_df.columns for col in optimal_columns):

        optimal_fig = go.Figure()

        optimal_fig.add_trace(
            go.Bar(
                x=summary_df["Budget"],
                y=summary_df["Standard Optimal Rate (%)"],
                name="Standard ACO"
            )
        )

        optimal_fig.add_trace(
            go.Bar(
                x=summary_df["Budget"],
                y=summary_df["Adaptive Optimal Rate (%)"],
                name="Adaptive ACO"
            )
        )

        optimal_fig.update_layout(
            title="Optimal Route Rate by Ant Budget",
            xaxis_title="Ant Budget",
            yaxis_title="Optimal Rate (%)",
            barmode="group",
            height=400
        )

        st.plotly_chart(
            optimal_fig,
            use_container_width=True
        )

    if individual_file.exists():

        with st.expander("View Individual Experimental Runs"):

            individual_df = pd.read_csv(individual_file)

            st.dataframe(
                individual_df,
                use_container_width=True,
                hide_index=True
            )

    st.caption(
        "These are experimental results for the evaluated "
        "synthetic topology and link-failure scenario. "
        "They should not be interpreted as proof of "
        "general superiority."
    )

else:

    st.warning(
        "Experimental summary CSV not found. "
        "Place aco_multi_budget_summary.csv in the "
        "same folder as app.py to display the results."
    )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "Adaptive Swarm Routing | "
    "Dijkstra • Standard ACO • Adaptive ACO"
)
