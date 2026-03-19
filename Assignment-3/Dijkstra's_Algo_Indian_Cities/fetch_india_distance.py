"""
fetch_india_distances.py

Builds a sparse road graph of major Indian cities using the
Google Maps Distance Matrix API.

Strategy:
    - For each city, fetch road distances to ALL other cities (1 request per city)
    - Keep each city's K nearest neighbors as edges
    - Union rule: keep an edge if EITHER city considers the other a top-K neighbor
    - Total: 80 requests, ~6320 elements, costs ~$0.03 (well within free $200 credit)

Usage:
    pip install requests
    python fetch_india_distances.py --key YOUR_API_KEY
    # or via env var:
    GOOGLE_MAPS_API_KEY=your_key python fetch_india_distances.py

Output:
    india_distances.json  — raw NxN distance matrix
    india_edges.json      — sparse edge list [{from, to, km}]
    india_edges.csv       — same as CSV
"""

import argparse
import csv
import json
import os
import time
from datetime import datetime

import requests

# ── City list ─────────────────────────────────────────────────────────────────

CITIES = [
    # North UP
    "Delhi, India", "Agra, India", "Lucknow, India", "Kanpur, India",
    "Varanasi, India", "Prayagraj, India", "Meerut, India", "Bareilly, India",
    "Aligarh, India", "Mathura, India", "Moradabad, India",
    # Rajasthan
    "Jaipur, India", "Jodhpur, India", "Udaipur, India", "Kota, India",
    "Ajmer, India", "Bikaner, India",
    # Punjab / Haryana / HP / Uttarakhand
    "Chandigarh, India", "Amritsar, India", "Ludhiana, India", "Jalandhar, India",
    "Faridabad, India", "Gurugram, India", "Ambala, India",
    "Shimla, India", "Dehradun, India", "Haridwar, India",
    # J&K
    "Jammu, India", "Srinagar, India",
    # Bihar / Jharkhand
    "Patna, India", "Gaya, India", "Ranchi, India", "Jamshedpur, India",
    "Dhanbad, India", "Muzaffarpur, India",
    # West Bengal / Northeast
    "Kolkata, India", "Siliguri, India", "Guwahati, India",
    "Shillong, India", "Agartala, India", "Imphal, India",
    # Odisha
    "Bhubaneswar, India", "Cuttack, India", "Rourkela, India",
    # MP / Chhattisgarh
    "Bhopal, India", "Indore, India", "Jabalpur, India", "Gwalior, India",
    "Raipur, India", "Bilaspur, India",
    # Maharashtra
    "Mumbai, India", "Pune, India", "Nagpur, India", "Nashik, India",
    "Aurangabad, India", "Solapur, India", "Kolhapur, India",
    # Gujarat
    "Ahmedabad, India", "Surat, India", "Vadodara, India", "Rajkot, India",
    "Bhavnagar, India", "Jamnagar, India",
    # Andhra / Telangana
    "Hyderabad, India", "Visakhapatnam, India", "Vijayawada, India",
    "Tirupati, India", "Warangal, India", "Guntur, India",
    # Karnataka
    "Bengaluru, India", "Mysuru, India", "Hubli, India",
    "Mangalore, India", "Belagavi, India", "Davangere, India",
    # Tamil Nadu
    "Chennai, India", "Coimbatore, India", "Madurai, India",
    "Salem, India", "Tiruchirappalli, India", "Tirunelveli, India", "Vellore, India",
    # Kerala
    "Kochi, India", "Thiruvananthapuram, India", "Kozhikode, India", "Thrissur, India",
    # Goa
    "Panaji, Goa, India",
]

N = len(CITIES)
K = 6
DELAY = 0.25
API_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
BATCH = 25


def short_name(city: str) -> str:
    return city.replace(", Goa, India", "").replace(", India", "")


def fetch_distances_from(origin: str, destinations: list[str], api_key: str) -> list[int | None]:
    """Fetch road distances from one origin to a batch of destinations."""
    params = {
        "origins":      origin,
        "destinations": "|".join(destinations),
        "mode":         "driving",
        "units":        "metric",
        "key":          api_key,
    }
    resp = requests.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data["status"] != "OK":
        raise RuntimeError(f"API error: {data['status']} — {data.get('error_message', '')}")

    results = []
    for el in data["rows"][0]["elements"]:
        if el["status"] == "OK":
            results.append(round(el["distance"]["value"] / 1000))
        else:
            results.append(None)
    return results


def fetch_all_from(origin: str, destinations: list[str], api_key: str) -> list[int | None]:
    """Fetch distances from one origin to all destinations, batching as needed."""
    all_results = []
    for start in range(0, len(destinations), BATCH):
        batch = destinations[start : start + BATCH]
        results = fetch_distances_from(origin, batch, api_key)
        all_results.extend(results)
        if start + BATCH < len(destinations):
            time.sleep(DELAY)
    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Build a sparse India road graph using K-nearest-neighbors + union rule"
    )
    parser.add_argument(
        "--key",
        default=os.getenv("GOOGLE_MAPS_API_KEY"),
        help="Google Maps API key (or set GOOGLE_MAPS_API_KEY env var)",
    )
    parser.add_argument(
        "--k", type=int, default=K,
        help=f"Number of nearest neighbors to keep per city (default: {K})",
    )
    parser.add_argument(
        "--delay", type=float, default=DELAY,
        help=f"Delay between API requests in seconds (default: {DELAY})",
    )
    parser.add_argument(
        "--out-dir", default=".",
        help="Directory to write output files (default: current dir)",
    )
    args = parser.parse_args()

    if not args.key:
        parser.error("No API key. Use --key YOUR_KEY or set GOOGLE_MAPS_API_KEY env var.")

    print(f"\nFetching distances for {N} cities, keeping {args.k} nearest neighbors each")
    print(f"    Total API requests: {N}  |  Total elements: ~{N * (N-1):,}\n")

    # NxN distance matrix — None = unreachable
    dist: list[list[int | None]] = [[None] * N for _ in range(N)]
    for i in range(N):
        dist[i][i] = 0

    # nearest[i] = sorted list of (km, j) for all reachable j != i
    nearest: list[list[tuple[int, int]]] = [[] for _ in range(N)]

    for i, origin in enumerate(CITIES):
        # All other cities as destinations
        other_indices = [j for j in range(N) if j != i]
        other_cities  = [CITIES[j] for j in other_indices]

        try:
            results = fetch_all_from(origin, other_cities, args.key)
        except Exception as e:
            print(f"\n  Failed for {short_name(origin)}: {e}")
            continue

        for idx, j in enumerate(other_indices):
            km = results[idx]
            if km is not None:
                dist[i][j] = km
                nearest[i].append((km, j))

        # Sort by road distance ascending
        nearest[i].sort()

        top = nearest[i][:args.k]
        top_names = ", ".join(short_name(CITIES[j]) for _, j in top)
        print(f"  [{i+1:2d}/{N}] {short_name(origin):<22} - nearest {args.k}: {top_names}")

        time.sleep(args.delay)

    print(f"\nAll cities fetched.\n")

    os.makedirs(args.out_dir, exist_ok=True)

    matrix_path = os.path.join(args.out_dir, "india_distances.json")
    with open(matrix_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated": datetime.utcnow().isoformat() + "Z",
                "cities":    CITIES,
                "matrix":    dist,
            },
            f, indent=2,
        )
    print(f"Written: {matrix_path}")

    edge_set: dict[tuple[int, int], int] = {}

    for i in range(N):
        for _, j in nearest[i][:args.k]:
            key = (min(i, j), max(i, j))
            km  = dist[i][j] or dist[j][i]
            if km is not None:
                edge_set[key] = km

    edges = [
        {"from": short_name(CITIES[i]), "to": short_name(CITIES[j]), "km": km}
        for (i, j), km in sorted(edge_set.items(), key=lambda x: x[1])
    ]

    edges_json_path = os.path.join(args.out_dir, "india_edges.json")
    with open(edges_json_path, "w", encoding="utf-8") as f:
        json.dump(edges, f, indent=2)
    print(f"Written: {edges_json_path}  ({len(edges):,} edges)")

    edges_csv_path = os.path.join(args.out_dir, "india_edges.csv")
    with open(edges_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["from", "to", "km"])
        writer.writeheader()
        writer.writerows(edges)
    print(f"Written: {edges_csv_path}")
    kms = [e["km"] for e in edges]
    if kms:
        min_e = min(edges, key=lambda e: e["km"])
        max_e = max(edges, key=lambda e: e["km"])
        print(f"\nSummary:")
        print(f"   Cities     : {N}")
        print(f"   Edges      : {len(edges):,}")
        print(f"   Shortest   : {min_e['km']} km  ({min_e['from']} - {min_e['to']})")
        print(f"   Longest    : {max_e['km']} km  ({max_e['from']} - {max_e['to']})")
        print(f"   Avg edge   : {round(sum(kms) / len(kms))} km")

        city_mentions = {}
        for e in edges:
            city_mentions[e["from"]] = city_mentions.get(e["from"], 0) + 1
            city_mentions[e["to"]]   = city_mentions.get(e["to"],   0) + 1
        isolated = [short_name(c) for c in CITIES if short_name(c) not in city_mentions]
        if isolated:
            print(f"\nWarning: Isolated cities (no edges):")
            for c in isolated:
                print(f"     {c}")
        else:
            print(f"\nAll cities connected.")


if __name__ == "__main__":
    main()