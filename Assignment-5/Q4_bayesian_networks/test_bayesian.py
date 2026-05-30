"""
Tests for the manual Bayesian Network implementation.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from bayesian_network import manual_joint, marginalise

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    print(f"  [{status}] {name}  {detail}")

def approx(a, b, tol=1e-4):
    return abs(a - b) < tol


joint = manual_joint()
print("\n=== Manual BN Tests ===")

# Joint distribution must sum to 1
total = sum(joint.values())
check("Joint sums to 1", approx(total, 1.0), f"(got {total:.8f})")

# All probabilities are non-negative
check("All probabilities >= 0", all(v >= 0 for v in joint.values()))

# P(Burglary=T | Call=T) should be much higher than prior P(Burglary=T) = 0.001
r_burglary = marginalise(joint, 0, {3: True})
check("P(Burglary|Call=T) > prior 0.001", r_burglary[True] > 0.001,
      f"(got {r_burglary[True]:.6f})")

# Conditional probabilities must sum to 1
check("P(Burglary|Call=T) sums to 1",
      approx(r_burglary[True] + r_burglary[False], 1.0))

# P(Alarm | Burglary=T, Earthquake=F) should be ~0.94 (from CPT)
r_alarm = marginalise(joint, 2, {0: True, 1: False})
check("P(Alarm=T|Burg=T,EQ=F) ≈ 0.94", approx(r_alarm[True], 0.94, tol=0.01),
      f"(got {r_alarm[True]:.6f})")

# Without any evidence, P(Alarm=T) should be very low (rare event)
r_alarm_prior = marginalise(joint, 2, {})
check("P(Alarm=T) is small without evidence", r_alarm_prior[True] < 0.1,
      f"(got {r_alarm_prior[True]:.6f})")

# Earthquake makes alarm more likely even without burglary
r_eq = marginalise(joint, 2, {0: False, 1: True})
r_no_eq = marginalise(joint, 2, {0: False, 1: False})
check("Earthquake raises alarm probability",
      r_eq[True] > r_no_eq[True],
      f"(with EQ={r_eq[True]:.4f}, without EQ={r_no_eq[True]:.4f})")

print()
