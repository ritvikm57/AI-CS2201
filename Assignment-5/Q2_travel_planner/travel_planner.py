"""
AI Travel Planner
Uses a rule-based inference engine over the knowledge base to produce
personalised tour plans with cost estimates and food recommendations.
"""

from knowledge_base import (
    DESTINATIONS, FOOD_KB, ACCOMMODATION_COST, TRANSPORT_COST_FROM,
    INTEREST_CATEGORIES, DIETARY_OPTIONS, BUDGET_LEVELS
)


class UserProfile:
    def __init__(self, name, origin, month, duration_days, budget_level,
                 interests, dietary, nationality):
        self.name = name
        self.origin = origin             # e.g. "India"
        self.month = month               # 1-12
        self.duration_days = duration_days
        self.budget_level = budget_level # budget / mid / luxury
        self.interests = interests       # list of interest categories
        self.dietary = dietary           # vegetarian / vegan / halal / none
        self.nationality = nationality   # for visa check


class TravelPlanner:
    def __init__(self):
        self.destinations = DESTINATIONS
        self.food_kb = FOOD_KB
        self.accommodation = ACCOMMODATION_COST
        self.transport = TRANSPORT_COST_FROM

    # ── Scoring ──────────────────────────────────────────────────────────────

    def _score_destination(self, dest_name, profile):
        """Compute a relevance score for a destination given user preferences."""
        dest = self.destinations[dest_name]
        score = 0

        # Interest match: +2 per overlapping category
        for interest in profile.interests:
            if interest in dest["category"]:
                score += 2

        # Season match: +3 if this month is in the best months
        if profile.month in dest["best_months"]:
            score += 3

        # Budget check: rough daily cost vs level
        daily = dest["avg_daily_cost_usd"]
        if profile.budget_level == "budget" and daily <= 80:
            score += 2
        elif profile.budget_level == "mid" and 80 < daily <= 200:
            score += 2
        elif profile.budget_level == "luxury":
            score += 1  # luxury travellers can go anywhere

        # Visa penalty
        if profile.nationality in dest.get("visa_required", []):
            score -= 1

        return score

    def rank_destinations(self, profile, top_n=3):
        """Returns destinations sorted by suitability score."""
        scored = []
        for name in self.destinations:
            s = self._score_destination(name, profile)
            scored.append((name, s))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    # ── Cost estimation ───────────────────────────────────────────────────────

    def estimate_cost(self, dest_name, profile):
        acc_per_night = self.accommodation.get(profile.budget_level, {}).get(dest_name, 100)
        acc_total = acc_per_night * profile.duration_days

        transport = self.transport.get((profile.origin, dest_name), 700)

        food_per_day = {
            "budget": 20,
            "mid": 50,
            "luxury": 150
        }.get(profile.budget_level, 50)
        food_total = food_per_day * profile.duration_days

        misc_per_day = 30  # entrance fees, local transport, etc.
        misc_total = misc_per_day * profile.duration_days

        total = acc_total + transport + food_total + misc_total
        return {
            "accommodation": acc_total,
            "transport":     transport,
            "food":          food_total,
            "miscellaneous": misc_total,
            "total":         total,
        }

    # ── Itinerary generation ──────────────────────────────────────────────────

    def _distribute_attractions(self, attractions, days):
        """Spread attractions across days, roughly 2 per day."""
        plan = {}
        per_day = max(1, len(attractions) // days)
        idx = 0
        for day in range(1, days + 1):
            plan[f"Day {day}"] = []
            for _ in range(per_day):
                if idx < len(attractions):
                    plan[f"Day {day}"].append(attractions[idx])
                    idx += 1
        # put leftovers on last day
        while idx < len(attractions):
            plan[f"Day {days}"].append(attractions[idx])
            idx += 1
        return plan

    def generate_itinerary(self, dest_name, profile):
        dest = self.destinations[dest_name]
        food = self.food_kb.get(dest_name, {})
        cost = self.estimate_cost(dest_name, profile)

        day_plan = self._distribute_attractions(dest["attractions"], profile.duration_days)

        # Pick dietary-appropriate food suggestions
        dietary_food = food.get("dietary", {}).get(profile.dietary, [])
        budget_food = food.get("budget_options", [])
        fine_food = food.get("fine_dining", [])

        food_recs = food.get("must_try", [])[:3]
        if profile.dietary != "none" and dietary_food:
            food_recs = dietary_food[:3]

        return {
            "destination":   dest_name,
            "country":       dest["country"],
            "duration":      profile.duration_days,
            "day_plan":      day_plan,
            "food":          food_recs,
            "budget_eats":   budget_food,
            "fine_dining":   fine_food if profile.budget_level == "luxury" else [],
            "cost_breakdown": cost,
            "languages":     dest["languages"],
            "visa_needed":   profile.nationality in dest.get("visa_required", []),
        }

    # ── Main interface ────────────────────────────────────────────────────────

    def plan(self, profile, top_n=3):
        """Full pipeline: rank destinations and generate itineraries for each."""
        ranked = self.rank_destinations(profile, top_n=top_n)
        plans = []
        for dest_name, score in ranked:
            itinerary = self.generate_itinerary(dest_name, profile)
            itinerary["score"] = score
            plans.append(itinerary)
        return plans

    def print_plan(self, plan):
        p = plan
        print(f"\n{'='*55}")
        print(f"  Destination : {p['destination']}, {p['country']}")
        print(f"  Duration    : {p['duration']} days")
        print(f"  Match score : {p['score']}")
        print(f"  Visa needed : {'Yes' if p['visa_needed'] else 'No'}")
        print(f"  Languages   : {', '.join(p['languages'])}")
        print(f"\n  -- Day-by-Day Plan --")
        for day, activities in p["day_plan"].items():
            print(f"  {day}: {', '.join(activities) if activities else 'Free / Rest day'}")
        print(f"\n  -- Food Recommendations --")
        print(f"  Must try    : {', '.join(p['food'])}")
        print(f"  Budget eats : {', '.join(p['budget_eats'])}")
        if p["fine_dining"]:
            print(f"  Fine dining : {', '.join(p['fine_dining'])}")
        print(f"\n  -- Estimated Cost (USD) --")
        c = p["cost_breakdown"]
        print(f"  Accommodation : ${c['accommodation']}")
        print(f"  Transport     : ${c['transport']}")
        print(f"  Food          : ${c['food']}")
        print(f"  Miscellaneous : ${c['miscellaneous']}")
        print(f"  TOTAL         : ${c['total']}")
        print(f"{'='*55}")


# ─── Example usage ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    planner = TravelPlanner()

    user = UserProfile(
        name="Arjun",
        origin="India",
        month=4,
        duration_days=7,
        budget_level="mid",
        interests=["cultural", "historical", "nature"],
        dietary="vegetarian",
        nationality="India"
    )

    print(f"\nGenerating personalised travel plan for {user.name}...")
    plans = planner.plan(user, top_n=3)
    for plan in plans:
        planner.print_plan(plan)
