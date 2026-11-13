# Turn website changes into a useful digest

> Monitor a reviewed watchlist, deduplicate signed events, and build a source-linked digest that also exposes failed checks.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/website-change-digests.md

Read the recipe and linked API guides, inspect this project's stack, and build the complete flow using its existing conventions.

Build a reviewed watchlist with meaningful monitor targets and supported schedules. Store monitor IDs and secrets, verify webhook signatures against raw request bytes, and save events durably before processing. Deduplicate event and change IDs, build source-linked digests, and reconcile missed deliveries through paginated runs and changes. Show failed checks separately from successful checks with no changes.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Track relevant changes to careers, pricing, product, or company pages and turn them into a digest. Context.dev detects changes; your application saves events, decides what belongs in the digest, and handles notification delivery.

[Adapt uses Context.dev to monitor websites](https://www.context.dev/blog/adapt-puts-20k-accounts-and-6000-websites-to-work-with-context-dev). This recipe connects Monitors to a durable event store, with polling to recover missed deliveries and expose failed checks.

## Define what matters on each source

Create a watchlist with an application ID, source URL, owner, and description of the relevant change. Choose the target by the question you want to answer:

| Question | Target and detection |
| - | - |
| Did any visible text change? | `page` with `exact` |
| Did this page announce a relevant change? | `page` with `semantic` and specific instructions |
| Were matching URLs added or removed? | `sitemap` with `exact` |
| Did a structured fact change? | `extract` with `semantic` |
| Did the web publish something new about a topic? | [`search`](https://docs.context.dev/monitors/targets/search) with `semantic` and specific instructions |

Use the [monitoring guide](https://docs.context.dev/monitors/overview#create-a-monitor) for cURL and SDK requests. For example, send this body to `POST /monitors`, replacing the source and webhook URL:

```json Monitor request body theme={null}
{
  "name": "Example careers updates",
  "target": {
    "type": "page",
    "url": "https://example.com/careers",
    "instructions": "Report newly listed or removed engineering jobs. Ignore navigation, copyright years, and unrelated copy edits."
  },
  "change_detection": { "type": "semantic", "confidence_threshold": 0.8 },
  "schedule": { "type": "interval", "frequency": 6, "unit": "hours" },
  "webhook": {
    "url": "https://app.example.com/hooks/context/watch-123",
    "events": ["change.detected", "run.completed"],
    "retry": {}
  }
}
```

The interval must be at least 10 minutes. Save the returned monitor `id`, `initial_run_id`, and generated webhook secret with your watchlist record. Store the secret securely. The first run establishes a baseline; it is not a new-change alert.

## Verify and persist before acknowledging

Read the raw webhook body and verify `X-Context-Signature` using the [signature verification implementation](https://docs.context.dev/webhooks.md#verify-signatures). The signature covers the timestamp and raw bytes. This Python equivalent uses the same protocol:

```python verify_webhook.py theme={null}
import hashlib
import hmac
import re
import time

def verify_webhook(raw_body, signature_header, secret, now=None):
    parts = {}
    for part in signature_header.split(","):
        key, separator, value = part.strip().partition("=")
        if separator:
            if key in parts:
                return False
            parts[key] = value
    timestamp = parts.get("t", "")
    signature = parts.get("v1", "")
    if not re.fullmatch(r"[0-9]{1,12}", timestamp) or not re.fullmatch(r"[0-9a-fA-F]{64}", signature):
        return False
    now = time.time() if now is None else now
    if abs(now - int(timestamp)) > 300:
        return False
    expected = hmac.new(secret.encode(), timestamp.encode() + b"." + raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.lower())
```

Reject a false verification result before parsing or storing the event. Compute the signature from the original request bytes.

The following Python store starts after that verification step. `accept_verified_event` also checks that the event belongs to the monitor associated with the verified secret. Route your webhook using the application watch ID, resolve its stored monitor and secret, then verify the signature, validate the payload, and call this function.

```python digest_store.py theme={null}
import json
import sqlite3

def open_digest(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript("""
      CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY, monitor_id TEXT NOT NULL, payload_json TEXT NOT NULL,
        processed INTEGER NOT NULL DEFAULT 0
      );
      CREATE TABLE IF NOT EXISTS changes (
        id TEXT PRIMARY KEY, monitor_id TEXT NOT NULL, title TEXT NOT NULL,
        summary TEXT NOT NULL, source_url TEXT NOT NULL, detected_at TEXT NOT NULL,
        payload_json TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY, monitor_id TEXT NOT NULL, status TEXT NOT NULL,
        started_at TEXT, completed_at TEXT, error_json TEXT
      );
    """)
    return db

def accept_verified_event(db, event, expected_monitor_id):
    if event.get("event") not in ("change.detected", "run.completed"):
        raise ValueError("Unsupported event")
    if not isinstance(event.get("id"), str) or not event["id"]:
        raise ValueError("Missing event ID")
    data = event["data"]
    primary = data["change"] if event["event"] == "change.detected" else data["run"]
    if primary["monitor_id"] != expected_monitor_id:
        raise ValueError("Event belongs to another monitor")
    if data.get("change") and data["change"]["monitor_id"] != expected_monitor_id:
        raise ValueError("Change belongs to another monitor")
    with db:
        db.execute("INSERT INTO events (id, monitor_id, payload_json) VALUES (?, ?, ?) ON CONFLICT(id) DO NOTHING",
            (event["id"], expected_monitor_id, json.dumps(event)))

def save_change(db, change):
    existing = db.execute("SELECT payload_json FROM changes WHERE id=?", (change["id"],)).fetchone()
    payload = {**json.loads(existing["payload_json"]), **change} if existing else change
    db.execute("""
      INSERT INTO changes VALUES (?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(id) DO UPDATE SET payload_json=excluded.payload_json
    """,
        (change["id"], change["monitor_id"], change["title"], change["summary"],
         change["url"], change["detected_at"], json.dumps(payload)))

def save_run(db, run):
    db.execute("""
      INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?)
      ON CONFLICT(id) DO UPDATE SET status=excluded.status,
        started_at=excluded.started_at, completed_at=excluded.completed_at,
        error_json=excluded.error_json
      WHERE runs.status NOT IN ('completed', 'failed', 'skipped')
         OR excluded.status IN ('completed', 'failed', 'skipped')
    """, (run["id"], run["monitor_id"], run["status"], run.get("started_at"),
          run.get("completed_at"), json.dumps(run.get("error"))))

def process_events(db):
    for row in db.execute("SELECT * FROM events WHERE processed=0").fetchall():
        event = json.loads(row["payload_json"])
        with db:
            if event["event"] == "run.completed":
                save_run(db, event["data"]["run"])
            if event["data"].get("change"):
                save_change(db, event["data"]["change"])
            db.execute("UPDATE events SET processed=1 WHERE id=?", (row["id"],))

def digest_items(db, start, end):
    # UTC timestamps in a consistent ISO 8601 format; [start, end).
    return [dict(row) for row in db.execute("""
      SELECT id, monitor_id, title, summary, source_url, detected_at
      FROM changes WHERE detected_at >= ? AND detected_at < ?
      ORDER BY detected_at, id
    """, (start, end))]
```

Validate parsed events against the [`change.detected`](https://docs.context.dev/api-reference/monitors/webhook-payload) or [`run.completed`](https://docs.context.dev/api-reference/monitors/webhook-run-completed) schema before calling the store. Return `2xx` only after the event insert commits. A worker can then call `process_events`; its transaction saves the derived records and marks the event processed together.

Deduplicate both levels. Event `id` handles a repeated delivery. Change `id` handles a changed run arriving through both event subscriptions, or later through polling. Both paths should produce one digest item.

## Reconcile deliveries and failed checks

`run.completed` reports completed runs, including baselines and runs with no change. Failed and skipped checks require the [runs API](https://docs.context.dev/api-reference/monitors/runs.md); absence of a webhook does not mean “no change.”

The following polling worker imports the store functions above. It reads every page of runs and changes and uses the same record IDs as the webhook path. For a larger history, persist a reconciliation cursor and continue the job across bounded worker executions.

```python reconcile_digest.py theme={null}
import json
import os
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from digest_store import save_change, save_run

def api_pages(path):
    cursor = None
    seen = set()
    while True:
        params = {"limit": 100}
        if cursor:
            params["cursor"] = cursor
        request = Request(
            f"https://api.context.dev/v1{path}?{urlencode(params)}",
            headers={"Authorization": f"Bearer {os.environ['CONTEXT_DEV_API_KEY']}"},
        )
        with urlopen(request, timeout=30) as response:
            page = json.load(response)
        yield page["data"]
        if not page["has_more"]:
            break
        cursor = page["next_cursor"]
        if not cursor or cursor in seen:
            raise ValueError("Invalid pagination cursor")
        seen.add(cursor)

def reconcile(db, monitor_id):
    encoded_id = quote(monitor_id, safe="")
    for page in api_pages(f"/monitors/{encoded_id}/runs"):
        with db:
            for run in page:
                save_run(db, run)
    for page in api_pages(f"/monitors/{encoded_id}/changes"):
        with db:
            for change in page:
                save_change(db, change)
```

The changes list returns full change records. Use the [retrieve endpoint](https://docs.context.dev/api-reference/monitors/change.md) when you have only a change ID or need to recover missing evidence. A later fetch should fill missing detail on the existing change, not create another item.

Only advance your reconciliation checkpoint after every page is saved. If a request fails, keep already saved rows, leave the job incomplete, and resume with a bounded retry policy. Inspect the monitor's `webhook_failure` and individual run delivery records when diagnosing delivery problems.

## Make freshness visible in the digest

Compute the last successful observation from completed runs rather than from the latest attempt:

```sql Last successful check theme={null}
SELECT monitor_id, MAX(completed_at) AS last_successful_check
FROM runs
WHERE status = 'completed'
GROUP BY monitor_id;
```

Show the latest failed or skipped check alongside this value. A baseline is a successful observation, but it has not yet compared two snapshots. Keep that distinction visible for newly added sources.

Each digest item should link to the observed URL and include its detection time. For sitemap changes, a newly discovered URL is a candidate for a follow-up scrape; its appearance alone does not prove that a new listing exists. Keep the original change evidence available behind summaries.

Build delivery around a saved digest edition and its change IDs. Use an outbox or equivalent durable queue, and record provider delivery state so worker retries do not repeatedly send the same edition. Notification channels and summarization belong to your application.

## Exercise duplicate and missing events

Process one change event twice, then process the `run.completed` event for the same changed run: the store should contain one change. Skip another webhook and reconcile it through the API. Add a failed run and check that the last successful observation remains intact while the failure appears in the watchlist.

> [card] [Monitor setup and signatures](https://docs.context.dev/monitors/overview)
>
> Configure targets, intervals, and verified webhook delivery.

> [card] [Structured datasets](https://docs.context.dev/use-cases/structured-web-datasets.md)
>
> Refresh stored records after a relevant source change.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.