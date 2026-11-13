# Build a sourced competitor comparison

> Collect comparable product and pricing facts, retain sources and observation times, and keep interpretation separate from evidence.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/competitor-research.md

Read the recipe and linked API guides, inspect this project's stack, and build the complete flow using its existing conventions.

Build a comparison from a reviewed competitor list using selected product and pricing pages. Collect nullable facts with source URLs and observation times: Scrape parsed fields for known pricing pages, Answers for research tasks. Compare only offers that share currency, unit, billing period, commitment, product variant, market, and conditions. Keep unknown prices distinct from zero, show stale or failed sources, and separate sourced facts from analysis.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Build a comparison that readers can check against the original pages. Start with a reviewed competitor list, collect a consistent set of facts, then compare only compatible plans, units, and markets.

Context.dev provides source discovery, page content, CSS-parsed fields, sourced research answers, and change monitoring. Competitor selection, strategic analysis, and the comparison interface belong to your application.

## Review the comparison scope

Accept a list of product or company URLs, or use [Search](https://docs.context.dev/api-reference/web-scraping/search.md) to propose candidates. Confirm their identities and relevance before adding them to the comparison. A similar name or a search result alone does not establish that two products compete.

Write down the comparison question, geography, and intended product variant. For a pricing comparison, collect both the displayed billing basis and any conditions such as annual commitment, seat minimums, usage tiers, promotions, or taxes.

## Collect a fixed set of facts

Use a server-side key from the [Quickstart](https://docs.context.dev/quickstart.md). Pick the request by how well you know the source page.

| Source | Request |
| - | - |
| A known pricing page with stable markup | [Scrape](https://docs.context.dev/scrape/parse-fields.md) with `formats.parse` and CSS rules, or `formats.markdown` for a page you read yourself |
| A research task, such as what a named plan costs | [Answers](https://docs.context.dev/answers/overview) with a task and an example JSON shape |

Both guides include TypeScript, Python, Ruby, Go, PHP, and cURL examples. See [credits](https://docs.context.dev/account/credits.md) for request pricing.

For a known pricing page, describe the fields as CSS rules. The following body returns the page's Markdown and a `plans` list from one visit:

```json Scrape request body theme={null}
{
  "url": "https://example.comhttps://www.context.dev/pricing",
  "formats": { "markdown": true, "parse": true },
  "sharedParams": { "mainContentOnly": true },
  "parseParams": {
    "rules": {
      "plans": {
        "selector": ".pricing-plan",
        "type": "list",
        "output": {
          "name": "h3",
          "price": ".price",
          "billing_note": ".billing-period"
        }
      }
    }
  },
  "maxAgeMs": 0
}
```

`parsed.data.plans` is an array of objects with string values. A rule that matches nothing returns `null` for an item and `[]` for a list, so a missing price stays unknown. Convert `price` into `amount` and `currency` in your application and keep the original string. `maxAgeMs: 0` forces a fresh capture, so the observation time is the response time. With the default cache window, subtract `cache_metadata.age_ms` instead. Store the final `url`, `request_id`, and the raw `parsed.data` with each row.

When the selectors are unknown or the fact needs interpretation, send a research task. Name the page in `task` so research starts there, and use placeholder values so an unstated field returns `null`:

```json Answers request body theme={null}
{
  "mode": "fast",
  "task": "On https://example.comhttps://www.context.dev/pricing, report the Team plan's displayed price, currency, billing basis, unit, and any stated conditions such as seat minimums or annual commitment. Use null for anything the page does not state.",
  "json_format": {
    "plan": "",
    "amount": 0,
    "currency": "",
    "billing_basis": "",
    "unit": "",
    "conditions": ""
  }
}
```

Name the intended plan in `task` when the page lists several. Use `ultra` when the task spans several pages or asks for a comparison. Store `sources`, the original `json_content` values, `key_metadata.credits_consumed`, and the time the request completed. If you send `timeoutOpts.behavior: "return-partial"`, keep the `partial` marker with the row and review it before accepting.

`sources` lists the pages and search results that contributed, not a citation per field. For a claim that needs an exact source, verify a supporting excerpt on the page and retain that URL with the field. Scrape with `formats.markdown` gives you the page text for that check. Record a blocked page or failed request as a failed attempt, not as a missing price.

## Normalize without hiding commercial differences

Convert the raw result into a reviewed application model. Keep annual commitments and monthly billing in different groups, even when both pages display a monthly equivalent.

```typescript comparison.ts theme={null}
type Offer = {
  id: string;
  company: string;
  plan: string;
  amount: number | null;
  currency: string | null;
  billingBasis: "monthly" | "annual" | "monthly_equivalent_annual_commitment" | null;
  unit: string | null;
  market: string | null;
  variant: string | null;
  conditions: string | null;
  sourceUrl: string;
  observedAt: string;
  status: "current" | "stale" | "failed";
};

export function comparableGroup(offer: Offer): string | null {
  if (offer.status !== "current" || offer.amount === null ||
      !Number.isFinite(offer.amount) || offer.amount < 0 ||
      !offer.currency || !offer.billingBasis || !offer.unit ||
      !offer.market || !offer.variant || !offer.conditions) return null;
  return JSON.stringify([
    offer.currency, offer.billingBasis, offer.unit, offer.market, offer.variant,
    offer.conditions,
  ]);
}

export function comparisonRows(offers: Offer[]) {
  return offers.map((offer) => ({
    company: offer.company,
    plan: offer.plan,
    price: offer.amount === null ? "Unknown" :
      `${offer.amount} ${offer.currency ?? "(currency unknown)"}`,
    billingBasis: offer.billingBasis ?? "Unknown",
    unit: offer.unit ?? "Unknown",
    conditions: offer.conditions ?? "Not established",
    group: comparableGroup(offer),
    sourceUrl: offer.sourceUrl,
    observedAt: offer.observedAt,
    status: offer.status,
  }));
}
```

Assign normalized fields such as `market` and `variant` only after review. The grouping function is conservative: identical keys identify rows eligible for further comparison, not proof that their features or service levels are equivalent. Keep rows without a group visible as incomplete rather than ranking them as the cheapest offer.

If you convert currency, save the exchange-rate source, date, and original amount. If you normalize a package price, retain the package quantity and the conversion rule. A simple comparison can avoid these conversions and show the original prices with their stated basis.

## Separate facts from interpretation

Render a table with the plan, observed price, commercial conditions, source link, observation time, and freshness state. Keep analytical conclusions in a separate section that cites the rows it uses.

| Output | Example treatment |
| - | - |
| Sourced fact | A stated price, with its billing basis and source |
| Missing fact | “Not stated” or “Could not verify,” never zero |
| Interpretation | An explicitly labeled assessment based on selected facts |
| Failed refresh | Last accepted value marked stale, plus the failed attempt |

A generated opinion should not be written back into sourced-fact fields. This workflow also does not supply SEO or GEO visibility metrics, ranking lift, or a validated competitor ranking; those require separate data and analysis.

## Refresh and review changes

Use [Monitors](https://docs.context.dev/monitors/overview) on the reviewed source pages, or schedule fresh Scrape requests with `maxAgeMs: 0`. A detected change can queue a new observation for the affected row. Compare it with the previous snapshot before accepting changes to plan identity, currency, or billing basis.

Store attempts independently from accepted facts, as in the [dataset workflow](https://docs.context.dev/use-cases/structured-web-datasets.md). A timeout must not erase the last known price or be described as a price removal.

Try two compatible offers, one annual-commitment offer, an unstated price, and a failed refresh. Check that only compatible rows share a group, every fact has a source and time, and no interpretation appears as a sourced fact.

> [card] [Structured datasets](https://docs.context.dev/use-cases/structured-web-datasets.md)
>
> Persist observations and refresh records without duplicates.

> [card] [Website change digests](https://docs.context.dev/use-cases/website-change-digests.md)
>
> Turn source changes into a reviewable research feed.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.