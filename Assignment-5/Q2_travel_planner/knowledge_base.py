"""
Knowledge Base for AI Travel Planner
Contains structured facts about destinations, food, budgets, and activities.
Organised as Python dicts/lists to simulate a lightweight ontology.
In a production system these would be stored in an RDF/OWL triple store.
"""

# ─── Destinations ────────────────────────────────────────────────────────────
DESTINATIONS = {
    "Paris": {
        "country": "France",
        "climate": "temperate",
        "category": ["cultural", "romantic", "historical"],
        "best_months": [4, 5, 6, 9, 10],
        "avg_daily_cost_usd": 200,
        "attractions": ["Eiffel Tower", "Louvre Museum", "Versailles", "Montmartre"],
        "languages": ["French"],
        "visa_required": ["US", "Australia"],
    },
    "Kyoto": {
        "country": "Japan",
        "climate": "humid subtropical",
        "category": ["cultural", "historical", "nature"],
        "best_months": [3, 4, 10, 11],
        "avg_daily_cost_usd": 120,
        "attractions": ["Fushimi Inari", "Arashiyama Bamboo", "Kinkaku-ji", "Gion District"],
        "languages": ["Japanese"],
        "visa_required": [],
    },
    "Barcelona": {
        "country": "Spain",
        "climate": "mediterranean",
        "category": ["beach", "cultural", "nightlife"],
        "best_months": [5, 6, 9, 10],
        "avg_daily_cost_usd": 150,
        "attractions": ["Sagrada Familia", "Park Güell", "La Boqueria", "Barceloneta Beach"],
        "languages": ["Spanish", "Catalan"],
        "visa_required": ["US", "Australia"],
    },
    "Bali": {
        "country": "Indonesia",
        "climate": "tropical",
        "category": ["beach", "spiritual", "nature", "budget"],
        "best_months": [4, 5, 6, 7, 8, 9],
        "avg_daily_cost_usd": 60,
        "attractions": ["Ubud Rice Terraces", "Tanah Lot", "Seminyak Beach", "Mount Batur"],
        "languages": ["Indonesian", "Balinese"],
        "visa_required": [],
    },
    "New York": {
        "country": "USA",
        "climate": "humid continental",
        "category": ["urban", "cultural", "shopping"],
        "best_months": [4, 5, 9, 10],
        "avg_daily_cost_usd": 250,
        "attractions": ["Central Park", "Times Square", "MoMA", "Brooklyn Bridge"],
        "languages": ["English"],
        "visa_required": ["India", "China"],
    },
    "Cape Town": {
        "country": "South Africa",
        "climate": "mediterranean",
        "category": ["nature", "adventure", "cultural"],
        "best_months": [11, 12, 1, 2, 3],
        "avg_daily_cost_usd": 80,
        "attractions": ["Table Mountain", "Cape Point", "Robben Island", "Boulders Beach"],
        "languages": ["English", "Afrikaans", "Xhosa"],
        "visa_required": [],
    },
}

# ─── Food Recommendations (by destination) ──────────────────────────────────
FOOD_KB = {
    "Paris": {
        "must_try": ["Croissant", "Crêpes", "Boeuf Bourguignon", "French Onion Soup", "Macarons"],
        "dietary": {
            "vegetarian": ["Ratatouille", "Soupe à l'oignon", "Crêpes"],
            "vegan": ["Ratatouille", "Tarte flambée (vegan option)"],
            "halal": ["Available in Marais district"],
        },
        "budget_options": ["Street crêpes (~€3)", "Boulangerie sandwiches (~€5)"],
        "fine_dining": ["Le Jules Verne", "L'Ambroisie"],
    },
    "Kyoto": {
        "must_try": ["Kaiseki", "Matcha desserts", "Tofu dishes", "Ramen", "Yakitori"],
        "dietary": {
            "vegetarian": ["Shojin Ryori (Buddhist cuisine)", "Tofu dishes"],
            "vegan": ["Shojin Ryori"],
            "halal": ["Halal Ramen Kyoto", "some Indian restaurants"],
        },
        "budget_options": ["Ramen (~¥900)", "Conveyor belt sushi (~¥1500)"],
        "fine_dining": ["Kikunoi", "Mizai"],
    },
    "Barcelona": {
        "must_try": ["Paella", "Tapas", "Patatas Bravas", "Croquetas", "Churros"],
        "dietary": {
            "vegetarian": ["Patatas Bravas", "Pan con tomate", "most tapas"],
            "vegan": ["Gazpacho", "bread-based tapas"],
            "halal": ["Available in El Raval district"],
        },
        "budget_options": ["Bocadillo (~€3)", "Menú del día (~€10)"],
        "fine_dining": ["Tickets", "Disfrutar"],
    },
    "Bali": {
        "must_try": ["Nasi Goreng", "Satay", "Babi Guling", "Gado-gado", "Mie Goreng"],
        "dietary": {
            "vegetarian": ["Gado-gado", "Nasi Goreng (veg)", "Tempeh"],
            "vegan": ["Jamu (herbal drink)", "most rice dishes"],
            "halal": ["Most local warungs serve halal food"],
        },
        "budget_options": ["Warung meal (~IDR 30,000)", "Fresh coconut (~IDR 10,000)"],
        "fine_dining": ["Locavore", "Mozaic Restaurant"],
    },
    "New York": {
        "must_try": ["New York Pizza", "Bagels", "Pastrami on rye", "Cheesecake", "Hot dogs"],
        "dietary": {
            "vegetarian": ["Lots of options citywide"],
            "vegan": ["Superiority Burger", "By Chloe"],
            "halal": ["Halal cart food is iconic — every street corner"],
        },
        "budget_options": ["Street hot dog (~$2)", "Dollar pizza slice (~$1.50)"],
        "fine_dining": ["Le Bernardin", "Eleven Madison Park"],
    },
    "Cape Town": {
        "must_try": ["Braai (BBQ)", "Bunny Chow", "Bobotie", "Boerewors", "Rooibos tea"],
        "dietary": {
            "vegetarian": ["Potjiekos (veg)", "Samoosas"],
            "vegan": ["Most Cape Malay dishes adaptable"],
            "halal": ["Bo-Kaap neighbourhood has halal options"],
        },
        "budget_options": ["Bunny Chow (~R45)", "Street braai (~R60)"],
        "fine_dining": ["La Colombe", "Test Kitchen"],
    },
}

# ─── Cost model ─────────────────────────────────────────────────────────────
ACCOMMODATION_COST = {
    "budget":  {"Paris": 60,  "Kyoto": 40,  "Barcelona": 55, "Bali": 15, "New York": 80,  "Cape Town": 25},
    "mid":     {"Paris": 150, "Kyoto": 100, "Barcelona": 120,"Bali": 50, "New York": 200, "Cape Town": 80},
    "luxury":  {"Paris": 400, "Kyoto": 300, "Barcelona": 350,"Bali": 200,"New York": 500, "Cape Town": 250},
}

TRANSPORT_COST_FROM = {
    # approximate round-trip airfare in USD from common origins
    ("India", "Paris"):      900,
    ("India", "Kyoto"):      650,
    ("India", "Barcelona"):  800,
    ("India", "Bali"):       350,
    ("India", "New York"):   950,
    ("India", "Cape Town"):  700,
    ("US", "Paris"):         600,
    ("US", "Kyoto"):         800,
    ("US", "Barcelona"):     500,
    ("US", "Bali"):          1100,
    ("US", "New York"):      0,
    ("US", "Cape Town"):     900,
}

# ─── User preference taxonomy ────────────────────────────────────────────────
INTEREST_CATEGORIES = ["beach", "cultural", "historical", "nature", "urban",
                       "adventure", "romantic", "nightlife", "spiritual", "budget"]

DIETARY_OPTIONS = ["vegetarian", "vegan", "halal", "none"]

BUDGET_LEVELS = ["budget", "mid", "luxury"]
