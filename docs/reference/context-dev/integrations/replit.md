# Replit

> Connect Replit Agent to Context.dev for live web research, scraping, and company data.

Connect Context.dev to Replit Agent through the Model Context Protocol (MCP). Ask Agent to search the web, read websites, map a site's URLs, or bring company logos and brand data into your app.

> [card] [Add Context.dev to Replit](https://replit.com/~?settings.show=true\&settings.tab=integrations\&connector=predefined-context_dev)
>
> Open the Context.dev integration in your Replit settings.

## Prerequisites

* A [Replit account](https://replit.com) with access to Agent
* A [Context.dev account](https://context.dev/signup)

## Install and connect

**1. Open the integration**

Select **Add Context.dev to Replit** above while signed in to Replit. You can also open [Integrations](https://replit.com/integrations) and find Context.dev under **MCP Servers for Replit Agent**.

**2. Authorize Context.dev**

Select **Sign in** for Context.dev. Complete the Context.dev sign-in and authorization prompts, then return to Replit.

**3. Start an Agent chat**

Confirm that the connection shows as connected, then open a project and start an Agent chat. Replit automatically discovers the server's tools and makes them available across your projects.

> [!NOTE]
>
> Context.dev uses browser-based OAuth for MCP. You do not need to create or paste an API key into Replit for this connection.

> [accordion] Connect manually if the integration link is unavailable
>
> In Replit's [Integrations](https://replit.com/integrations), select **+ Add MCP server**. Set **Display name** to `Context.dev` and **MCP Server URL** to:
>
> ```text theme={null}
> https://mcp.context.dev/mcp
> ```
>
> Leave custom headers empty. Select **Test & save** and complete Context.dev's OAuth flow.

## Verify the setup

Ask Agent to make a request whose result you can inspect:

```text theme={null}
Use Context.dev to scrape https://www.context.dev and return the page title and source URL. Use the connected tool.
```

Confirm that Agent shows a successful Context.dev tool call with live output. If Replit asks for confirmation before running the tool, review and approve the request.

## Use Context.dev in Agent

Name Context.dev in your prompt and describe the result you want:

```text theme={null}
Use Context.dev to retrieve the Brand profile and Styleguide for linear.app, then build a landing page using its logo, colors, and fonts.
```

```text theme={null}
Use Context.dev to find Stripe's latest official product announcements. Summarize them and include the source URLs.
```

## Troubleshooting

| Symptom | Fix |
| - | - |
| Sign-in does not finish | Return to Replit's Integrations page, select Context.dev, and complete the browser authorization flow. |
| Agent answers without calling Context.dev | Check the connection status in Integrations, then explicitly request a live Context.dev tool call in chat. |
| Calls fail for insufficient credits | Review usage in the [Context.dev dashboard](https://context.dev/dashboard). |

## Reference

> [card] [Replit MCP setup](https://docs.replit.com/build/connect-via-mcp)
>
> Official instructions for connecting MCP servers and using their tools in Agent.

> [card] [Context.dev MCP guide](https://docs.context.dev/install-mcp.md)
>
> Hosted server capabilities, authentication, and usage details.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.