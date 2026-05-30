"""
Knowledge Graph Demo
Builds a small movie KG using two approaches:
  1. NetworkX (in-memory property graph — quick, no setup needed)
  2. RDFLib (semantic triple store — more formal, OWL/SPARQL compatible)
"""

# ─── Approach 1: NetworkX property graph ─────────────────────────────────────
print("=" * 60)
print("Approach 1: NetworkX Property Graph")
print("=" * 60)

import networkx as nx

G = nx.DiGraph()

# Nodes with attributes
people = [
    ("Christopher Nolan", {"type": "Person", "role": "Director"}),
    ("Leonardo DiCaprio",  {"type": "Person", "role": "Actor"}),
    ("Cillian Murphy",     {"type": "Person", "role": "Actor"}),
    ("Hans Zimmer",        {"type": "Person", "role": "Composer"}),
]

movies = [
    ("Inception",  {"type": "Movie", "year": 2010, "genre": "Sci-Fi", "rating": 8.8}),
    ("Interstellar",{"type": "Movie", "year": 2014, "genre": "Sci-Fi", "rating": 8.7}),
    ("Oppenheimer",{"type": "Movie", "year": 2023, "genre": "Drama",  "rating": 8.9}),
]

G.add_nodes_from(people)
G.add_nodes_from(movies)

# Edges with relation labels
edges = [
    ("Christopher Nolan", "Inception",   {"relation": "directed"}),
    ("Christopher Nolan", "Interstellar",{"relation": "directed"}),
    ("Christopher Nolan", "Oppenheimer", {"relation": "directed"}),
    ("Leonardo DiCaprio", "Inception",   {"relation": "acted_in"}),
    ("Cillian Murphy",    "Inception",   {"relation": "acted_in"}),
    ("Cillian Murphy",    "Oppenheimer", {"relation": "acted_in"}),
    ("Hans Zimmer",       "Inception",   {"relation": "composed_for"}),
    ("Hans Zimmer",       "Interstellar",{"relation": "composed_for"}),
    ("Inception",         "Interstellar",{"relation": "shares_director"}),
]

G.add_edges_from(edges)

# ── Simple queries over the graph ────────────────────────────────────────────
print("\nQuery 1: Movies directed by Christopher Nolan")
nolan_movies = [
    t for _, t, d in G.out_edges("Christopher Nolan", data=True)
    if d["relation"] == "directed"
]
print(f"  {nolan_movies}")

print("\nQuery 2: Actors in Inception")
inception_actors = [
    s for s, _, d in G.in_edges("Inception", data=True)
    if d["relation"] == "acted_in"
]
print(f"  {inception_actors}")

print("\nQuery 3: All movies with rating > 8.8")
high_rated = [
    n for n, d in G.nodes(data=True)
    if d.get("type") == "Movie" and d.get("rating", 0) > 8.8
]
print(f"  {high_rated}")

print(f"\nGraph stats: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")


# ─── Approach 2: RDFLib triple store ─────────────────────────────────────────
print("\n" + "=" * 60)
print("Approach 2: RDFLib Triple Store (Turtle serialisation)")
print("=" * 60)

try:
    from rdflib import Graph as RDFGraph, Namespace, RDF, RDFS, Literal
    from rdflib.namespace import XSD

    EX  = Namespace("http://example.org/kg/")
    SCHEMA = Namespace("http://schema.org/")

    g = RDFGraph()
    g.bind("ex", EX)
    g.bind("schema", SCHEMA)

    # Define resources
    nolan   = EX.ChristopherNolan
    leo     = EX.LeonardoDiCaprio
    cillian = EX.CillianMurphy
    zimmer  = EX.HansZimmer
    inception    = EX.Inception
    interstellar = EX.Interstellar
    oppenheimer  = EX.Oppenheimer

    # Type triples
    for person in [nolan, leo, cillian, zimmer]:
        g.add((person, RDF.type, SCHEMA.Person))
    for movie in [inception, interstellar, oppenheimer]:
        g.add((movie, RDF.type, SCHEMA.Movie))

    # Properties
    g.add((nolan, SCHEMA.name,    Literal("Christopher Nolan")))
    g.add((leo,   SCHEMA.name,    Literal("Leonardo DiCaprio")))
    g.add((cillian,SCHEMA.name,   Literal("Cillian Murphy")))
    g.add((zimmer, SCHEMA.name,   Literal("Hans Zimmer")))

    g.add((inception,    SCHEMA.name,           Literal("Inception")))
    g.add((inception,    SCHEMA.datePublished,   Literal("2010", datatype=XSD.gYear)))
    g.add((inception,    SCHEMA.director,        nolan))
    g.add((inception,    SCHEMA.actor,           leo))
    g.add((inception,    SCHEMA.actor,           cillian))
    g.add((inception,    EX.composedBy,          zimmer))
    g.add((inception,    SCHEMA.aggregateRating, Literal(8.8, datatype=XSD.float)))

    g.add((interstellar, SCHEMA.name,            Literal("Interstellar")))
    g.add((interstellar, SCHEMA.datePublished,   Literal("2014", datatype=XSD.gYear)))
    g.add((interstellar, SCHEMA.director,        nolan))
    g.add((interstellar, EX.composedBy,          zimmer))

    g.add((oppenheimer,  SCHEMA.name,            Literal("Oppenheimer")))
    g.add((oppenheimer,  SCHEMA.datePublished,   Literal("2023", datatype=XSD.gYear)))
    g.add((oppenheimer,  SCHEMA.director,        nolan))
    g.add((oppenheimer,  SCHEMA.actor,           cillian))

    print(f"\nTriple store contains {len(g)} triples\n")

    # SPARQL query: find all actors and their movies
    sparql_query = """
    PREFIX schema: <http://schema.org/>
    SELECT ?actorName ?movieName
    WHERE {
        ?movie schema:actor ?actor .
        ?actor schema:name  ?actorName .
        ?movie schema:name  ?movieName .
    }
    ORDER BY ?actorName
    """
    print("SPARQL Query: Find all actors and their movies")
    results = g.query(sparql_query)
    for row in results:
        print(f"  {row.actorName}  --[acted_in]-->  {row.movieName}")

    # Serialise to Turtle
    turtle_str = g.serialize(format="turtle")
    print("\n-- Turtle serialisation (first 10 lines) --")
    for line in turtle_str.split("\n")[:10]:
        print(f"  {line}")

except ImportError:
    print("  rdflib not installed — run: pip install rdflib")
    print("  (NetworkX demo above works without any extra packages)")
