"""
Bayesian Network — Medical Diagnosis Example

The classic "Asia" network (simplified) models:
  Visit to Asia  -->  Tuberculosis
  Smoking        -->  Lung Cancer
  Smoking        -->  Bronchitis
  Tuberculosis   -->  Dyspnoea (shortness of breath)
  Lung Cancer    -->  Dyspnoea
  Bronchitis     -->  Dyspnoea
  Tuberculosis   -->  X-ray positive
  Lung Cancer    -->  X-ray positive

All variables are binary: True / False.
Implemented using pgmpy (pip install pgmpy).
"""

try:
    from pgmpy.models import BayesianNetwork
    from pgmpy.factors.discrete import TabularCPD
    from pgmpy.inference import VariableElimination

    PGMPY = True
except ImportError:
    PGMPY = False
    print("[WARNING] pgmpy not installed. Run: pip install pgmpy")
    print("          Falling back to manual implementation below.\n")


# ─── pgmpy implementation ─────────────────────────────────────────────────────
def run_pgmpy():
    print("=" * 60)
    print("Bayesian Network — pgmpy implementation")
    print("=" * 60)

    # Define structure as list of edges
    model = BayesianNetwork([
        ("Asia",   "Tuberculosis"),
        ("Smoking","LungCancer"),
        ("Smoking","Bronchitis"),
        ("Tuberculosis","XRay"),
        ("LungCancer",  "XRay"),
        ("Tuberculosis","Dyspnoea"),
        ("LungCancer",  "Dyspnoea"),
        ("Bronchitis",  "Dyspnoea"),
    ])

    # CPD format: P(node | parents)
    # Columns correspond to parent combinations (False, True) or just (False, True) for no parents
    # Index 0 = False, Index 1 = True for the node

    cpd_asia    = TabularCPD("Asia",   2, [[0.99], [0.01]])
    cpd_smoking = TabularCPD("Smoking",2, [[0.50], [0.50]])

    cpd_tub = TabularCPD(
        "Tuberculosis", 2,
        [[0.99, 0.95],   # P(Tub=F | Asia=F), P(Tub=F | Asia=T)
         [0.01, 0.05]],  # P(Tub=T | Asia=F), P(Tub=T | Asia=T)
        evidence=["Asia"], evidence_card=[2]
    )

    cpd_cancer = TabularCPD(
        "LungCancer", 2,
        [[0.99, 0.90],
         [0.01, 0.10]],
        evidence=["Smoking"], evidence_card=[2]
    )

    cpd_bronch = TabularCPD(
        "Bronchitis", 2,
        [[0.70, 0.40],
         [0.30, 0.60]],
        evidence=["Smoking"], evidence_card=[2]
    )

    # XRay positive if Tuberculosis OR LungCancer
    # Parents: Tuberculosis, LungCancer → 4 combinations (FF, FT, TF, TT)
    cpd_xray = TabularCPD(
        "XRay", 2,
        [[0.95, 0.02, 0.03, 0.001],  # P(XRay=F | ...)
         [0.05, 0.98, 0.97, 0.999]], # P(XRay=T | ...)
        evidence=["Tuberculosis","LungCancer"], evidence_card=[2, 2]
    )

    # Dyspnoea if any of Tub, Cancer, Bronchitis
    # 8 combinations for 3 binary parents
    cpd_dysp = TabularCPD(
        "Dyspnoea", 2,
        [[0.90, 0.30, 0.20, 0.10, 0.10, 0.05, 0.02, 0.01],
         [0.10, 0.70, 0.80, 0.90, 0.90, 0.95, 0.98, 0.99]],
        evidence=["Tuberculosis","LungCancer","Bronchitis"], evidence_card=[2, 2, 2]
    )

    model.add_cpds(cpd_asia, cpd_smoking, cpd_tub, cpd_cancer, cpd_bronch, cpd_xray, cpd_dysp)

    assert model.check_model(), "Model CPDs are inconsistent!"
    print("Model structure valid.\n")

    infer = VariableElimination(model)

    # ── Query 1: P(LungCancer | Dyspnoea=True) ────────────────────────────────
    print("Query 1: P(LungCancer | Dyspnoea=True)")
    result = infer.query(["LungCancer"], evidence={"Dyspnoea": 1})
    print(result)

    # ── Query 2: P(Tuberculosis | XRay=True, Smoking=False) ─────────────────
    print("\nQuery 2: P(Tuberculosis | XRay=True, Smoking=False)")
    result = infer.query(["Tuberculosis"], evidence={"XRay": 1, "Smoking": 0})
    print(result)

    # ── Query 3: P(Dyspnoea | Smoking=True) ──────────────────────────────────
    print("\nQuery 3: P(Dyspnoea | Smoking=True)")
    result = infer.query(["Dyspnoea"], evidence={"Smoking": 1})
    print(result)

    # ── Query 4: Most likely explanation (MPE) ────────────────────────────────
    print("\nQuery 4: MAP — most likely disease given Dyspnoea=True, XRay=True")
    map_result = infer.map_query(
        ["Tuberculosis","LungCancer","Bronchitis"],
        evidence={"Dyspnoea": 1, "XRay": 1}
    )
    print("  Most likely diagnosis:", map_result)


# ─── Manual implementation (no pgmpy) ────────────────────────────────────────
# Implements exact inference via variable enumeration for a simpler 3-node network.
# Burglary --> Alarm <-- Earthquake
#              Alarm --> Call (neighbour calls)

def manual_joint():
    """
    Manual BN: Burglary & Earthquake cause Alarm; Alarm causes a neighbour to Call.
    Returns the full joint distribution as a dict.
    """
    P = {
        "Burglary":   {True: 0.001, False: 0.999},
        "Earthquake": {True: 0.002, False: 0.998},
    }

    # P(Alarm | Burglary, Earthquake)
    P_alarm = {
        (True,  True):  0.95,
        (True,  False): 0.94,
        (False, True):  0.29,
        (False, False): 0.001,
    }

    # P(Call | Alarm)
    P_call = {True: 0.90, False: 0.05}

    joint = {}
    for b in [True, False]:
        for e in [True, False]:
            for a in [True, False]:
                for c in [True, False]:
                    p = (P["Burglary"][b] *
                         P["Earthquake"][e] *
                         (P_alarm[(b, e)] if a else 1 - P_alarm[(b, e)]) *
                         (P_call[a] if c else 1 - P_call[a]))
                    joint[(b, e, a, c)] = p
    return joint


def marginalise(joint, query_idx, evidence):
    """
    Compute P(query_idx | evidence) by marginalising the joint.
    Variables: 0=Burglary, 1=Earthquake, 2=Alarm, 3=Call
    """
    numerator   = {True: 0.0, False: 0.0}
    denominator = 0.0

    for (b, e, a, c), prob in joint.items():
        world = [b, e, a, c]
        # Check evidence
        consistent = all(world[i] == v for i, v in evidence.items())
        if consistent:
            denominator += prob
            numerator[world[query_idx]] += prob

    if denominator == 0:
        return {True: 0, False: 0}
    return {True: numerator[True]/denominator, False: numerator[False]/denominator}


def run_manual():
    print("=" * 60)
    print("Manual Bayesian Network — Burglary/Earthquake/Alarm/Call")
    print("=" * 60)
    joint = manual_joint()

    # P(Burglary | Call=True)
    r = marginalise(joint, query_idx=0, evidence={3: True})
    print(f"\nP(Burglary | Call=True):")
    print(f"  True  = {r[True]:.6f}")
    print(f"  False = {r[False]:.6f}")

    # P(Alarm | Burglary=True, Earthquake=False)
    r2 = marginalise(joint, query_idx=2, evidence={0: True, 1: False})
    print(f"\nP(Alarm | Burglary=True, Earthquake=False):")
    print(f"  True  = {r2[True]:.6f}")
    print(f"  False = {r2[False]:.6f}")

    # Sanity check: probabilities sum to 1
    total = sum(joint.values())
    print(f"\nJoint distribution sums to: {total:.10f}  (should be 1.0)")


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if PGMPY:
        run_pgmpy()
        print()

    run_manual()
