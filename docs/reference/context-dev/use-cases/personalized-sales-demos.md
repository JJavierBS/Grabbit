# Create a personalized sales demo

> Use a prospect's domain to prepare a branded demo with sourced account facts, editable content, and a reviewable sharing step.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/personalized-sales-demos.md

Read the recipe and linked API guides, inspect this project's stack, and build the complete flow using its existing conventions.

Turn a verified prospect domain into a saved, editable demo configuration with reviewed branding and sourced account facts. Keep sender, prospect, CRM context, and clearly labeled sample data distinct. Render a preview, preserve manual overrides across regeneration, and version drafts separately from approved shareable demos. Tie claims to evidence and keep each account's data separate.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Turn a prospect's domain into a demo that looks familiar and uses relevant, verified account context. Context.dev supplies brand data and website evidence. Your application supplies CRM history, the product demonstration, and delivery.

[MarketBetter uses brand context for sales meeting preparation](https://www.context.dev/blog/marketbetter-gives-every-sdr-on-brand-meeting-prep-with-context-dev), and [Comp AI built a branded sales-deck generator](https://www.context.dev/blog/comp-ai-builds-an-on-brand-sales-deck-generator-with-context-dev). This recipe produces a saved demo configuration that your own renderer can preview.

## Resolve the prospect first

Start with a verified company domain from your CRM or a rep's selection. If the flow begins with a work email, use [Brand by email](https://docs.context.dev/brand/lookup-by-email.md) and let the rep confirm the result. Similar company names, subsidiaries, and platform-hosted pages can otherwise produce the wrong branding.

Keep the sender and prospect as distinct identities:

| Identity | Purpose |
| - | - |
| Sender | Who built the demo, owns its claims, and will share it |
| Prospect | Whose approved branding and public context personalize the experience |
| Example data | Clearly labeled sample records used to demonstrate the product |

## Gather branding and selected facts

On your server, use an API key from the [Quickstart](https://docs.context.dev/quickstart.md) to retrieve the [Brand profile](https://docs.context.dev/brand/lookup-by-domain.md). Use [Styleguide](https://docs.context.dev/brand/styleguide.md) only when the template needs additional design context.

Read selected about or product pages with [Scrape](https://docs.context.dev/scrape/markdown.md) and `formats.markdown`. The following body reads a product page's main content:

```json Scrape request body theme={null}
{
  "url": "https://example.com/product",
  "formats": { "markdown": true },
  "sharedParams": { "mainContentOnly": true }
}
```

Keep `markdown.data`, the final `url`, `metadata.title`, and the retrieval time with the result. A blocked or missing page still returns HTTP 200: check `markdown.success`, and treat `success: false` with `error_code` `WEBSITE_BLOCKED`, `NOT_FOUND`, or `REQUEST_TIMEOUT` as a missing page, not as evidence about the product.

When the demo needs shaped JSON rather than page text, send [Answers](https://docs.context.dev/answers/overview) a task that asks only for public product context. Name the domain in `task` so research starts on the prospect's site, and use placeholder values so an unstated field returns `null`:

```json Answers request body theme={null}
{
  "mode": "fast",
  "task": "On example.com, report the product's stated purpose and the audience the site explicitly names. Use null when the site does not state one. Do not infer the company's buying goals.",
  "json_format": {
    "product_description": "",
    "stated_audience": ""
  }
}
```

`fast` suits focused lookups; `ultra` researches more deeply. Keep `sources` and the retrieval time with the result. Before approving a fact for the demo, inspect the relevant page and retain its supporting URL or excerpt. `sources` lists contributing pages, not field-level citations.

A full-site crawl should not be required to preview a demo. Let an unavailable page remain missing, and keep a neutral theme and editable company name when brand data is partial.

## Keep website evidence and CRM history distinct

Public website text can support a description of a product. Your CRM can support a rep's meeting notes or a stated next step. Neither source should silently overwrite the other.

```typescript demo-model.ts theme={null}
type Fact = {
  id: string;
  text: string;
  source:
    | { kind: "website"; url: string; retrievedAt: string; excerpt: string }
    | { kind: "crm"; recordId: string; updatedAt: string };
};

type DemoTheme = { accent: string; logoUrl: string | null };
type DemoOverrides = {
  headline?: string;
  accent?: string;
  logoUrl?: string | null;
};

type DemoConfig = {
  version: number;
  state: "draft" | "approved";
  preparedBy: string;
  preparedFor: { name: string; domain: string };
  headline: string;
  theme: DemoTheme;
  facts: Fact[];
  sampleDataLabel: string;
  sourceVersion: string;
  overrides: DemoOverrides;
};

export function buildDemo(input: {
  senderName: string;
  prospectName: string;
  prospectDomain: string;
  reviewedTheme: DemoTheme;
  approvedFacts: Fact[];
  sourceVersion: string;
  previous?: DemoConfig;
}): DemoConfig {
  if (input.previous && input.previous.preparedFor.domain !== input.prospectDomain) {
    throw new Error("Start a separate demo for a different account");
  }
  const overrides = input.previous?.overrides ?? {};
  return {
    version: (input.previous?.version ?? 0) + 1,
    state: "draft",
    preparedBy: input.senderName,
    preparedFor: { name: input.prospectName, domain: input.prospectDomain },
    headline: overrides.headline ?? `A product demo for ${input.prospectName}`,
    theme: {
      accent: overrides.accent ?? input.reviewedTheme.accent,
      logoUrl: overrides.logoUrl !== undefined
        ? overrides.logoUrl : input.reviewedTheme.logoUrl,
    },
    facts: input.approvedFacts,
    sampleDataLabel: "Illustrative sample data",
    sourceVersion: input.sourceVersion,
    overrides,
  };
}
```

`approvedFacts` means facts checked against their source for this revision. Keep their IDs tied to content or a source version so a changed claim cannot inherit an old approval. Rebuilding creates a draft while preserving design and headline edits; it does not silently update an already-shared demo.

## Populate the product demonstration

Use the configuration to select and fill components you control. A model can suggest which product features to highlight, but its output should reference approved fact IDs and a fixed list of available demo sections.

Do not infer the prospect's budget, purchase intent, goals, customer relationships, or results from its branding. Keep sample accounts, transactions, metrics, and testimonials visibly illustrative unless the rep supplied approved real data.

In the preview, show the sender and recipient labels, the source links behind account facts, and controls to replace the logo or edit the copy. Keep internal CRM notes out of the shared payload unless the rep intentionally selects content appropriate for the recipient.

## Save and share the reviewed revision

Persist the configuration and source-bundle version with your CRM account ID. A share action should select an approved revision and create the appropriate application link or export. Email sending, CRM updates, access controls, and link expiry belong to your application.

Try one complete prospect profile, one missing logo, a failed product-page read, and an edited headline. Regenerate the demo and verify that edits survive, unsupported claims remain absent, and the shared version stays unchanged until a new revision is approved.

> [card] [Lead enrichment](https://docs.context.dev/use-cases/lead-enrichment.md)
>
> Save company and person context without replacing rep edits.

> [card] [Branded documents](https://docs.context.dev/use-cases/branded-documents.md)
>
> Render the approved meeting brief as a report or deck.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.