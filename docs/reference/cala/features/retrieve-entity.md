# Retrieve Entity

The retrieve entity endpoint gives your agent comprehensive access to all the information we know about a specific entity. This endpoint:

* Delivers structured, schema-validated data about any entity
* Provides complete entity profiles with all available attributes or requested entity properties and relationships
* Ensures data consistency through proper schema validation

Once you have an entity UUID (from `entity_search`, `entity_lookup`, `knowledge_search`, or `knowledge_query`), retrieve everything Cala knows about it:

## Example:

`POST /entities/c6772802-bdbc-4778-91e9-cd3d27d008d5`

or if you want to query only some of the entity properties add a request body with the desired entity fields:

```json theme={null}
{"properties": ["name", "cik", "lei"]}
```

> [accordion] Full Entity Profile
>
> A complete, structured profile — founders, executives, HQ, industry, employee count, and more. No parsing needed.
>
> ```json theme={null}
> {
>     "properties": {
>         "id": {
>             "value": "c6772802-bdbc-4778-91e9-cd3d27d008d5",
>             "sources": []
>         },
>         "name": {
>             "value": "APPLE INC",
>             "sources": [
>                 {
>                     "name": "SEC",
>                     "document": {
>                         "endpoint": "https://efts.sec.gov/LATEST/search-index?q=%22APPLE+INC%22",
>                         "params": {},
>                         "response_hash": "3f0354a291ad77088d55bd2577294a85d5ba3c1b9ae0aa5a58c53bb24ed49111"
>                     },
>                     "date": "2026-02-26"
>                 }
>             ]
>         },
>         "aliases": {
>             "value": [
>                 "Apple Computer, Inc."
>             ],
>             "sources": []
>         },
>         "registered_address": {
>             "value": "C/O C T Corporation System, 330 N. Brand Blvd, Suite 700, Glendale, US-CA, 91203, US",
>             "sources": [
>                 {
>                     "name": "GLEIF",
>                     "document": {
>                         "endpoint": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=APPLE+INC&page%5Bsize%5D=20",
>                         "params": {},
>                         "response_hash": "7089723cc94015908b284e2637d34fca0d700bccca36b0f83e4fb6e93c211437"
>                     },
>                     "date": "2026-02-26"
>                 }
>             ]
>         },
>         "headquarters_address": {
>             "value": "One Apple Park Way, Cupertino, US-CA, 95014, US",
>             "sources": [
>                 {
>                     "name": "GLEIF",
>                     "document": {
>                         "endpoint": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=APPLE+INC&page%5Bsize%5D=20",
>                         "params": {},
>                         "response_hash": "7089723cc94015908b284e2637d34fca0d700bccca36b0f83e4fb6e93c211437"
>                     },
>                     "date": "2026-02-26"
>                 }
>             ]
>         },
>         "cik": {
>             "value": "0000320193",
>             "sources": [
>                 {
>                     "name": "SEC",
>                     "document": {
>                         "endpoint": "https://efts.sec.gov/LATEST/search-index?q=%22APPLE+INC%22",
>                         "params": {},
>                         "response_hash": "3f0354a291ad77088d55bd2577294a85d5ba3c1b9ae0aa5a58c53bb24ed49111"
>                     },
>                     "date": "2026-02-26"
>                 }
>             ]
>         },
>         "lei": {
>             "value": "HWUPKR0MPOU8FGXBT394",
>             "sources": [
>                 {
>                     "name": "GLEIF",
>                     "document": {
>                         "endpoint": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=APPLE+INC&page%5Bsize%5D=20",
>                         "params": {},
>                         "response_hash": "7089723cc94015908b284e2637d34fca0d700bccca36b0f83e4fb6e93c211437"
>                     },
>                     "date": "2026-02-26"
>                 }
>             ]
>         },
>         "bics": {
>             "value": [
>                 "APLEUS66XXX"
>             ],
>             "sources": []
>         },
>         "legal_name": {
>             "value": "Apple Inc.",
>             "sources": [
>                 {
>                     "name": "GLEIF",
>                     "document": {
>                         "endpoint": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=APPLE+INC&page%5Bsize%5D=20",
>                         "params": {},
>                         "response_hash": "7089723cc94015908b284e2637d34fca0d700bccca36b0f83e4fb6e93c211437"
>                     },
>                     "date": "2026-02-26"
>                 }
>             ]
>         }
>     },
>     "relationships": {
>         "outgoing": {},
>         "incoming": {}
>     },
>     "numerical_observations": []
> }
> ```

> [accordion] How to find an entity ID
>
> Use `entity_search` to look up any entity by name (for example "Apple")
>
> ```json theme={null}
> {
>   "entities": [
>     {"id": "c6772802-bdbc-4778-91e9-cd3d27d008d5", "name": "APPLE INC", "entity_type": "Company", "description": "Founded in 1976, this Cupertino‑based firm with 164,000 employees is the direct parent of Apple Operations India, Apple Canada, and others, and current CEO is Tim Cook."},
>     {"id": "ccee8487-8170-4ee7-81d5-cb1f9a7dc1a7", "name": "Apple Intelligence", "entity_type": "Product", "description": null},
>     {"id": "051a574e-cac7-4ff1-bb1a-20ef410b2a0b", "name": "Apple Korea Limited", "entity_type": "Company", "description": "A Korean subsidiary of Apple Inc."},
>     {"id": "4dce2f0b-87b3-4a9a-b70f-6f14e67f463b", "name": "APPLE CANADA INC.", "entity_type": "Company", "description": "A Canadian company located at 120 Bremner Boulevard, Toronto, that operates as a subsidiary of Apple Inc."}
>   ]
> }
> ```
>
> > [!TIP]
> >
> > Fuzzy matching included — searching "Apple" also returns related products, subsidiaries, and legal entities.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.