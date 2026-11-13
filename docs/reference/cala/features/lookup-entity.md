# Lookup Entity

Resolve a company by an external identifier. Exact match, not fuzzy name search.

`POST /v1/entities/lookup` accepts **exactly one** of these identifier schemes:

| Scheme | Meaning |
| - | - |
| `lei` | Legal Entity Identifier |
| `cik` | SEC Central Index Key |
| `rssd_id` | Federal Reserve RSSD ID |
| `companies_house_uk_company_number` | UK Companies House number |
| `siren` | French SIREN |

* Takes one identifier scheme and value
* Returns a single entity stub (`id`, `name`, `entity_type`, `description`)
* Use the returned `id` with Retrieve Entity / Entity Introspection for a full profile

## Example:

```json theme={null}
{"id": {"lei": "95980020140005017502"}}
```

Or as a top-level shorthand:

```json theme={null}
{"lei": "95980020140005017502"}
```

> [accordion] Lookup result
>
> One matching entity stub. Feed the `id` into Retrieve Entity for properties, relationships, and numerical observations.
>
> ```json theme={null}
> {
>   "id": "d1715183-1d00-42c9-81c3-be3da24cdcf2",
>   "name": "MANGO MNG S.A.",
>   "entity_type": "Company",
>   "description": "Spanish fashion retailer headquartered in Palau-solità i Plegamans, Barcelona, founded in 1989."
> }
> ```
>
> > [!NOTE]
> >
> > Lookup is exact: the identifier must match the value stored in the Knowledge Graph (whitespace is stripped; LEI is uppercased; CIK is zero-padded to 10 digits).

> [accordion] Request example
>
> ```bash theme={null}
> curl -X POST "https://api.cala.ai/v1/entities/lookup" \
>   -H "X-API-KEY: YOUR_CALA_API_KEY" \
>   -H "Content-Type: application/json" \
>   -d '{"lei": "95980020140005017502"}'
> ```
>
> > [!NOTE]
> >
> > Unknown identifiers return **404**. Unknown schemes return **422**.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.