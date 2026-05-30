"""
Test cases for the AI Travel Planner.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from travel_planner import TravelPlanner, UserProfile

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    print(f"  [{status}] {name}  {detail}")

planner = TravelPlanner()

# ── Test 1: Budget traveller should prefer Bali ────────────────────────────
print("\n=== Test 1: Budget beach traveller ===")
u = UserProfile("TestUser", "India", 6, 5, "budget", ["beach"], "none", "India")
plans = planner.plan(u, top_n=3)
top_dest = plans[0]["destination"]
check("Top recommendation is Bali for budget+beach", top_dest == "Bali", f"(got {top_dest})")

# ── Test 2: Cost breakdown adds up ───────────────────────────────────────────
print("\n=== Test 2: Cost arithmetic ===")
u2 = UserProfile("CostTest", "US", 9, 5, "mid", ["cultural"], "none", "US")
cost = planner.estimate_cost("Barcelona", u2)
manual = cost["accommodation"] + cost["transport"] + cost["food"] + cost["miscellaneous"]
check("Cost total equals sum of components", cost["total"] == manual,
      f"(total={cost['total']}, sum={manual})")

# ── Test 3: Dietary filter applied ───────────────────────────────────────────
print("\n=== Test 3: Dietary recommendations ===")
u3 = UserProfile("VeganUser", "India", 4, 4, "mid", ["cultural"], "vegan", "India")
itinerary = planner.generate_itinerary("Kyoto", u3)
food_items = itinerary["food"]
check("Vegan food recs are non-empty for Kyoto", len(food_items) > 0)

# ── Test 4: Visa flag is set correctly ────────────────────────────────────────
print("\n=== Test 4: Visa detection ===")
# US passport requires visa for Paris
u4 = UserProfile("VisaTest", "US", 5, 7, "luxury", ["cultural"], "none", "US")
it = planner.generate_itinerary("Paris", u4)
check("US citizen flagged as needing visa for Paris", it["visa_needed"] == True)

# ── Test 5: Itinerary covers all requested days ────────────────────────────────
print("\n=== Test 5: Itinerary day coverage ===")
u5 = UserProfile("DayCover", "India", 10, 6, "mid", ["nature"], "none", "India")
it5 = planner.generate_itinerary("Cape Town", u5)
check("Day plan has entries for all 6 days", len(it5["day_plan"]) == 6,
      f"(got {len(it5['day_plan'])} days)")

# ── Test 6: Season penalty — peak season vs off season ───────────────────────
print("\n=== Test 6: Season scoring ===")
u_peak = UserProfile("PeakSeason", "India", 4, 5, "mid", ["cultural"], "none", "India")
u_off  = UserProfile("OffSeason",  "India", 1, 5, "mid", ["cultural"], "none", "India")
ranked_peak = planner.rank_destinations(u_peak, top_n=6)
ranked_off  = planner.rank_destinations(u_off,  top_n=6)
score_peak = dict(ranked_peak).get("Kyoto", 0)
score_off  = dict(ranked_off).get("Kyoto", 0)
check("Kyoto scores higher in peak months (Mar/Apr)", score_peak >= score_off,
      f"(peak={score_peak}, off={score_off})")

print()
