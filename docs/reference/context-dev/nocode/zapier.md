# Zapier

> Enrich spreadsheet rows, research websites, and send change alerts with Context.dev in Zapier.

Add Context.dev to a Zap to turn a domain into company data, scrape a webpage, or send website change alerts. Start by enriching one spreadsheet row, then choose other operations as your workflow grows.

> [card] [Install the Context.dev Zapier app](https://zapier.com/apps/contextdev/integrations)
>
> Connect your Context.dev account using an API key.

## Setup walkthrough

This example reads a domain from Google Sheets and writes the company name back to the same row.

### Prerequisites

* A [Context.dev API key](https://context.dev/dashboard).
* A Zapier account with access to the apps and steps used in your workflow.
* A Google Sheet with `domain` and `company_name` columns. Add a test row containing `stripe.com` in the domain column.

### 1. Connect your account

Open the [Context.dev app in Zapier](https://zapier.com/apps/contextdev/integrations), create a connection, and enter your `ctxt_secret_` key. Give it a name such as `Context.dev production` so you can identify it later.

Keep the key in the saved connection. Other steps should use that connection rather than copy the key into fields or notes.

### 2. Add a trigger

Create a Zap with **Google Sheets > New Spreadsheet Row**. Select your spreadsheet and worksheet, then test the trigger. Confirm that the test record includes `stripe.com` in the `domain` field.

### 3. Get the company profile

Add **Context.dev > Get Brand Profile**:

| Field | Value |
| - | - |
| Connection | Your saved Context.dev connection |
| Lookup By | Domain |
| Lookup Value | The trigger's `domain` field |
| Optional fields | Leave blank for the first test |

Select **Test step**. Check that the response contains `brand.domain` and `brand.title`. Other fields, including logos and social profiles, may be absent.

> [!NOTE]
>
> Action names depend on the version available to your connection. If **Get Brand Profile** is missing, check the [older action names](#upgrading-from-the-retired-actions) or use an [HTTP request](#reach-endpoints-without-a-dedicated-action) with the current API contract.

### 4. Map and publish

Add **Google Sheets > Update Spreadsheet Row**. Map the original row ID from the trigger and the returned **Brand Title** to `company_name`. Preserve the domain and any fields you are not enriching.

Test the update, confirm the expected row changed, then publish the Zap. Add a new row and inspect its run in **Zap History** before processing a larger list.

## Map the response

Most workflows can map the action's output directly without a code step:

| Field | Use it for |
| - | - |
| `brand.title` | Company name |
| `brand.domain` | Resolved company domain |
| `brand.description` | Company summary |
| `brand.logos` | Available logo files |
| `brand.socials` | Social profile links |

Keep existing destination values when optional data is missing. For arrays, select the entry that fits your use case rather than assuming the first logo or social profile is always the right one.

## What you get

Triggers start a Zap, searches find an existing record, and actions pass API results to later steps. The catalog below describes the version 3.1 action names for the endpoints these docs cover; the app also lists a few actions outside them, such as **Extract Structured Data** and **Get Website Fonts**. Check the version in your Zap editor when a name or field differs. Context.dev API usage and Zapier tasks are billed separately.

> [accordion] Triggers and searches
>
> ### Triggers
>
> | Trigger | Fires when | Filters | Endpoint |
> | - | - | - | - |
> | **New Website Change** | A website monitor confirms a change | Monitor ID (blank watches every monitor), Target Type, Tags | `GET /monitors/changes` |
> | **New Monitor Run** | A monitor run is recorded | Monitor ID (blank watches every monitor), Run Status | `GET /monitors/runs` |
> | **Batch Finished** | A batch reaches the chosen final status (`completed`, `cancelled`, or `failed`) | Final Status (required), Tags | `GET /batch/list` |
>
> All three are polling triggers. Zapier checks Context.dev on your Zapier plan's polling interval, so an event reaches your Zap a few minutes after Context.dev records it. For instant delivery, give the monitor a **Webhook URL** that points at a Webhooks by Zapier catch hook instead; see [Receive webhooks](https://docs.context.dev/monitors/webhooks.md).
>
> ### Searches
>
> | Search | Input | Output | Endpoint |
> | - | - | - | - |
> | **Find Website Monitor** | Monitor ID for an exact lookup, or Name Search | The matching monitor | `GET /monitors/{monitor_id}` or `GET /monitors` |
> | **Find Batch** | Batch ID, or Search Query when the ID is blank | The matching batch with its status and progress | `GET /batch/{batch_id}` or `GET /batch/list` |
>
> Searches are useful as the step before an update: find the monitor by name, then feed its ID into **Update Website Monitor** or **Run Website Monitor Now**.

> [accordion] Company data
>
> ### Brand intelligence actions
>
> | Action | Input | Output | Endpoint |
> | - | - | - | - |
> | **Get Brand Profile** | Lookup By (domain, company name, email, ticker, URL, or transaction description) and Lookup Value, plus optional Country, Ticker Exchange, Maximum Speed, and Maximum Cache Age | Full brand record (logos, colors, description, socials, industry, address) | `POST /brand/retrieve` |
> | **Get Website Style Guide** | Website (domain or full URL), optional Maximum Cache Age and Color Scheme | Colors, typography, font files, spacing, shadows, and UI components | `GET /web/styleguide` |
> | **Search Company News** | Identify Company By (domain, company name, ticker, or ISIN) and Company Identifier, plus optional Stock Exchange, Publisher Domains, Publisher Countries, Article Languages, Article Types, Published After, Published Before, Sort Order, Maximum Results (1 to 100), and Pagination Cursor | Matching articles plus a Next Cursor for the following page | `POST /news/search` |

> [accordion] Web scraping and search
>
> ### Web scraping and search actions
>
> | Action | Input | Output | Endpoint |
> | - | - | - | - |
> | **Fetch Page Content** | URL, optional Include Links, Include Images, Main Content Only, Also Include HTML, Wait Before Reading, Maximum Cache Age, Country, and Zero Data Retention | The page as Markdown, plus its HTML when requested | [`POST /web/scrape`](https://docs.context.dev/api-reference/web-scraping/scrape) |
> | **Fetch Raw Page HTML** | URL, optional Wait Before Reading, Maximum Cache Age, Country, and Zero Data Retention | Rendered page HTML | [`POST /web/scrape`](https://docs.context.dev/api-reference/web-scraping/scrape) |
> | **Find Images on a Page** | URL, optional Wait Before Reading and Maximum Cache Age | Images found on the page | [`POST /web/scrape`](https://docs.context.dev/api-reference/web-scraping/scrape) |
> | **Find Website Pages** | Domain, optional Maximum Links, Topic Search, URL Pattern, and Zero Data Retention | The site's URLs and available metadata, ranked by Topic Search when set | [`GET /web/urls`](https://docs.context.dev/api-reference/web-scraping/map) |
> | **Crawl a Website** | URL, optional Maximum Pages (1 to 500), Maximum Link Depth, URL Pattern, Follow Subdomains, Main Content Only, Stop After, Maximum Cache Age, Country, and Zero Data Retention | Markdown for every crawled page | `POST /web/crawl` |
> | **Capture Website Screenshot** | URL, optional Capture Full Page, Viewport Width, Viewport Height, Wait Before Capture, Color Scheme, and Maximum Cache Age | Screenshot of the page | [`POST /web/scrape`](https://docs.context.dev/api-reference/web-scraping/scrape) |
> | **Search the Web** | Search Query, optional Number of Results (1 to 100), Only These Domains, Exclude These Domains, Freshness, Country, Expand Search Query, and Include Page Content | Ranked results with title, URL, and snippet, plus cleaned page content when requested | `POST /web/search` |

> [accordion] Document parsing
>
> ### Document parsing actions
>
> | Action | Input | Output | Endpoint |
> | - | - | - | - |
> | **Parse a Document** | File (from an earlier step or a public URL) and File Extension (`pdf`, `docx`, `pptx`, `xlsx`, `png`, and so on), optional Include Links, Include Images, Use OCR, and Zero Data Retention | Document text as Markdown | `POST /parse` |

> [accordion] Batch processing
>
> ### Batch processing actions
>
> | Action | Input | Output | Endpoint |
> | - | - | - | - |
> | **Submit URL Batch** | URLs (comma or newline separated, up to 100,000) or URL Items JSON, Output Format (`markdown` or `html`), optional Main Content Only, Wait Per Page, Country, Maximum Cache Age, Completion Webhook URL, and Tags | Batch ID and initial status | `POST /batch/submit` |
> | **Submit Website Crawl Batch** | Source Type (start URL or sitemap), Start URL or Domain, Output Format, optional Maximum Pages (1 to 100,000), Maximum Link Depth, URL Pattern, Follow Subdomains, Main Content Only, Wait Per Page, Country, Maximum Cache Age, Completion Webhook URL, and Tags | Batch ID and initial status | `POST /batch/submit` |
> | **Get Batch Results** | Batch ID, optional Results Per Page and Next Cursor | One page of result records plus the next cursor | `GET /batch/{batch_id}/results` |
> | **Cancel Batch** | Batch ID and Confirm | The batch as it winds down | `POST /batch/{batch_id}/cancel` |

> [accordion] Website monitors
>
> ### Website monitor actions
>
> | Action | Input | Output | Endpoint |
> | - | - | - | - |
> | **Create Website Monitor** | Monitor Name, Target Type, Target URL, plus optional Change Instructions, Structured Data Schema, Include Sitemap Paths, Exclude Sitemap Paths, Maximum Pages or URLs, Change Detection, Semantic Confidence Threshold, Run Every, Schedule Unit, Tags, and Webhook URL | The new monitor, including its ID | `POST /monitors` |
> | **Update Website Monitor** | Monitor ID, optional New Name, Status (`active` or `paused`), Run Every, Schedule Unit, Tags, and Advanced Update JSON | The updated monitor | `PATCH /monitors/{monitor_id}` |
> | **Run Website Monitor Now** | Monitor ID | The queued run | `POST /monitors/{monitor_id}/run` |
> | **Delete Website Monitor** | Monitor ID and Confirm Permanent Deletion | Confirmation | `DELETE /monitors/{monitor_id}` |

## Request options

* **Lists are plain text.** Fields such as URLs, Tags, Publisher Domains, and Only These Domains take comma-separated values or one value per line.
* **Maximum Cache Age (Milliseconds)** controls how old a cached result may be. Leave it blank for the endpoint default, or set `0` to skip the cache and fetch fresh data. See [freshness controls](https://docs.context.dev/scrape/freshness-and-caching.md) and [Brand caching](https://docs.context.dev/brand/overview#options).
* **Country** takes a two-letter code such as `US` or `GB` and fetches the page as a visitor from that country would see it.
* **Zero Data Retention** bypasses shared caches and keeps request content out of retained logs. It only works once zero data retention is enabled for your organization; otherwise the step fails with `ZDR_NOT_ENABLED`. See [Zero Data Retention](https://docs.context.dev/optimization/zero-data-retention.md).
* **Free and disposable emails are rejected.** **Get Brand Profile** with **Lookup By** set to email returns a `422` for addresses at Gmail, Yahoo, and similar providers, or at disposable-email domains.
* **Keep single-step crawls small.** **Crawl a Website** runs inside one Zap step. For whole sites, use **Submit Website Crawl Batch** and pick the results up with the **Batch Finished** trigger.
* **Include Page Content** returns cleaned page content alongside each search result.

### Upgrading from the retired actions

For a Zap using version 3.0 action names, use this mapping when upgrading to version 3.1. Test the replacement's inputs and outputs before publishing the updated Zap.

> [accordion] Compare action names
>
> | Version 3.0 action | Version 3.1 replacement |
> | - | - |
> | Retrieve Brand Data by Domain, by Company Name, by Email Address, by Stock Ticker | **Get Brand Profile** with the matching **Lookup By**. Turn on **Maximum Speed** when you need a faster, less comprehensive profile. |
> | Retrieve Simplified Brand Data by Domain | **Get Brand Profile** with **Lookup By** set to domain and **Maximum Speed** turned on |
> | Retrieve Brand Data by ISIN | No direct replacement. Look the company up by ticker or domain instead. **Search Company News** still accepts an ISIN. |
> | Identify Brand From Transaction Data | **Get Brand Profile** with **Lookup By** set to transaction description, plus **Country** when you have it |
> | Take Screenshot of Website | **Capture Website Screenshot**. Pass the full URL of the page to capture, such as `https://stripe.com/pricing`. |
> | Extract Design System and Styleguide From Website | **Get Website Style Guide** |
> | Extract Fonts From Website | **Get Website Fonts**, or **Get Website Style Guide** for typography alongside colors and components |
> | Extract Products From a Brand's Website | No dedicated action. Call [`POST /web/scrape`](https://docs.context.dev/scrape/product) with `formats.product` through Webhooks by Zapier; see [Reach endpoints without a dedicated action](#reach-endpoints-without-a-dedicated-action). |
> | Query Website Data Using AI | **Extract Structured Data**. Review its schema and inputs before replacing the step. |
> | Prefetch Brand Data for a Domain, Prefetch Brand Data by Email | No dedicated action. Call `POST /utility/prefetch` through Webhooks by Zapier; see [Reach endpoints without a dedicated action](#reach-endpoints-without-a-dedicated-action). |
> | Custom API Request | Use Webhooks by Zapier; see [Reach endpoints without a dedicated action](#reach-endpoints-without-a-dedicated-action). |

## Start Zaps from Context.dev events

The triggers turn Context.dev into the source of a Zap instead of a step in the middle.

### Website change alerts

1. Create the monitor in the [dashboard](https://context.dev/dashboard) or with the **Create Website Monitor** action. Give it a tag such as `competitors` so you can filter on it later.
2. **Trigger:** Context.dev "New Website Change". Set **Monitor ID** to watch one monitor, or leave it blank and set **Tags** to `competitors` to watch a group.
3. **Action:** Slack "Send Channel Message" with the change summary, the monitor name, and the target URL.

Each change record includes an importance rating. Add a **Filter by Zapier** step on it to keep low-value edits out of the channel. See [Create Monitors](https://docs.context.dev/monitors/overview) for how targets and detection modes work.

### Batch pipeline

Submitting a batch and reading its results are two Zaps, connected by the **Batch Finished** trigger.

**Zap A: submit**

1. **Trigger:** Google Sheets "New Spreadsheet Row" with a `domain` column
2. **Action:** Context.dev "Submit Website Crawl Batch" with **Source Type** set to sitemap, **Start URL or Domain** mapped from the row, **Output Format** set to `markdown`, and **Tags** set to `sheet-import`

**Zap B: collect**

1. **Trigger:** Context.dev "Batch Finished" with **Final Status** set to `completed` and **Tags** set to `sheet-import`
2. **Action:** Context.dev "Get Batch Results" with the **Batch ID** from the trigger and **Results Per Page** set to `100`
3. **Looping by Zapier:** Iterate over the result records
4. **Action:** Airtable "Create Record" per page with its URL, title, and Markdown

**Get Batch Results** returns one page at a time. Continue with each **Next Cursor** until no cursor remains. For an unknown number of pages, use a workflow or completion-webhook handler that can repeat this process; adding one more step only reads one more page. Record shapes are documented in [Read result records as JSON](https://docs.context.dev/batches/results.md#read-results).

## Reach endpoints without a dedicated action

Some endpoints have no Zapier action yet, for example people search and enrichment, company search, Answers, brand search, cache prefetching, batch deletion, usage and logs, and per-monitor change history. Use the built-in **Webhooks by Zapier** app to call them with your API key.

| Field | What to enter |
| - | - |
| **Action event** | `Custom Request` |
| **Method** | The method from the API reference, such as `POST` |
| **URL** | The full endpoint URL, such as `https://api.context.dev/v1/people/enrich` |
| **Data** | The JSON body for `POST` and `PATCH` requests |
| **Headers** | `Authorization` set to `Bearer ctxt_secret_...` and `Content-Type` set to `application/json` |

Example: enrich a new lead with people data.

1. **Trigger:** HubSpot "New Contact"
2. **Action:** Webhooks by Zapier "Custom Request"
   * **Method:** `POST`
   * **URL:** `https://api.context.dev/v1/people/enrich`
   * **Data:** `{"email": "<contact email from step 1>"}`
   * **Headers:** `Authorization: Bearer ctxt_secret_...` and `Content-Type: application/json`
3. **Action:** HubSpot "Update Contact" with the returned title, company, and social profiles

The key lives in the step configuration rather than in a saved connection, so keep these Zaps in a folder with restricted access, and prefer a dedicated Context.dev action whenever one exists. Parameter names and response shapes for every endpoint are in the [API reference](https://docs.context.dev/api-reference/brand-intelligence/brand.md).

## Troubleshooting

General API errors and retry guidance are in [Troubleshooting](https://docs.context.dev/optimization/troubleshooting.md). Zapier-specific issues:

* **"Authentication failed."** The API key was rejected. Re-paste it in Zapier's **My Apps > Context.dev** connection settings; confirm the `ctxt_secret_` prefix.
* **Get Brand Profile returns 422 on an email.** The address is at a free provider (Gmail, Yahoo, and similar) or a disposable-email domain. Filter those out before the Context.dev step, or switch **Lookup By** to company name or domain.
* **A trigger never fires.** Polling triggers only pick up events recorded after the Zap is turned on. Check that the monitor is active, that **Monitor ID**, **Tags**, or **Final Status** filters match, and that Zapier's polling interval has elapsed. **Batch Finished** requires one **Final Status**, so make a separate Zap for each terminal status you care about.
* **Create Website Monitor is rejected.** Semantic page monitors and structured website monitors need **Change Instructions**, sitemap monitors only support exact change detection, and **Run Every** with **Schedule Unit** must land between 10 minutes and one year. See [Pick a target](https://docs.context.dev/monitors/overview#pick-a-target).
* **A crawl step times out.** Lower **Maximum Pages** or **Maximum Link Depth**, or move the job to **Submit Website Crawl Batch** and read it back with **Batch Finished** and **Get Batch Results**.
* **Parse a Document fails.** **File Extension** is required and must match the file, written without a dot. Scanned PDFs need **Use OCR** turned on.
* **A step fails with `ZDR_NOT_ENABLED`.** **Zero Data Retention** is on but your organization has not enabled it. Turn the field off, or contact [support@context.dev](mailto:support@context.dev) to enable it.
* **No logo in the response.** Keep the company name visible and use your own initials or neutral icon when the destination needs an image. [Logo Link](https://docs.context.dev/brand/logo-link.md) can provide a hosted logo, but it also needs a format-compatible fallback.
* **An old Zap references a different action name.** Compare the installed version with [the migration table](#upgrading-from-the-retired-actions), then test the replacement before publishing.

## Next steps

> [card] [Make integration](https://docs.context.dev/nocode/make.md)
>
> Build a scenario using Context.dev and Make's HTTP module.

> [card] [Website monitors](https://docs.context.dev/monitors/overview)
>
> Targets, detection modes, schedules, and webhooks behind the monitor
> actions and triggers.

> [card] [Batch jobs](https://docs.context.dev/batches/overview)
>
> How batches are queued, billed, and read back.

> [card] [Brand API reference](https://docs.context.dev/api-reference/brand-intelligence/brand.md)
>
> The underlying endpoints. Useful when reading Zap test responses.

> [!TIP]
>
> Need help implementing a specific Zap? [Email us](mailto:hello@context.dev)
> and we'll walk through it with you.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.