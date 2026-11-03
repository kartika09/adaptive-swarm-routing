# Adaptive Swarm Routing Using Ant Colony Optimization



An interactive network-routing simulation that explores how Ant Colony Optimization (ACO) can respond to network topology changes, particularly link failures.



The project compares three routing approaches:



- **Dijkstra's Algorithm:** Shortest-path baseline.

- **Standard Ant Colony Optimization (ACO):** Uses pheromone-based probabilistic route selection.

- **Adaptive ACO:** Applies pheromone adaptation after a network topology change to help the ant colony discover alternative routes.



## Project Overview



Communication networks can experience topology changes when links fail. Routing algorithms must identify alternative paths while minimizing route cost.



This project investigates whether adapting pheromone levels after a link failure can help an ACO-based routing system discover good alternative routes.



The simulation uses a weighted, undirected synthetic network containing 12 routers (Aâ€“L) and 20 links.



## Features



- Interactive network topology visualization.

- Source and destination router selection.

- Comparison of Dijkstra, Standard ACO, and Adaptive ACO.

- Simulation of network link failures.

- Pheromone adaptation after topology changes.

- Route-cost comparison.

- ACO best-so-far convergence visualization.

- Multi-budget experimental evaluation.

- Experimental summary and individual-run CSV results.



## Algorithms



### 1. Dijkstra's Algorithm



Dijkstra's algorithm calculates the minimum-cost path between the selected source and destination. It serves as the shortest-path reference for evaluating the ACO approaches.



### 2. Standard ACO



Standard ACO uses artificial ants to construct candidate routes. Route selection is influenced by pheromone levels and edge weights.



Pheromone evaporation and deposition allow the colony to reinforce promising routes over successive iterations.



### 3. Adaptive ACO



Adaptive ACO introduces a pheromone adaptation mechanism after a topology change.



The adaptation rule is:



\\\[

\\tau'\_{ij}=(1-\\gamma)\\tau\_{ij}+\\gamma\\tau\_0

\\]



Where:



- \\(\\tau\_{ij}\\) is the existing pheromone level.

- \\(\\tau\_0\\) is the initial pheromone level.

- \\(\\gamma\\) is the adaptation strength.

- \\(\\tau'\_{ij}\\) is the adapted pheromone level.



This adjustment partially resets pheromone levels on active links towards the initial pheromone value, reducing the influence of previously learned routing preferences.



## Technology Stack



- Python

- Streamlit

- NetworkX

- Plotly

- Pandas



## Project Structure



```text

adaptive-swarm-routing/

â”‚

â”œâ”€â”€ algorithms/

â”‚   â”œâ”€â”€ \_\_init\_\_.py

â”‚   â”œâ”€â”€ aco.py

â”‚   â””â”€â”€ dijkstra.py

â”‚

â”œâ”€â”€ simulation/

â”‚   â”œâ”€â”€ \_\_init\_\_.py

â”‚   â””â”€â”€ network.py

â”‚

â”œâ”€â”€ visualization/

â”‚

â”œâ”€â”€ app.py

â”œâ”€â”€ evaluate\_aco.py

â”œâ”€â”€ aco\_multi\_budget\_summary.csv

â”œâ”€â”€ aco\_multi\_budget\_individual.csv

â”œâ”€â”€ requirements.txt

â””â”€â”€ README.md

```



## Installation and Setup



### 1. Clone the repository



```bash

git clone https://github.com/YOUR\_USERNAME/adaptive-swarm-routing.git

cd adaptive-swarm-routing

```



### 2. Create a virtual environment



```bash

python -m venv venv

```



Activate it on Windows:



```powershell

venv\\Scripts\\activate

```



### 3. Install dependencies



```bash

pip install -r requirements.txt

```



### 4. Run the application



```bash

streamlit run app.py

```



The application will open in your browser.



## Running the Experiments



Run the multi-budget evaluation using:



```bash

python evaluate\_aco.py

```



The evaluation compares Standard ACO and Adaptive ACO across three computational budgets:



| Budget | Number of Ants | Iterations |

|---|---:|---:|

| Low | 5 | 20 |

| Medium | 10 | 50 |

| High | 50 | 100 |



Each budget is evaluated across 30 random seeds.



The evaluation generates:



- `aco\_multi\_budget\_summary.csv`

- `aco\_multi\_budget\_individual.csv`



The summary file contains aggregate performance metrics, while the individual file contains run-level results.



## Evaluation Metrics



The experimental evaluation considers:



- Mean route cost.

- Mean optimality gap relative to Dijkstra.

- Optimal route rate.

- Standard deviation of route cost.

- Stagnation indicator.

- Paired wins, losses, and ties.

- Failed route counts.



## Demonstration



The Streamlit dashboard allows users to:



1\. Select source and destination routers.

2\. Run all three routing algorithms.

3\. Compare the resulting routes and costs.

4\. Simulate a network link failure.

5\. Observe how the routing algorithms respond to the changed topology.

6\. Examine ACO best-so-far route-cost histories.

7\. View the multi-budget experimental results.



## Scope and Limitations



- The network is synthetic and illustrative, not a real-world network topology.

- The experiments currently evaluate a specific topology and link-failure scenario.

- The results should not be interpreted as proof of general superiority of Adaptive ACO.

- The simulation focuses on route discovery and weighted path costs; it does not model packet transmission, traffic demand, or real-time network congestion.



## Future Improvements



- Evaluate additional network topologies.

- Test multiple link-failure scenarios.

- Investigate different pheromone adaptation strengths.

- Extend the evaluation to larger networks.



## Author



Developed as a project exploring swarm intelligence and adaptive routing in dynamic networks.




