# Company and funding data in Cala — field guide

Shared by the Cala team for the "Make Unicorns Real" track on 2026-11-14. Verbatim; tables
converted to Markdown. Summary for agents: `docs/agents/cala.md`.

This guide lists the company, funding and ecosystem data you can query in Cala: company profiles, headcount and revenue over time, funding rounds and their investors, people, acquisitions, and events such as Slush 2026.

Each company returns the fields that apply to it. A bootstrapped company has no funding rounds, a company that never acquired anyone has no acquisitions, and a young startup may not have published revenue. When a field does not apply to a company, Cala does not return it. Where a source confirms a zero (for example a company stating it has never raised), you'll see it as a sourced 0.

## How to query

Cala is available through its MCP server (https://api.cala.ai/mcp/, authenticated with your API key in the X-API-KEY header) and its API. For this challenge, we recommend the entity endpoints below: they give you every field in this guide, with its sources, and let you follow the connections between companies, rounds, investors, people and events.

| Tool | Use it to |
| --- | --- |
| entity_search | Find a company, person, investor or event by name (fuzzy). Filter with entity_types, e.g. ["Company"] or ["Event"]. |
| entity_lookup | Find a company by an identifier: LEI, SEC CIK, UK Companies House number, SIREN or RSSD ID. |
| entity_introspection | See which properties, relationships and time series this particular entity has. |
| entity_retrieval | Get the values: name the properties, relationships and numerical_observations you want. |

Recommended flow:

1. Find the entity with entity_search or entity_lookup.
2. Run entity_introspection on its id to see exactly what you can retrieve.
3. Call entity_retrieval, asking only for the fields you need.
4. Repeat on linked entities, such as a funding round or an investor, to go deeper.

## What a value looks like

Every property comes back as a value plus the sources it was read from:

```json
"legal_name": {
  "value": "Aiven Oy",
  "sources": [
    { "name": "tietopalvelu.ytj.fi", "document": "https://tietopalvelu.ytj.fi/yritys/2795743-5",
      "date": "2026-10-15", "date_precision": "day", "source_rank": "FILING" }
  ]
}
```

- document is the source URL.
- date is the publication or retrieval date. date_precision tells you whether it is exact (day) or approximate (month, year). For example, a founding date of 2019-01-01 with year precision means "2019".
- source_rank tells you what kind of source it is:
  - FILING: business registries, regulators and official filings (SEC, Companies House, national registries, GLEIF).
  - PRIMARY: the company itself, or its investors, lenders or grant bodies.
  - PRESS: independent publications.
  - AGGREGATOR: funding databases, data providers and archives.

Relationships (founders, investors, rounds…) return the linked entity's id, name and entity_type. They carry their own sources and, where relevant, extra fields such as role, is_lead, valid_since, valid_until or event_date.

Time series (headcount, revenue, financial statements) come back as a list of dated observations, each with the value, the date it refers to, and its origin (source name and URL).

## Company

Entity type Company.

### Properties

| Field | What it holds |
| --- | --- |
| name | Brand or trading name. |
| legal_name | Registered name of the legal entity, often straight from a business registry. |
| aliases | Other names the company is known by: brands, former names. |
| website | The company's domain. |
| description | What the company does. |
| founding_date | Incorporation or founding date. Check date_precision. |
| headquarters_address | Operating headquarters, as precise as its sources state it: from a city to a full street address. |
| registered_address | Registered office, for companies where it differs from the headquarters. |
| operational_status | Whether the company is operating, e.g. ACTIVE. |
| company_ownership_status | The company's ownership or legal status as its source states it, e.g. Merged or acquired, or a registry's legal form such as Private Limited Company. |
| employee_count_range | Headcount as a single figure or a band, e.g. [90] or [51, 200], with its source. |
| total_funding | Cumulative funding as reported, all instruments. The currency is in total_funding_units. |
| total_funding_excluding_debt | Total funding minus loan facilities. The currency is in total_funding_excluding_debt_units. |
| funding_stage | The company's current stage in round terms, e.g. PRE_SEED, SEED, SERIES_A, SERIES_B… |
| companies_house_uk_company_number | For UK companies, the Companies House registration number. |

### Time series

| Series | What it holds |
| --- | --- |
| ObservableProperty "Number of employees" (code employee_count) | Headcount over time: one dated observation per source, from company pages, press, registries' annual accounts and data providers. |
| FinancialMetric "Annual recurring revenue" | ARR figures over time, each dated and sourced, for companies that have published them. |
| FinancialMetric financial statement lines | For UK companies filing accounts at Companies House: cash, current assets, creditors, net assets, equity, average number of employees and more, by year. |

Request a series through numerical_observations in entity_retrieval, using the id that entity_introspection returns for it.

### Relationships

| Relationship | Direction | What it links |
| --- | --- | --- |
| HAS_DOMAIN_NAME | outgoing | The company's domains, each with a status (ACTIVE or INACTIVE) and valid_since. A company that moved domain shows both. |
| HAS_HEADQUARTERS_IN | outgoing | The place of the headquarters. |
| IS_REGISTERED_IN | outgoing | The jurisdiction the company is registered in. |
| OPERATES_IN_INDUSTRY | outgoing | Industry: a broad code (e.g. SOFTWARE_AND_SERVICES) plus the source's own label. |
| FOUNDED | incoming | Founders (Person), with valid_since. |
| IS_CEO_OF, IS_CTO_OF, IS_VICEPRESIDENT_OF | incoming | Executives, with valid_since and, for people who have left the role, valid_until. |
| IS_BOARD_MEMBER_OF | incoming | Directors, often from regulatory filings. |
| WORKS_AT | incoming | Other people at the company, with their role. |
| IS_BENEFICIARY_OWNER_OF, IS_CONTROL_PERSON_OF | incoming | For UK companies, beneficial owners and persons with significant control from Companies House. |
| INVESTED_IN | incoming | Investors in the company (organisations and people), across all rounds. |
| PARTICIPATES_IN_FUNDING_ROUND | outgoing | The company's funding rounds (see below). |
| PARTICIPATES_IN_CORPORATE_EVENT | outgoing | Acquisitions and financing events (see below). |
| PARTICIPATES_IN_EVENT | outgoing | Events the company takes part in, such as Slush 2026 (see below). |

## Funding rounds

Entity type FundingRound, one per round. You reach a round from the company through PARTICIPATES_IN_FUNDING_ROUND.

The relationship's role tells you the company's side of the round: ISSUER for rounds the company raised, INVESTOR or LENDER for rounds where the company invested in or lent to someone else. To list the money a company raised, keep the ISSUER rounds.

### Properties

| Field | What it holds |
| --- | --- |
| name | The round's name, e.g. Seed, Series B, Venture Debt, Grant; Funding round or Equity round for financings that no source names. |
| round_label | The round's label as a code, e.g. SEED, SERIES_A. |
| instrument | Type of financing, e.g. EQUITY. |
| transaction_value | Amount raised. The currency is in transaction_value_units. |
| announcement_date | First public report of the round. |
| event_date | When the round took place (first sale, signing or first close). Check event_date__precision. |

Round names cover the full financing ladder, e.g. Pre-Seed, Seed, Seed+, Angel, Series A to E, Venture Debt, Debt Financing and Grant.

### Participants

The round's incoming PARTICIPATES_IN_FUNDING_ROUND links list the issuing company and every participant, each with its role (INVESTOR for equity, LENDER for debt) and an is_lead flag marking the round's lead investors.

### Financing events

Financings reported in regulatory filings, such as SEC Form D, also appear as PrivateCompanyFundingRound events (name FINANCING_RAISED_OR_FACILITY_ENTERED), linked through PARTICIPATES_IN_CORPORATE_EVENT. These hold an event_date, transaction_value, round_type (e.g. Series B, Debt) and a description; filings record the offering but not the investors.

One financing can be recorded both as a FundingRound (from announcements) and as a financing event (from filings). Match them by date and amount before you add them up.

## Acquisitions

Entity type CorporateEvent, linked through PARTICIPATES_IN_CORPORATE_EVENT. The event's name tells you what happened (e.g. MNA_COMPLETED, MATERIAL_AGREEMENT_ANNOUNCED), the relationship's role tells you the company's side (e.g. ACQUIRER), and event_date tells you when.

## Example: startups attending Slush 2026

Events are entities too, so you can start from an event and reach every company linked to it. For example, the companies attending Slush 2026 are linked to the Slush 2026 event entity:

1. Find the event with entity_search (name Slush 2026, entity_types: ["Event"]). Its id is bc844d56-6ab4-452b-96bf-2661e86e592b.
2. Retrieve its incoming PARTICIPATES_IN_EVENT relationships to get the companies attending, each with the role ATTENDEE:

   ```json
   { "entity_id": "bc844d56-6ab4-452b-96bf-2661e86e592b",
     "relationships": { "incoming": { "PARTICIPATES_IN_EVENT": { "limit": 100 } } } }
   ```

3. Retrieve any of those companies to see its funding rounds, investors, founders and headcount.

From there you could, for instance, find which Slush startups raised in the last year and who led their rounds. Attendees include startups as well as investors and established companies, so a company's profile (founding date, funding stage, headcount) helps you focus on the ones you need.

## What to expect

- Fields that apply. Each company carries the fields relevant to its history: rounds, events and metrics appear where they happened and were made public.
- Brand and legal names. Companies are recorded under their legal name, with brands as names or aliases. For example, Cameo is "Baron App, Inc.". You can search by brand or legal name, or use entity_lookup with an identifier.
- Legal entities are modelled individually. A brand and its legal entity, or a group and its national subsidiaries, can each be a separate Company entity. Use website to pick the one you need.
