# Complete demo rehearsal

Issue #214. Checked on 15 November 2026. Launch the demo at
https://cosmic-enhanced-jawfish.eur-1.aiven.app/?demo.
This is the real backend and Gemini, using recorded Cala data. The separate guided tour
uses sample data and does not verify the deployed backend.

## Repeat the verified flow

1. Open the Aiven URL above, exit the guided tour if it opens, and choose
   **New research**. Keep the existing research so the rehearsal does not replace it.
2. Send: `I am preparing for Slush. Find AI startups at pre-seed or seed. I trust
   Y Combinator and 500 Global.` Answer the questions with **Others too**, **Any time**
   and **Anywhere** (or their equivalent wording). The rehearsal produced eight startups.
3. Open the report. Pally and whisperr showed their trusted backers. Open a real source:
   Pally's **Company or investor** badge linked to
   `https://www.ycombinator.com/companies/pally`, which loaded successfully.
4. Send `Shorter, co-investors first`. Wait for the rewrite to finish. The report changed
   from eight to five startups; the profile change appeared in the conversation.
5. Send `Add FIRSTPICK to the investors I trust, alongside Y Combinator and 500 Global.
   Keep the report short, co-investors first.` Wait for the new report and check that
   **GREÏ is in it**. This matters: the fixed `grei_seed_round` fixture always concerns
   GREÏ, which was absent from the first five-startup report.
6. Confirm **Looks right, keep me posted**. On a narrow screen, close the report panel
   before using the **Alerts** button in the header. Press it once; it must show
   **Alert in 30 s**. Leave the app open until the alert arrives.
7. Open the notification in the chat. Check **Simulated event**, GREÏ's name,
   **Why it matters**, and the staged EUR 2.5M round. Say aloud that the event is simulated.
   Its `grabbit.example/simulated` source is a label for the simulation, not a real source
   to open. The report's recorded EUR 650K pre-seed must remain unchanged.

Gemini may vary its wording and questions. Verify the actual selected companies before
showing an alert; do not promise a fixed candidate count for other profiles or caches.

## Checks

- `make test lint` runs the backend and frontend regression suites and static checks.
- `backend/tests/test_demo_flow.py` exercises the graph-backed thesis, questions, sourced
  report, instruction rewrite, an alert for a selected company, event-bus delivery and
  workspace isolation through HTTP APIs. It mocks Cala and uses FakeLLM; it does not
  establish live provider availability.
- `frontend/src/features/demo/demo.test.tsx` exercises the separate guided sample tour,
  including report rewrite, labelled alert and returning to the visitor's research.
- `frontend/src/components/FactValue.test.tsx`, `finalPolish.test.tsx` and
  `features/alerts/alerts.test.tsx` protect currency rendering. Whole compact amounts
  must read `€650K` and `€8M`, while fractional amounts retain their decimal.

## Cache readiness

Before presenting locally, run `make warm ARGS=--check` on the database the app actually
uses. Both the event walk and reverse walk must report zero misses to claim a fully
warmed graph. A functioning shortlist alone does not prove full reverse-walk coverage.

The original laptop cache passed the first turn (898 calls, zero misses), but missed the
full attendee-list request needed by the reverse walk. Warming an isolated copy recovered
the attendee list and additional investor paths. Cala returned HTTP 429 during the process;
spacing requests one second apart let the demo pair finish with 699 calls and zero reverse
misses. The new recorded responses were added to the original cache without replacing
existing entries or changing profiles and reports. The warm-up also includes FIRSTPICK,
which keeps the staged alert's company in the rehearsal shortlist. Final check on the
original database with all three references: **898 first-turn calls, zero misses;
700 reverse-walk calls, zero misses**. In total, 567 recorded responses were added.

The custom domain worked for the first rehearsal, then redirected API requests to an Aiven
service-status page (HTTP 307, ending in HTTP 404). The direct Aiven hostname still returned
`status=ok`, `cala_mode=replay`, `llm_mode=gemini`, `demo_mode=true`. Use that host until
the custom-domain mapping is repaired; do not present from a stale tab on the custom domain.

The deployed cache is separate. This checkout has no `VALKEY_URL`, so local warming does
not update Aiven. See README, **Deploy**, for the shared-cache connection and manual
runtime deployment. Browser notification permission and delivery while the tab is hidden
need a separate check in the browser used for presenting; in-app delivery is the rehearsal's
verified path.

## Local fallback

Build once while online with `cd frontend && npm run build`. From `backend/`, serve the
already built app with:

```sh
CALA_MODE=replay LLM_MODE=fake DEMO_MODE=1 VALKEY_URL= \
  uv run uvicorn app.main:app --host 127.0.0.1 --port 8014
```

Open `http://127.0.0.1:8014/?tour` for the explicitly labelled sample-data tour. This
fallback uses scripted responses, not live Gemini. A rehearsal copy was also started on
this port with `DATABASE_PATH=/tmp/grabbit-214/local-demo.db`, so it does not change the
presenter's existing profiles or reports.
