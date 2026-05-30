# Q3 — Knowledge Graphs: Description and Tools

## 1. What is a Knowledge Graph?

A Knowledge Graph (KG) is a structured representation of real-world entities and the relationships between them. Entities are represented as **nodes** and relationships as directed **edges**, forming a graph where each fact is expressed as a triple:

```
(Subject) --[Predicate]--> (Object)
```

For example:
```
(Christopher Nolan) --[directed]--> (Inception)
(Inception)         --[released_in]--> (2010)
(Inception)         --[genre]--> (Sci-Fi)
```

These triples collectively allow machines to answer complex queries, infer new facts, and reason over large datasets in a way that flat relational tables cannot easily support.

---

## 2. Key Properties

| Property | Description |
|---|---|
| **Entities** | Real-world objects (people, places, things) represented as nodes |
| **Relations** | Named, typed edges connecting entities |
| **Attributes** | Properties of entities (string, number, date literals) |
| **Schema / Ontology** | Optional formal vocabulary (OWL, RDFS) defining types and constraints |
| **Inference** | New facts derived automatically from existing triples and rules |

---

## 3. Why Knowledge Graphs?

Traditional databases store structured tables but struggle to express multi-hop relationships. Knowledge Graphs solve this by:

- **Linking** data across sources naturally (entity resolution)
- **Reasoning** — e.g. inferring that if A directed B and B stars C, then C worked with A
- **Explainability** — each inferred fact traces back to specific triples
- **Flexibility** — schema-optional, so adding new entity types doesn't break existing data
- **Semantic search** — understanding "movies like Inception" rather than keyword matching

---

## 4. Real-World Examples

| KG | Organisation | Size |
|---|---|---|
| Wikidata | Wikimedia Foundation | ~100M entities |
| Google Knowledge Graph | Google | ~500B facts |
| DBpedia | Open Community | ~4.6M entities |
| YAGO | Max Planck Institute | ~10M entities |
| Freebase (now merged into Wikidata) | Google | — |

---

## 5. Tools for Building Knowledge Graphs

### 5.1 Storage and Query

**RDFLib (Python)**
- Pure Python library for working with RDF triples
- Supports Turtle, N-Triples, JSON-LD serialisation formats
- In-memory store; also connects to SPARQL endpoints
- Best for: small-medium KGs, prototyping, academic use
```bash
pip install rdflib
```

**Apache Jena / Fuseki**
- Java-based full RDF triple store with SPARQL endpoint
- Handles billions of triples
- Best for: production-grade semantic web applications

**Stardog**
- Enterprise graph database with OWL reasoning, SPARQL, property paths
- Used in pharmaceutical and finance industries

**Neo4j**
- Property graph database (not RDF, but widely used for KGs)
- Cypher query language — intuitive for developers
- Best for: connected data, recommendation engines, fraud detection
```bash
pip install neo4j py2neo
```

**Amazon Neptune / Google Spanner Graph**
- Cloud-managed graph databases; both support SPARQL and Gremlin

---

### 5.2 Construction (Entity and Relation Extraction)

**spaCy + spaCy-LLM**
- NLP pipeline to extract entities and relations from free text
- Combined with an LLM backend, can populate a KG from unstructured data

**Stanford OpenIE / Stanza**
- Open information extraction — finds (subject, relation, object) triples in text automatically
- Good baseline before fine-tuning

**Hugging Face Transformers (REBEL model)**
- REBEL is a fine-tuned BART model that directly outputs relation triples from sentences
- State-of-the-art for automated KG construction from text

---

### 5.3 Ontology Modelling

**Protégé (Stanford)**
- Graphical OWL/RDF ontology editor
- Supports class hierarchies, object properties, data properties, restrictions
- Can run built-in reasoners (HermiT, Pellet)
- Free, open-source, widely used in academia

**WebVOWL**
- Browser-based ontology visualiser — renders OWL ontologies as interactive graphs

---

### 5.4 Visualisation

| Tool | Description |
|---|---|
| **NetworkX + Matplotlib** | Python; quick in-notebook visualisation |
| **Gephi** | Desktop app; handles large graphs, community detection |
| **Cytoscape** | Web/desktop; good for biological networks |
| **yEd** | Desktop diagram tool with auto-layout |
| **D3.js** | Web-based; fully custom, interactive |

---

### 5.5 Reasoning and Inference

**HermiT / Pellet (via Protégé)**
- OWL DL reasoners; check consistency and materialise inferred triples

**SPARQL 1.1 Entailment Regimes**
- SPARQL queries can reason over RDFS/OWL subclass and property hierarchies

**PyKeen**
- Python library for Knowledge Graph Embedding (TransE, RotatE, ComplEx)
- Learns vector representations of entities/relations for link prediction

---

## 6. KG Construction Pipeline (General Workflow)

```
Raw Data Sources
  (text, tables, APIs)
        |
        v
  Entity & Relation Extraction
  (NLP: NER, Coreference, RE)
        |
        v
  Entity Disambiguation / Linking
  (map to canonical entities: Wikidata QIDs)
        |
        v
  Triple Store Population
  (RDF, Neo4j, etc.)
        |
        v
  Ontology + Schema Validation
  (OWL / SHACL constraints)
        |
        v
  Inference / Reasoning
  (new facts derived from existing ones)
        |
        v
  Query Interface
  (SPARQL, Cypher, GraphQL)
```

---

## 7. Comparison: RDF vs Property Graphs

| Feature | RDF (Semantic Web) | Property Graphs (Neo4j) |
|---|---|---|
| Data model | Subject–Predicate–Object triples | Nodes + Edges with key-value properties |
| Query language | SPARQL | Cypher / Gremlin |
| Schema | Optional (OWL/RDFS) | Optional (labels) |
| Reasoning | Native OWL/RDFS entailment | Limited, plugin-based |
| Interoperability | High (open standards) | Vendor-specific |
| Ease of use | Steeper learning curve | More developer-friendly |

For most applied AI projects, **Neo4j** (property graph) is faster to prototype with, while **RDFLib/Jena** is preferable when semantic interoperability and OWL reasoning matter.

---

## 8. Code Demo

See `kg_demo.py` — demonstrates building and querying a movie KG using:
- **NetworkX** (no extra setup, runs anywhere)
- **RDFLib** with SPARQL queries and Turtle serialisation

---

## 9. Summary

Knowledge Graphs are a powerful data structure for representing and reasoning over interconnected facts. They are the foundation of search engines (Google's Knowledge Panel), virtual assistants, drug discovery pipelines, fraud detection systems, and recommendation engines. The ecosystem of tools — from Protégé for ontology design to PyKeen for embedding-based link prediction — makes KGs accessible at every scale, from a classroom prototype to an enterprise knowledge base.
