# Datasets and comparisons

> Collect structured web observations, preserve history, and compare verified facts.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/structured-web-datasets.md

Read the recipe and linked API guides, inspect this project's stack, and build the flow using its existing conventions.

Build a resumable web dataset and a reviewed comparison view. Preserve stable IDs and previous accepted values, store observation evidence, keep unknown prices unknown, and separate incompatible currencies, billing periods, and plan variants.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Use stable application IDs to collect changing web data, then compare only records whose commercial terms match. Store accepted values separately from failed attempts and unresolved observations.

## Discover and checkpoint sources

Use [Map URLs](https://docs.context.dev/map/overview) with `urlRegex` to select a section, or a [scoped crawl](https://docs.context.dev/crawl/scope.md) to follow its links. Review the resulting URL list before ingestion and persist it so a retry does not start discovery over.

For each source, keep an application ID, original URL, current URL, last successful observation, and next retry time. Do not use a mutable title as an identity key.

## Collect and retain observations

| Dataset requirement | Request |
| - | - |
| Deterministic fields from pages with stable markup | [Scrape](https://docs.context.dev/scrape/parse-fields.md) with `formats.parse` and CSS rules in `parseParams.rules` |
| Page text for review, or for your own parser | Scrape with `formats.markdown`, in the same request or alone |
| Large collection of raw Markdown or HTML | [Batch](https://docs.context.dev/batches/overview), followed by your processing pipeline |

Parsed fields are deterministic. A rule that matches nothing returns `null` for an item and `[]` for a list, so a missing value stays unknown instead of being guessed. Values are strings; convert numbers in your application and keep the original text. Rules run on the rendered HTML after `sharedParams.mainContentOnly`, `includeSelectors`, and `excludeSelectors`, so leave those filters off unless every selector targets content they keep.

The worker below sends this body for each source, requesting the parsed fields and the page Markdown from one visit.

```json Scrape request body theme={null}
{
  "url": "https://academy.example.com/courses/intro-python",
  "formats": { "parse": true, "markdown": true },
  "parseParams": {
    "rules": {
      "title": "h1",
      "instructor": ".course-instructor",
      "level": ".course-level",
      "price": { "selector": "[itemprop=price]", "output": "@content" },
      "currency": { "selector": "[itemprop=priceCurrency]", "output": "@content" },
      "topics": { "selector": ".syllabus li", "type": "list" }
    }
  },
  "maxAgeMs": 0
}
```

See the [Scrape guide](https://docs.context.dev/scrape/parse-fields.md) for this request in every SDK. Run the Python application below with `CONTEXT_DEV_API_KEY` set on the server.

## Store records separately from attempts

Keep three kinds of state: the source queue, the latest accepted record, and historical observations. The SQLite worker commits each source independently, so a failure on one page cannot delete another page's data.

```python catalog.py theme={null}
import json
import math
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

RULES = {
    "title": "h1",
    "instructor": ".course-instructor",
    "level": ".course-level",
    "price": {"selector": "[itemprop=price]", "output": "@content"},
    "currency": {"selector": "[itemprop=priceCurrency]", "output": "@content"},
    "topics": {"selector": ".syllabus li", "type": "list"},
}

def validate_record(parsed):
    # Every rule name is present: missing items are None and missing lists are [].
    if not isinstance(parsed, dict) or set(parsed) != set(RULES):
        raise ValueError("Unexpected record shape")
    for key in ("title", "instructor", "level", "price", "currency"):
        if parsed[key] is not None and not isinstance(parsed[key], str):
            raise ValueError(f"Invalid {key}")
    if not isinstance(parsed["topics"], list) or not all(isinstance(topic, str) for topic in parsed["topics"]):
        raise ValueError("Invalid topics")
    if not parsed["title"] or not parsed["title"].strip():
        raise ValueError("No usable record identity")
    record = {key: parsed[key] for key in ("title", "instructor", "level", "topics")}
    record["price_text"] = parsed["price"]
    record["price_amount"] = None
    if parsed["price"] is not None:
        try:
            amount = float(parsed["price"])
        except ValueError:
            raise ValueError("Price needs review") from None
        if not math.isfinite(amount) or amount < 0:
            raise ValueError("Invalid price")
        record["price_amount"] = amount
    record["currency"] = None
    if parsed["currency"] is not None:
        currency = parsed["currency"].strip().upper()
        if len(currency) != 3 or not currency.isascii() or not currency.isalpha():
            raise ValueError("Currency needs review")
        record["currency"] = currency
    return record

def open_catalog(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript("""
      CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY, url TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
        attempts INTEGER NOT NULL DEFAULT 0, next_attempt_at REAL NOT NULL DEFAULT 0,
        error TEXT, last_success_at TEXT
      );
      CREATE TABLE IF NOT EXISTS records (
        id TEXT PRIMARY KEY, source_url TEXT NOT NULL, final_url TEXT NOT NULL,
        observed_at TEXT NOT NULL, data_json TEXT NOT NULL, request_id TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS observations (
        id TEXT NOT NULL, observed_at TEXT NOT NULL, source_url TEXT NOT NULL,
        final_url TEXT NOT NULL, request_id TEXT NOT NULL,
        parsed_json TEXT NOT NULL, markdown TEXT,
        PRIMARY KEY (id, observed_at)
      );
    """)
    return db

def enqueue(db, items, refresh=False):
    with db:
        for item in items:
            url = urlsplit(item["url"])
            if url.scheme != "https" or not url.hostname or url.username or url.password:
                raise ValueError("Use reviewed HTTPS source URLs")
            db.execute("""
              INSERT INTO sources (id, url) VALUES (?, ?)
              ON CONFLICT(id) DO UPDATE SET
                status=CASE WHEN url <> excluded.url THEN 'pending' ELSE status END,
                attempts=CASE WHEN url <> excluded.url THEN 0 ELSE attempts END,
                next_attempt_at=CASE WHEN url <> excluded.url THEN 0 ELSE next_attempt_at END,
                url=excluded.url
            """, (item["id"], item["url"]))
            if refresh:
                db.execute("UPDATE sources SET status='pending', attempts=0, next_attempt_at=0, error=NULL WHERE id=?", (item["id"],))

def scrape_page(url):
    request = Request(
        "https://api.context.dev/v1/web/scrape",
        data=json.dumps({
            "url": url,
            "formats": {"parse": True, "markdown": True},
            "parseParams": {"rules": RULES},
            "maxAgeMs": 0,
        }).encode(),
        headers={"Authorization": f"Bearer {os.environ['CONTEXT_DEV_API_KEY']}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=120) as response:
        return json.load(response)

def retry_delay(headers):
    value = headers.get("Retry-After")
    try:
        return max(0, float(value))
    except (TypeError, ValueError):
        try:
            return max(0, parsedate_to_datetime(value).timestamp() - time.time())
        except (TypeError, ValueError, AttributeError):
            return 30

def run_pending(db):
    jobs = db.execute("""
      SELECT * FROM sources WHERE status IN ('pending', 'retryable')
      AND attempts < 3 AND next_attempt_at <= ?
    """, (time.time(),)).fetchall()
    for job in jobs:
        with db:
            db.execute("UPDATE sources SET attempts=attempts+1 WHERE id=?", (job["id"],))
        try:
            result = scrape_page(job["url"])
            data = validate_record(result["parsed"]["data"])
            final_url, markdown = result["url"], result["markdown"]["data"]
            if urlsplit(final_url).hostname != urlsplit(job["url"]).hostname:
                raise ValueError("Final URL is on another host")
            observed = datetime.now(timezone.utc).isoformat()
            with db:
                db.execute("INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (job["id"], observed, job["url"], final_url, result["request_id"],
                     json.dumps(result["parsed"]["data"]), markdown))
                db.execute("""
                  INSERT INTO records VALUES (?, ?, ?, ?, ?, ?)
                  ON CONFLICT(id) DO UPDATE SET source_url=excluded.source_url,
                    final_url=excluded.final_url, observed_at=excluded.observed_at,
                    data_json=excluded.data_json, request_id=excluded.request_id
                """, (job["id"], job["url"], final_url, observed, json.dumps(data), result["request_id"]))
                db.execute("UPDATE sources SET status='ready', error=NULL, last_success_at=? WHERE id=?", (observed, job["id"]))
        except HTTPError as error:
            retryable = error.code in (408, 429) or error.code >= 500
            delay = retry_delay(error.headers)
            error.close()
            with db:
                db.execute("UPDATE sources SET status=?, error=?, next_attempt_at=? WHERE id=?",
                    ("retryable" if retryable else "error", f"HTTP {error.code}",
                     time.time() + delay, job["id"]))
            if error.code in (401, 402, 403, 429):
                break
        except (URLError, TimeoutError):
            with db:
                db.execute("UPDATE sources SET status='retryable', error='Network failure', next_attempt_at=? WHERE id=?", (time.time() + 30, job["id"]))
        except (ValueError, KeyError, TypeError) as error:
            with db:
                db.execute("UPDATE sources SET status='review', error=? WHERE id=?", (str(error), job["id"]))

if __name__ == "__main__":
    with open(sys.argv[1]) as source_file:
        manifest = json.load(source_file)
    db = open_catalog("catalog.sqlite")
    enqueue(db, manifest, refresh="--refresh" in sys.argv[2:])
    run_pending(db)
    for row in db.execute("SELECT status, count(*) AS count FROM sources GROUP BY status"):
        print(dict(row))
    db.close()
```

```bash Run the worker theme={null}
python3 catalog.py sources.json
python3 catalog.py sources.json --refresh
```

The first command resumes pending or eligible retryable items and skips completed ones. The second starts a new observation cycle for the listed sources. Because the application IDs are stable, a changed price updates the current record instead of creating a duplicate course. Each accepted refresh also records an observation for history.

The worker retries `408`, `429`, and `5xx` responses after the `Retry-After` delay, and stops the run on `401`, `402`, `403`, and `429`. A `400 WEBSITE_BLOCKED` becomes an error; `parsed.success: false` or an unexpected parsed shape goes to review without replacing the accepted record. A record with an unexpected shape, a price that cannot be parsed, or a final URL on another host goes to `review` and leaves the last accepted record in place.

This is a single-worker example. Use queue leases or transactional job claiming before running multiple workers. Schedule retries after `next_attempt_at`; do not repeatedly restart after an authentication or account-limit error. Review exhausted retries and invalid records explicitly.

## Compare facts on compatible terms

For a research question spanning several pages, send this body to [Answers](https://docs.context.dev/answers/overview), then keep its source URLs and the time of the observation:

```json Answers request body theme={null}
{
  "mode": "fast",
  "task": "On https://example.com/pricing, report the Team plan's displayed price, currency, billing basis, unit, and any stated conditions such as seat minimums or annual commitment. Use null for anything the page does not state.",
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

Keep missing prices as `null`. Do not compare a monthly commitment with an annual promotion, or prices in different currencies, as though they were interchangeable:

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

Name the intended plan or product variant in the research task. Inspect the source for currency, billing period, tax treatment, minimum seats, usage tiers, and promotional conditions. A source URL identifies a page, not a field-level citation; retain the supporting excerpt for claims that need review.

## Reconcile changes

Refresh observations under their existing application IDs. Keep the last accepted values after errors or ambiguous extraction, and distinguish unknown values from confirmed changes. Promote a new observation only after schema and source checks pass.

Re-run discovery periodically to find added and removed URLs. A page missing from an incomplete index or crawl is not proof that the item disappeared. For notifications, feed accepted changes into a [digest](https://docs.context.dev/use-cases/website-change-digests.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.