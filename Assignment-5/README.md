# Assignment 5 — AI Techniques: Search, Planning, and Probabilistic Reasoning

Implementation of adversarial search algorithms, AI-based travel planning, knowledge graph exploration, and Bayesian networks.

---

## Repository Structure

```text
Assignment 5:
├── Task 1: Game Tree Search Algorithms (Tic-Tac-Toe)
│   ├── game.py
│   ├── minimax.py
│   ├── alpha_beta.py
│   ├── heuristic_alpha_beta.py
│   ├── mcts.py
│   └── test_algorithms.py
├── Task 2: AI-Based Travel Planner
│   ├── knowledge_base.py
│   ├── travel_planner.py
│   └── test_planner.py
├── Task 3: Knowledge Graphs
│   ├── knowledge_graphs_report.md
│   └── kg_demo.py
└── Task 4: Bayesian Networks
    ├── bayesian_network.py
    ├── bayesian_report.md
    └── test_bayesian.py
```

---

## Task 1: Game Tree Search Algorithms

Implementation and comparison of four adversarial search algorithms using **Tic-Tac-Toe** as the game environment.

### Algorithms Implemented

* Minimax Search
* Alpha-Beta Pruning
* Heuristic Alpha-Beta Search (depth-limited)
* Monte-Carlo Tree Search (MCTS)

### Key Concepts

* Two-player zero-sum games
* Maximising and minimising players (X and O)
* Utility functions (+1 win, −1 loss, 0 draw)
* Full game-tree expansion vs. depth-limited search
* Alpha and beta cutoff conditions
* Heuristic evaluation of non-terminal states
* UCB1 selection in MCTS
* Simulation-based search via random rollouts

### Heuristic Evaluation Function

The heuristic scores non-terminal board states by counting "open lines":

```
+10  for 2-in-a-line with empty third cell (X)
-10  for 2-in-a-line with empty third cell (O)
+3   for 1-in-a-line (X)
-3   for 1-in-a-line (O)
```

Terminal wins are scaled by ×100 so they always outweigh heuristic estimates.

### MCTS — Four Phases

```
Selection      →  UCB1 traversal from root to leaf
Expansion      →  Add one new child node
Simulation     →  Random rollout to terminal state
Backpropagation →  Update win/visit counts up the tree
```

### Test Cases

* Immediate winning move detection
* Win before blocking (optimal play)
* Node count comparison across algorithms
* Cross-algorithm agreement on optimal moves

### Key Insights

| Algorithm | Nodes (empty board) | Notes |
|---|---|---|
| Minimax | 549,945 | Exhaustive, optimal |
| Alpha-Beta | 30,709 | ~18× fewer, same result |
| Heuristic AB (depth 3) | 305 | Fast, approximate |
| MCTS (1000 iters) | — | Stochastic, scalable |

* Minimax guarantees optimal play but explores the full game tree.
* Alpha-Beta gives the same optimal result with significantly fewer nodes explored.
* Heuristic Alpha-Beta trades some accuracy for speed — practical for larger games.
* MCTS does not need a handcrafted evaluation function and scales well to games with large branching factors (e.g., Go, Chess).

### How to Run

```bash
cd Q1_search_algorithms
python3 test_algorithms.py
```

---

## Task 2: AI-Based Travel Planner

An AI-based travel planner that reuses structured domain knowledge bases to generate personalised tour plans.

### Knowledge Base Components

* **Destinations** — 6 cities (Paris, Kyoto, Barcelona, Bali, New York, Cape Town) with categories, best travel months, and daily cost estimates
* **Food KB** — must-try dishes, dietary filters (vegetarian, vegan, halal), budget eats, and fine dining per city
* **Accommodation costs** — per budget level (budget / mid / luxury) per city
* **Transport costs** — approximate round-trip airfares from common origins
* **User preferences** — interests, dietary requirements, travel month, duration, budget, nationality

### Features

* Interest-based destination scoring
* Seasonal suitability scoring (best travel months)
* Budget-level matching
* Visa requirement flag
* Day-by-day itinerary generation
* Dietary-aware food recommendations
* Itemised cost breakdown (accommodation + transport + food + miscellaneous)

### Scoring Formula

Each destination receives a score based on:

```
+2 per matching interest category
+3 if travel month falls in best months
+2 if daily cost matches budget level
-1 if visa is required for user's nationality
```

The top-N destinations are returned ranked by score.

### Example Output

```
Destination : Kyoto, Japan
Match score : 11
Day 1: Fushimi Inari
Day 2: Arashiyama Bamboo
...
Food        : Shojin Ryori, Tofu dishes
TOTAL Cost  : $1910
```

### How to Run

```bash
cd Q2_travel_planner
python3 travel_planner.py   # runs example plan for a user profile
python3 test_planner.py     # runs all 6 test cases
```

---

## Task 3: Knowledge Graphs and KG Tools

A study of knowledge graphs with a working code demonstration.

### What is a Knowledge Graph?

A Knowledge Graph represents real-world entities and their relationships as a directed graph of triples:

```
(Subject) --[Predicate]--> (Object)
```

Example:
```
(Christopher Nolan) --[directed]-->  (Inception)
(Inception)         --[released_in]--> (2010)
```

### Topics Covered

* Entities, relationships, and attributes
* RDF triples, Turtle serialisation, SPARQL queries
* OWL ontologies and schema-level reasoning
* Semantic search and explainable inference
* Real-world KGs: Wikidata, Google KG, DBpedia

### Tools Explored

| Tool | Type | Use Case |
|---|---|---|
| RDFLib | Python library | RDF triple store, SPARQL, Turtle I/O |
| NetworkX | Python library | Property graph, quick prototyping |
| Neo4j | Graph database | Connected data, recommendation engines |
| Protégé | Desktop GUI | OWL ontology modelling |
| Apache Jena / Fuseki | Java triple store | Production-scale SPARQL endpoints |
| Stardog | Enterprise KG DB | OWL reasoning, finance/pharma use cases |
| Amazon Neptune | Cloud graph DB | Managed SPARQL / Gremlin service |
| PyKeen | Python library | Knowledge graph embeddings, link prediction |

### Code Demo

`kg_demo.py` builds a movie knowledge graph (Nolan films) using two approaches:

1. **NetworkX** — property graph with custom queries
2. **RDFLib** — RDF triple store with SPARQL and Turtle serialisation

### How to Run

```bash
pip install networkx rdflib
cd Q3_knowledge_graphs
python3 kg_demo.py
```

---

## Task 4: Bayesian Networks

Implementation of probabilistic reasoning using Bayesian Networks.

### What is a Bayesian Network?

A Bayesian Network is a probabilistic graphical model using a Directed Acyclic Graph (DAG). Each node is a random variable, each edge encodes a direct probabilistic dependency, and each node has a Conditional Probability Table (CPT).

The joint distribution factorises as:

```
P(X₁, ..., Xₙ) = ∏ P(Xᵢ | parents(Xᵢ))
```

### Example 1 — Asia Medical Diagnosis Network (pgmpy)

Models respiratory disease diagnosis with 7 binary variables:

```
Visit-to-Asia ──→ Tuberculosis ──→ Dyspnoea
                                ↑
Smoking ──→ LungCancer ─────────┤
        ↘                       │
          Bronchitis ───────────┘
Tuberculosis, LungCancer ──→ XRay
```

Queries implemented:
* P(LungCancer | Dyspnoea = True)
* P(Tuberculosis | XRay = True, Smoking = False)
* P(Dyspnoea | Smoking = True)
* MAP query — most likely disease combination given symptoms

### Example 2 — Burglary/Alarm Network (manual, no dependencies)

```
Burglary ──→ Alarm ──→ Call
Earthquake ─┘
```

Implemented using direct joint distribution enumeration. No external libraries required.

### Inference Method

* **Variable Elimination** (via pgmpy)
* **Full joint enumeration** (manual implementation)

### Tools Explored

| Tool | Language | Strengths |
|---|---|---|
| pgmpy | Python | BN, structure learning, inference |
| Pomegranate | Python | Faster, GPU support via PyTorch |
| BayesiaLab | GUI | Production use, medical/risk |
| Hugin Expert | GUI + API | Oldest, most complete |
| bnlearn | R | Best structure learning from data |
| PyMC / Stan | Python | Custom probabilistic models, MCMC |

### How to Run

```bash
# No external libraries needed for the manual network
cd Q4_bayesian_networks
python3 bayesian_network.py

# For the full Asia network, install pgmpy first
pip install pgmpy
python3 bayesian_network.py

# Test suite
python3 test_bayesian.py
```

---

## Dependencies

```bash
pip install networkx rdflib pgmpy
```

All test suites (Q1, Q2, Q4) run without any external packages. Only the KG demo (Q3) requires `networkx`/`rdflib`, and the Asia BN (Q4) requires `pgmpy` — both fall back gracefully if not installed.

---

## Running All Tests

```bash
cd Q1_search_algorithms && python3 test_algorithms.py  # 16 tests
cd Q2_travel_planner    && python3 test_planner.py     # 6 tests
cd Q4_bayesian_networks && python3 test_bayesian.py    # 7 tests
```
