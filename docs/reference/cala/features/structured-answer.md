# Structured Answer

Returns **a tabular JSON rows plus matching entities** from Cala's knowledge base. Use `knowledge_query` (`POST /v1/knowledge/query`) when you need structured data ready for programmatic use rather than a natural-language answer.

Input can be a **Cala QL expression** or a **natural-language question** — both produce the same structured response shape.

* Navigate relationships between entities using dot notation
* Filter results by applying conditions directly in the path
* Access nested attributes across multiple entity relationships
* Get structured, typed responses ready for your applications

## Query language syntax

Build queries using dot notation and operators. This syntax works on both `knowledge_query` and `knowledge_search`.

| Operator | Meaning | Example |
| :- | :- | :- |
| `.` | Navigate relationships and access properties | `OpenAI.founded.year` |
| `=` | Filter by Exact match | `startups.location=Spain` |
| `!=` | Exclude | `startups.location!=US` |
| `>` | Greater than | `startups.funding>10M` |
| `<` | Less than | `startups.funding<50M` |
| `>=` | Greater than or equal | `startups.funding>=50M` |
| `<=` | Less than or equal | `startups.funding<=50M` |

Chain filters with dots: `startups.location=Spain.funding>10M.funding<50M`

## Example

Startups in Spain with funding between €10M and €50M:

```json theme={null}
{"input": "startups.location=Spain.funding>10M.funding<50M"}
```

Every response includes two parts:

> [accordion] Structured Results
>
> Typed, filterable data — not paragraphs of text. Each result is a structured object with consistent fields.
>
> ```json theme={null}
> {
>   "results": [
>     {
>       "company": "Amenitiz",
>       "sector": "Hospitality SaaS",
>       "funding_amount": "€38.9M",
>       "round_type": "Series B",
>       "year": 2025
>     },
>     {
>       "company": "H2SITE",
>       "sector": "Hydrogen Energy",
>       "funding_amount": "€36M ($37.2M)",
>       "round_type": "Series B",
>       "year": 2025
>     },
>     {
>       "company": "Fracttal",
>       "sector": "AI Maintenance",
>       "funding_amount": "€29.8M ($35M)",
>       "round_type": "Series B",
>       "year": 2026
>     },
>     {
>       "company": "Heura",
>       "sector": "Plant-based Foods",
>       "funding_amount": "€40M",
>       "round_type": "Total (multiple rounds)",
>       "year": 2023
>     },
>     {
>       "company": "Housfy",
>       "sector": "Real Estate",
>       "funding_amount": "€30M",
>       "round_type": "Series B",
>       "year": 2022
>     },
>     {
>       "company": "Highlight Therapeutics",
>       "sector": "Biotech",
>       "funding_amount": "€37.6M",
>       "round_type": "Venture Round",
>       "year": 2024
>     },
>     {
>       "company": "011h",
>       "sector": "Construction Tech",
>       "funding_amount": "€40.4M",
>       "round_type": "Venture Round",
>       "year": 2024
>     },
>     {
>       "company": "Kreios Space",
>       "sector": "Satellite Tech",
>       "funding_amount": "€10.6M",
>       "round_type": "Seed",
>       "year": 2025
>     },
>     {
>       "company": "Internxt",
>       "sector": "Security/Storage",
>       "funding_amount": "€10.9M",
>       "round_type": "Seed",
>       "year": 2020
>     },
>     {
>       "company": "Nomad Solar Energy",
>       "sector": "Solar Energy",
>       "funding_amount": "€15M",
>       "round_type": null,
>       "year": null
>     },
>     {
>       "company": "Universal DX",
>       "sector": "Healthcare",
>       "funding_amount": "€20M",
>       "round_type": null,
>       "year": null
>     },
>     {
>       "company": "Maisa AI",
>       "sector": "AI",
>       "funding_amount": "€30M",
>       "round_type": null,
>       "year": null
>     },
>     {
>       "company": "Reveni",
>       "sector": null,
>       "funding_amount": "€17.3M",
>       "round_type": null,
>       "year": null
>     }
>   ]
> }
> ```
>
> > [!NOTE]
> >
> > 13 startups returned — each with company name, sector, funding amount, round type, and year. This is structured data, not text to parse.

> [accordion] Entities
>
> Every company in the results is automatically linked to a Cala entity with a unique UUID and type.
>
> ```json theme={null}
> {
>   "entities": [
>     {"id": "e2ce8098-dea6-4fdd-b226-c33923b5efe1", "name": "Amenitiz", "entity_type": "Company"},
>     {"id": "b2171d05-18d4-4b1b-8953-208ce66be8d6", "name": "H2SITE", "entity_type": "Company"},
>     {"id": "714be9ad-cce1-46e5-b0d5-a01f71f26d01", "name": "Fracttal", "entity_type": "Company"},
>     {"id": "3d47d7b1-8f83-4be3-be42-b9d8712c1d4c", "name": "Heura", "entity_type": "Company"},
>     {"id": "3349e982-694e-4923-9af7-480af3efcedc", "name": "Housfy", "entity_type": "Company"},
>     {"id": "b5c7a256-79b6-43d9-84fb-24c4403cc098", "name": "Highlight Therapeutics", "entity_type": "Company"},
>     {"id": "63a254cb-40bc-49a2-9922-7ae806398c38", "name": "011h", "entity_type": "Company"},
>     {"id": "73f3603f-624e-457a-b5ad-f192792cc15b", "name": "Kreios Space", "entity_type": "Company"},
>     {"id": "9beb50ad-d4dc-4ef8-bd59-7a26bbcbb413", "name": "Internxt", "entity_type": "Company"},
>     {"id": "877fc47b-b23a-4cc9-b929-50d2a629fd38", "name": "Nomad Solar Energy", "entity_type": "Company"},
>     {"id": "fd163be0-ab87-4218-b0a6-48a5cc46c711", "name": "Universal DX", "entity_type": "Company"},
>     {"id": "42285452-6100-473b-a8bb-85c731e3e1e5", "name": "Maisa AI", "entity_type": "Company"},
>     {"id": "ff47dfd6-97de-401a-82ae-edc3adf35694", "name": "Reveni", "entity_type": "Company"}
>   ]
> }
> ```
>
> > [!TIP]
> >
> > Use any entity UUID to get the full profile: `POST /v1/entities/e2ce8098-dea6-4fdd-b226-c33923b5efe1` returns everything Cala knows about Amenitiz — founders, executives, HQ, employee count, and more.

## Natural-language input also works

You can also send a plain question — the response is still structured rows, not prose:

```json theme={null}
{"input": "What are the most promising climate tech startups in Southern Europe?"}
```

## More query examples

These use the Cala QL syntax. Natural-language questions also work with this endpoint.

```json theme={null}
{"input": "OpenAI.founded.year"}
{"input": "ibex35.companies.employee_count>2000"}
{"input": "companies.founder.incorporation>2020.previous_job=Google"}
```


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.