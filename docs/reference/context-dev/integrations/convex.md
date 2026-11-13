# Convex

> Scrape pages and retrieve company data from typed Convex actions.

The `@context-dot-dev/convex` component calls Context.dev from your Convex backend with typed inputs and responses. This guide starts with a page scrape; the same client supports company lookups and other API operations.

> [card] [View Context.dev for Convex](https://www.convex.dev/components/context-dot-dev/convex)
>
> Open the component listing, package links, and current method catalog.

## Prerequisites

* An existing [Convex project](https://docs.convex.dev/quickstart)
* A Context.dev account and a secret key from the [dashboard](https://context.dev/dashboard)

## Install and configure

**1. Install the package**

```bash theme={null}
npm install @context-dot-dev/convex
```

**2. Register the component**

Add the component and its environment contract to `convex/convex.config.ts`:

```ts theme={null}
import contextDev from "@context-dot-dev/convex/convex.config.js";
import { defineApp } from "convex/server";
import { v } from "convex/values";

const app = defineApp({
  env: {
    CONTEXT_DEV_API_KEY: v.string(),
  },
});

app.use(contextDev, {
  env: {
    CONTEXT_DEV_API_KEY: app.env.CONTEXT_DEV_API_KEY,
  },
});

export default app;
```

**3. Set the deployment secret**

Set the key interactively so it does not appear in shell history, then start Convex development:

```bash theme={null}
npx convex env set CONTEXT_DEV_API_KEY
npx convex dev
```

Convex environment variables are deployment-specific. Set the same variable separately for production, using the `--prod` option, before deploying.

> [!WARNING]
>
> Keep `CONTEXT_DEV_API_KEY` in the Convex deployment environment. Do not put it in `.env` files committed to source control or pass it from browser code.

## Call Context.dev from an action

Create a shared typed client and call it inside a Convex action. For example, add `convex/context.ts`:

```ts theme={null}
import { ContextDev } from "@context-dot-dev/convex";
import { v } from "convex/values";

import { components } from "./_generated/api.js";
import { action } from "./_generated/server.js";

const contextDev = new ContextDev(components.contextDev);

export const scrapeMarkdown = action({
  args: { url: v.string() },
  handler: async (ctx, { url }) => {
    return await contextDev.scrapeMarkdown(ctx, {
      params: { url },
    });
  },
});
```

Run the action against the development deployment:

```bash theme={null}
npx convex run context:scrapeMarkdown '{"url":"https://www.context.dev"}'
```

Inspect the returned `markdown` field to confirm the action reached Context.dev.

> [!NOTE]
>
> Context.dev methods must run in Convex actions because they make external HTTP requests. Do not call the component directly from a query or mutation.

## Common methods

| Method | Result |
| - | - |
| `scrapeMarkdown` / `scrapeHtml` | Clean Markdown or rendered HTML for a known URL |
| `search` / `crawl` | Current search results or pages from a focused site crawl |
| `retrieveBrand` | Logos, colors, company information, links, and industry data |
| `styleguide` | Detected colors, typography, and design system details |
| `screenshot` | A rendered webpage screenshot |

GET-backed helpers take `params`. POST-backed helpers take `body` and may also take `params` when the operation defines query parameters. TypeScript infers both the arguments and responses from the component.

## Data and caching

The component returns API results to your action but does not persist them in Convex. Store a result in your own tables only when your application needs it. Context.dev controls upstream caching through request parameters such as `maxAgeMs`.

## Troubleshooting

| Symptom | Fix |
| - | - |
| `components.contextDev` is missing | Run `npx convex dev` so Convex registers the component and regenerates `_generated`. |
| The action reports a missing environment variable | Set `CONTEXT_DEV_API_KEY` on the deployment you are calling, not only another development or production deployment. |
| A query or mutation cannot call the component | Move the external request into an `action`; queries and mutations cannot make arbitrary HTTP requests. |
| The API returns an authentication error | Replace the deployment secret with a current `ctxt_secret_` key from the Context.dev dashboard. |

## Reference

> [card] [Component source](https://github.com/context-dot-dev/convex-component)
>
> README, helper methods, generated bindings, examples, and tests.

> [card] [npm package](https://www.npmjs.com/package/@context-dot-dev/convex)
>
> Published package versions and install metadata.

> [card] [Convex components](https://docs.convex.dev/components/)
>
> How components are installed, configured, and called.

> [card] [Context.dev API quickstart](https://docs.context.dev/quickstart.md)
>
> Authentication, endpoint behavior, and API examples.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.