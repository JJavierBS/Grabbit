# Eve

> Give an Eve agent Context.dev tools with a separate connection for each user.

Add Context.dev from [Eve's integration registry](https://eve.dev/integrations/context) to give your agent live web and company data. Each user connects their own Context.dev account through OAuth.

> [card] [Open the Context.dev integration for Eve](https://eve.dev/integrations/context)
>
> Review the current registry definition and setup instructions on Eve.

## Prerequisites

* An existing [Eve project](https://eve.dev/docs)
* The Eve and [Vercel CLIs](https://vercel.com/docs/cli) available in that project
* A Vercel account with access to the project you will link

## Install and connect

**1. Add the registry connection**

Run this from the root of your Eve project:

```bash theme={null}
eve add connection/context
```

Eve creates `agent/connections/context.ts` and installs the authentication dependency when needed. The generated connection points to `https://mcp.context.dev/mcp`.

**2. Create the Vercel connector**

Link the project, create the connector, and pull its local environment:

```bash theme={null}
vercel link
vercel connect create mcp.context.dev --name context
vercel env pull
```

Run these commands against the same Vercel project and environment that hosts the Eve agent.

**3. Authorize Context.dev**

Start the agent through your normal Eve development flow and request a Context.dev operation. Before the first tool call, Vercel Connect opens Context.dev's browser authorization flow. Sign in and approve access.

> [!NOTE]
>
> The connection uses per-user OAuth. Do not add a Context.dev API key, bearer token, or custom authorization header to `agent/connections/context.ts`.

## Verify the setup

Start with a request whose result you can inspect:

```text theme={null}
Use Context.dev to scrape https://www.context.dev and return the page title and source URL. Use the connected tool.
```

Confirm that Eve shows a successful Context.dev tool call. An answer without a tool call does not verify the connection.

## Use the connection

Ask the agent for an outcome and name Context.dev when you want to force this connection. For example:

```text theme={null}
Use Context.dev to search for Stripe's latest official product announcements. Summarize the results and include the source URLs.
```

```text theme={null}
Use Context.dev to scrape https://example.com/pricing and return every plan as JSON with name, price, and included limits.
```

The connection covers these common workflows:

| Need | Context.dev capability |
| - | - |
| Find or read current pages | Web search, Markdown or HTML scraping, URL mapping, and crawling |
| Capture or parse content | Screenshots, page images, and document parsing |
| Enrich a company | Brand profiles with industry labels, logos, and style guides |
| Run work over time | Website monitors and asynchronous batch jobs |

## Troubleshooting

| Symptom | Fix |
| - | - |
| The `context` connection is missing | Confirm `agent/connections/context.ts` exists, then rerun `eve add connection/context`. |
| Authorization never starts | Rerun `vercel connect create mcp.context.dev --name context`, then `vercel env pull`. |
| OAuth succeeds but tools remain unavailable | Restart the Eve development process so it reloads the pulled environment. |
| A deployed agent cannot connect | Confirm the connector belongs to the deployed Vercel project and environment, not only a local or different project. |

## Reference

> [card] [Eve integration listing](https://eve.dev/integrations/context)
>
> Current registry commands and generated connection definition.

> [card] [Eve connections](https://eve.dev/docs/connections)
>
> Connection configuration, authentication, and tool access in Eve.

> [card] [Context.dev MCP guide](https://docs.context.dev/install-mcp.md)
>
> Hosted server capabilities and authentication details.

> [card] [Context.dev API docs](https://docs.context.dev/introduction.md)
>
> Guides and reference material for the underlying operations.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.