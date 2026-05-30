# Q4 — Bayesian Networks: Tools and Implementation

## 1. What is a Bayesian Network?

A Bayesian Network (BN) is a probabilistic graphical model that represents a set of variables and their conditional dependencies using a **Directed Acyclic Graph (DAG)**.

Each node in the DAG represents a random variable. Each edge `A → B` means "A has a direct probabilistic influence on B." For each node, a **Conditional Probability Table (CPT)** stores `P(node | its parents)`.

The key property is that the **full joint distribution** can be factored as a product:

```
P(X₁, X₂, ..., Xₙ) = ∏ᵢ P(Xᵢ | parents(Xᵢ))
```

This makes storage and computation tractable even for many variables.

---

## 2. Core Concepts

| Concept | Description |
|---|---|
| **Prior probability** | P(X) — belief about X before any evidence |
| **Likelihood** | P(Evidence \| Hypothesis) |
| **Posterior probability** | P(Hypothesis \| Evidence) — updated belief |
| **D-separation** | Graphical criterion for conditional independence |
| **Markov Blanket** | A node's parents, children, and co-parents; knowing these makes the node independent of all others |
| **CPT** | Conditional Probability Table — the parameters of each node |

---

## 3. Types of Inference

**Exact inference:**
- **Variable Elimination** — sum out irrelevant variables one by one
- **Belief Propagation** — message passing on tree-structured networks
- **Junction Tree algorithm** — exact inference on general graphs via clique trees

**Approximate inference (when exact is NP-hard):**
- **Rejection Sampling** — generate samples, keep those consistent with evidence
- **Likelihood Weighting** — weight samples by evidence probability (more efficient)
- **MCMC (Gibbs Sampling)** — Markov chain sampling from the posterior

---

## 4. Tools for Bayesian Networks

### 4.1 pgmpy (Python)
The most popular Python library for probabilistic graphical models.
```bash
pip install pgmpy
```
Supports:
- BayesianNetwork, NaiveBayes, Dynamic BNs
- CPT specification
- Inference: VariableElimination, BeliefPropagation, CausalInference
- Structure learning from data (PC, Hill Climb, TreeSearch)
- Parameter learning (MLE, Bayesian estimation)

### 4.2 Pomegranate (Python)
```bash
pip install pomegranate
```
- Faster than pgmpy for large networks
- Supports both BNs and Hidden Markov Models
- GPU acceleration via PyTorch backend

### 4.3 BayesiaLab
- Commercial GUI tool for BN modelling, learning, and inference
- Used extensively in medical diagnosis and risk assessment
- Supports causal modelling and counterfactual reasoning

### 4.4 Hugin Expert
- Commercial and academic BN tool
- One of the oldest and most feature-rich tools
- API available for Java, C, C++

### 4.5 GeNIe / SMILE (Bayesfusion)
- Free for academic use
- Graphical interface to build and query BNs
- SMILE library usable from Python/C++

### 4.6 Netica
- Commercial tool with Python/Java API
- Widely used in ecology and environmental risk

### 4.7 bnlearn (R)
- Comprehensive R package for structure and parameter learning
- Best-in-class for learning BN structure from data
```r
install.packages("bnlearn")
```

### 4.8 Stan / PyMC
- General probabilistic programming; can express BNs
- Best for custom models, MCMC inference
```bash
pip install pymc
```

---

## 5. Example: Asia Network (Medical Diagnosis)

The **Asia network** is a classic benchmark BN modelling respiratory disease:

```
Visit-to-Asia ──→ Tuberculosis ──→ Dyspnoea
                                ↑
Smoking ──→ LungCancer ─────────┤
        ↘                        │
          Bronchitis ────────────┘
Tuberculosis ──→ XRay ←─ LungCancer
```

### Variables (all binary: True/False)
| Variable | Meaning |
|---|---|
| Asia | Patient recently visited Asia |
| Smoking | Patient is a smoker |
| Tuberculosis | Patient has TB |
| LungCancer | Patient has lung cancer |
| Bronchitis | Patient has bronchitis |
| XRay | Chest X-ray is abnormal |
| Dyspnoea | Patient has shortness of breath |

### Example Queries
1. **P(LungCancer | Dyspnoea=True)** — How much more likely is lung cancer if the patient reports shortness of breath?
2. **P(Tuberculosis | XRay=True, Smoking=False)** — If a non-smoker has an abnormal X-ray, what is the probability of TB?
3. **MAP query** — given observed symptoms, which combination of diseases is most probable?

### Key Observation — Explaining Away
If a patient has Dyspnoea and we discover they have Bronchitis, the probability of LungCancer goes *down* even though Dyspnoea is still present. This is called "explaining away" — one cause accounts for the observation, making other causes less likely. This is captured naturally in BNs through d-separation but cannot be expressed in flat probability tables.

---

## 6. Implementation

See `bayesian_network.py` for two implementations:

1. **pgmpy** — full Asia network with CPTs and Variable Elimination inference
2. **Manual** — Burglary/Earthquake/Alarm/Call network using direct joint enumeration (no external library needed)

And `test_bayesian.py` for correctness tests on the manual implementation.

---

## 7. Summary

Bayesian Networks are a principled way to model uncertainty and causality. They are used in:
- Medical diagnosis (probability of disease given symptoms)
- Spam filtering (naive Bayes is a degenerate BN)
- Autonomous vehicles (sensor fusion under uncertainty)
- Risk assessment in finance and engineering
- Causal inference and counterfactual reasoning

The choice of tool depends on scale and purpose: **pgmpy** for prototyping in Python, **bnlearn** for structure learning in R, **BayesiaLab** for production systems, and **PyMC/Stan** for bespoke probabilistic models.
