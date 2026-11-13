# About Cala

Cala turns internet chaos into **structured, verified knowledge** that AI agents and LLMs can call as a tool.

Building agentic products means relying on external information, but agents work best with verified, structured, typed data they can call deterministically, not the open web. Cala abstracts away ingestion, normalization, and verification behind a simple API, so you can ship agentic products faster without building brittle data pipelines.

## Why Cala

Web search APIs crawl the open web and return URLs, scraped text, and HTML fragments. Your agent then has to parse, deduplicate, and hope the data is accurate.

Cala is different. It's a **verified entity graph** made of typed entities with structured fields, deterministic queries, and full traceability back to source. Every query returns clean, typed data your agent can reason over immediately.

Web search returns:\
"Here are 10 links about Spanish startups. Good luck parsing them."

Cala returns:

```json theme={null}
[
  { "name": "Luzia", "funding": "13M", "location": "Spain" },
  { "name": "Nomad Solar", "funding": "15M", "location": "Spain" },
  { "name": "Embat", "funding": "21.5M", "location": "Spain" },
...
]
```

## Key capabilities

* **Natural-language answers**: Get succinct, token-optimized answers in markdown — with full source citations and explainability
* **Structured answers**: Get typed, tabular JSON rows ready for programmatic use
* **Flexible input**: Both endpoints accept natural-language questions **and** Cala's query language (dot-notation filters like `OpenAI.founded.year` → `2015`) — the input format is interchangeable; only the output differs
* **Entity discovery**: Find and explore entities across companies, people, products, research papers, laws, places and more
* **Full traceability** — Every answer links back to its source documents, all verified and fact-checked
* **MCP integration** — Connect directly to Cursor, Claude Desktop, VS Code, and any MCP-compatible agent

## Tool Selection Cheat Sheet

| I want to... | Use | Endpoint |
| :- | :- | - |
| Get a succinct, sourced answer in natural language (markdown) | `knowledge_search` | `/v1/knowledge/search` |
| Get a structured, tabular answer (typed JSON rows) | `knowledge_query` | `/v1/knowledge/query` |
| Look up an entity by name | `entity_search` | `/v1/entities` |
| Resolve an entity by identifier (LEI, CIK, SIREN, …) | `entity_lookup` | `/v1/entities/lookup` |
| Retrieve full details for a known entity UUID | `retrieve_entity` | `/v1/entities/{entity_ID}` |

> [!NOTE]
>
> Both `knowledge_search` and `knowledge_query` accept either a natural-language question or a Cala QL expression as input. The only difference is the output format.

## Get started

> [card] [Quickstart](https://docs.cala.ai/quickstart.md)
>
> Get your first results with Cala

> [card] [API Reference](https://docs.cala.ai/api-reference/query.md)
>
> Learn more about the Cala API


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.