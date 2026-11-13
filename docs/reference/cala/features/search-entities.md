# Search Entities

Search for any entity by name: companies, people, products, places, laws, and more. Fuzzy matching included.

* Allows searching and filtering entities by various criteria
* Returns a list of matching entities with their ID, type, and a short description
* Helps agents find relevant entities in the Cala's Knowledge

## Example:

```json theme={null}
{"name":"Tesla"}
```

> [accordion] Search Results
>
> Returns all matching entities across types — companies, people, products, facilities, and more. Each result includes an `id`, `name`, `entity_type`, and a `description` when available (`null` if not).
>
> ```json theme={null}
> {
>   "entities": [
>     {"id": "2f3cb1a7-b8b8-4ef8-a3ae-b5b274d5601d", "name": "Tesla Motors, Inc.", "entity_type": "Company", "description": "A multinational automotive manufacturer and software, hardware, and financial services provider based in Austin, Texas, with over 130,000 employees."},
>     {"id": "8d6e0b83-7cf0-4fbf-a6f0-653df0c7ee9d", "name": "Tesla Semi", "entity_type": "Product", "description": null},
>     {"id": "5cfa93b1-008e-41ab-8a20-dc112e7fec17", "name": "Nikola Tesla", "entity_type": "Person", "description": "A Serbian who founded Tesla Electric Company."},
>     {"id": "f1c4a574-3e14-4d3c-8f8d-95e6d747670f", "name": "1 Tesla Road", "entity_type": "Facility", "description": null},
>     {"id": "6f9eebde-824f-49b2-8a89-6de8c419fba8", "name": "Tesoro", "entity_type": "Company", "description": "A logistics firm registered in Wilmington, Delaware and headquartered at Ridgewood Parkway in San Antonio, Texas."}
>   ]
> }
> ```
>
> > [!NOTE]
> >
> > One search for "Tesla" returns the company, its products, a historical person, and even a facility — all typed and ready to explore.

> [accordion] Filter by entity type
>
> Narrow results to specific types using the `entity_types` parameter:
>
> ```json theme={null}
> {"name":"Tesla", "entity_types":"Person"}
>
> ```
>
> ```json theme={null}
> {
>   "entities": [
>     {"id": "5cfa93b1-008e-41ab-8a20-dc112e7fec17", "name": "Nikola Tesla", "entity_type": "Person", "description": "A Serbian who founded Tesla Electric Company."}
>   ]
> }
> ```
>
> Available entity types:
>
> | Type | Description | Examples |
> | - | - | - |
> | `GPE` | Geopolitical entities (countries, cities, states) | Spain, San Francisco, Texas |
> | `Company` | Companies & corporations | Tesla, OpenAI, Y Combinator |
> | `CorporateEvent` | Corporate events | Tesla Q4 2024 Earnings Call |
> | `Country` | Sovereign countries | United States, Japan, Brazil |
> | `CountryRegion` | Regions within countries | California, Bavaria, Tuscany |
> | `EducationalInstitution` | Universities & schools | MIT, Stanford University |
> | `Facility` | Facilities & buildings | 1 Tesla Road, Pentagon |
> | `Industry` | Industries & sectors | Automotive, Artificial Intelligence |
> | `Language` | Languages | English, Mandarin |
> | `Law` | Laws & regulations | GDPR, Securities Act of 1933 |
> | `Location` | Regions & geographic areas | Southern Europe, Sahara Desert |
> | `Organization` | Non-company organizations | United Nations, NATO, FIFA |
> | `Person` | People | Nikola Tesla, Sam Altman |
> | `Product` | Products & services | Tesla Semi, GPT-4o |
> | `WorkOfArt` | Creative works | The Great Gatsby, Starry Night |
>
> > [!TIP]
> >
> > You can pass multiple types: `entity_types=Company&entity_types=Person`

> [accordion] Parameters
>
> | Parameter | Type | Required | Description |
> | - | - | - | - |
> | `name` | string | Yes | Entity name to search for |
> | `entity_types` | array | No | Filter by entity type(s) |
> | `limit` | integer | No | Max results (1–100, default 20) |
>
> ```bash theme={null}
> # Get up to 5 Company results for "Tesla"
> curl "https://api.cala.ai/v1/entities?name=Tesla&entity_types=Company&limit=5" \
>   -H "X-API-KEY: YOUR_CALA_API_KEY"
> ```
>
> > [!NOTE]
> >
> > Use the returned entity UUIDs with `POST /v1/entities/{entity_id}` to get full profiles — founders, executives, funding, HQ, and more. If you already have an LEI, CIK, or similar identifier, use [Lookup Entity](https://docs.cala.ai/features/lookup-entity.md) instead of searching by name.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.