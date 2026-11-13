# Natural Language Answer

Returns a **succinct, token-optimized answer in natural-language markdown**, with full explainability, source citations, and extracted entities. Use `knowledge_search` (`POST /v1/knowledge/search`) when you need a human-readable answer rather than raw data.

Input can be a **Cala QL expression** or a **natural-language question** — both produce the same response shape. See the [Structured Answer](https://docs.cala.ai/features/structured-answer.md) page for the full QL syntax reference.

* Automatically identifies and extracts entities from results
* Every claim is traceable back to its source documents

## Example

```json theme={null}
{"input": "What are the most promising climate tech startups in Southern Europe?"}
```

Every response includes four parts:

> [accordion] Answer
>
> A succinct, structured answer in markdown — ready to use directly.
>
> ```markdown theme={null}
> ## Spanish Startups with >€10M Funding
>
> ### Renewable Energy & Deep Tech
>
> **Altano Energy** — Madrid-based, developing renewable energy projects
> across Spain. Secured €60M Series C in 2025 from M&G Investments and Pioneer
> Point Partners.
>
> **BeePlanet Factory** — Navarre-based, manufactures energy storage from
> EV batteries. Raised €5M, building BeeCycle recycling plant with 10,000 tons/year
> capacity by 2026.
>
> **Matteco** — Paterna-based, advanced materials for green hydrogen.
> €16.3M raised.
>
> ### Market Trends
>
> **Spain** leads Southern Europe with 16 cleantech VC deals in Q1 2025.
> **Italy** and **Portugal** emerging as hubs via EU Innovation Fund projects.
> **Cleantech for Iberia** drove a 37% increase in clean tech investment.
> ```

> [accordion] Explainability
>
> Every claim in the answer is traced back to specific source documents — so you know exactly *why* something was said.
>
> ```json theme={null}
> [
>   {
>     "content": "Altano Energy secured a €60 million Series C round in July 2025 from Pioneer Point Partners and M&G Investments.",
>     "references": ["f22a1a96-6234-48d7-95c2-8b049f00fdab"]
>   },
>   {
>     "content": "BeePlanet Factory manufactures energy-storage systems from second-life EV batteries and raised approximately $5.3 million.",
>     "references": ["521038fd-3c36-4fd4-a6e3-9aa2c0be598d"]
>   },
>   {
>     "content": "Spain accounts for the largest share of cleantech VC activity in Southern Europe, recording 16 deals in Q1 2025.",
>     "references": ["27735c7a-f365-48f7-9db4-cf406ce7033e"]
>   }
> ]
> ```
>
> Each `reference` UUID links to a source document in the Sources section below.

> [accordion] Sources
>
> Full provenance for every claim — publisher, article title, and URL. Nothing is a black box.
>
> ```json theme={null}
> [
>   {
>     "id": "f22a1a96-6234-48d7-95c2-8b049f00fdab",
>     "content": "Altano Energy – €60m (Series C, Jul 2025). Develops and operates renewable energy projects across Spain...",
>     "origins": [
>       {
>         "source": {"name": "Impact Loop", "url": "https://www.impactloop.com/"},
>         "document": {
>           "name": "Europe's top 25 climate tech funding rounds this year",
>           "url": "https://www.impactloop.com/artikel/europe-s-25-largest-climate-tech-fundraises-funding-2025-and-the-investors-behind-them"
>         }
>       }
>     ]
>   },
>   {
>     "id": "521038fd-3c36-4fd4-a6e3-9aa2c0be598d",
>     "content": "Matteco: $16.3m raised. Producer of advanced materials for green hydrogen...",
>     "origins": [
>       {
>         "source": {"name": "Seedtable", "url": "https://www.seedtable.com/"},
>         "document": {
>           "name": "11 Best Climate Tech Green Tech Startups in Spain - 2025",
>           "url": "https://www.seedtable.com/best-climate-tech-green-tech-startups-in-spain"
>         }
>       }
>     ]
>   },
>   {
>     "id": "27735c7a-f365-48f7-9db4-cf406ce7033e",
>     "content": "Cleantech VC deals took place in 17 of 27 EU member states in Q1 2025. Germany led with 36 deals, followed by Netherlands and France (20 each), Spain (16)...",
>     "origins": [
>       {
>         "source": {"name": "Cleantech for Europe", "url": "https://www.cleantechforeurope.com/"},
>         "document": {
>           "name": "Cleantech Q1 Briefing 2025",
>           "url": "https://www.cleantechforeurope.com/publications/cleantech-q1-briefing-2025"
>         }
>       }
>     ]
>   }
> ]
> ```

> [accordion] Entities
>
> Every entity mentioned is automatically identified, typed, and assigned a Cala UUID — ready to query further with `retrieve_entity`.
>
> ```json theme={null}
> [
>   {"id": "d6b818c0-1d2c-47ca-a7d3-5b5c35635769", "name": "Altano Energy", "entity_type": "Organization"},
>   {"id": "c455f44f-6cb1-47b9-bf06-3cffac130dc4", "name": "BeePlanet Factory", "entity_type": "Organization"},
>   {"id": "37b9cc58-fd82-4637-a9f9-8409e3e52872", "name": "Matteco", "entity_type": "Organization"},
>   {"id": "a44ea7f1-2ce8-462a-9548-0ab4d85780de", "name": "Spain", "entity_type": "GPE"},
>   {"id": "56eb4d13-69c8-45d6-aae3-ff2147d2c157", "name": "Madrid", "entity_type": "GPE"},
>   {"id": "9ed04484-4df3-47f6-bd77-4e4e50395fa4", "name": "M&G Investments", "entity_type": "Organization"},
>   {"id": "6f6532d5-61e8-4f34-b4fe-15c50c57ce4e", "name": "Pioneer Point Partners", "entity_type": "Organization"},
>   {"id": "5fefdf5c-cf11-4980-8cc2-5f9ece2bf247", "name": "Navarre", "entity_type": "GPE"},
>   {"id": "99dfa2e6-c4ec-4f0e-8501-f35f47d9a764", "name": "BeeCycle", "entity_type": "Facility"},
>   {"id": "214f2f14-00a2-4812-bcf6-c95a7f4fc990", "name": "Barcelona", "entity_type": "GPE"},
>   {"id": "4f1235e7-f38d-44af-bcab-d66f3956c577", "name": "Italy", "entity_type": "GPE"},
>   {"id": "f223b71f-8e67-4493-a4a4-98256f5132f7", "name": "Portugal", "entity_type": "GPE"},
>   {"id": "6fbaeb38-4b5e-4de2-8f89-40494584d38d", "name": "European Union Innovation Fund", "entity_type": "Organization"},
>   {"id": "38132d67-d0a2-4f5f-a1a6-f49f6ba8a293", "name": "Cleantech for Iberia", "entity_type": "Organization"}
> ]
> ```
>
> > [!TIP]
> >
> > Use these UUIDs to get full entity profiles: `POST /v1/entities/d6b818c0-1d2c-47ca-a7d3-5b5c35635769` returns everything Cala knows about Altano Energy.

## Query language input also works

You can also send a plain question — the response shape is identical:

```json theme={null}
{"input": "startups.location=Spain.funding>10M"}
```

## What you get back

| Field | Description |
| - | - |
| `content` | A succinct markdown answer with structured sections |
| `explainability` | Reasoning chain — each claim linked to specific source documents by UUID |
| `context` | Source documents with full provenance: publisher name, article title, URL |
| `entities` | Every entity mentioned, with Cala UUIDs and types (Company, Organization, GPE, Facility, etc.) |


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.