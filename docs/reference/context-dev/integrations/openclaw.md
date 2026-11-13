# OpenClaw

> Add web search and scraping to OpenClaw, or connect the full Context.dev MCP server.

The Context.dev plugin adds web search and scraping to OpenClaw. Connect the hosted MCP server as well when you need company data, document parsing, or other Context.dev tools.

> [card] [Install Context.dev from ClawHub](https://clawhub.ai/plugins/@contextdev/openclaw-context)
>
> Review the current package, compatibility, and source before installing.

## Choose an access level

| Access | Authentication | Use it for |
| - | - | - |
| OpenClaw plugin | `CONTEXT_API_KEY` in the Gateway environment | Native `web_search` and `web_fetch`, plus `context_search` and `context_scrape` |
| Hosted MCP server | Browser-based OAuth | The complete public Context.dev tool catalog |

You can use either path or enable both.

## Install the plugin

**1. Install from ClawHub**

```bash theme={null}
openclaw plugins install clawhub:@contextdev/openclaw-context
```

**2. Configure the API key**

Create a secret key in the [Context.dev dashboard](https://context.dev/dashboard), then set it as `CONTEXT_API_KEY` in the environment that starts the OpenClaw Gateway.

For a Gateway started from the same shell:

```bash theme={null}
export CONTEXT_API_KEY=ctxt_secret_your_key
openclaw gateway restart
```

If OpenClaw runs as a background service, container, or process manager, set the variable in that service's environment and restart it there. A shell-only export will not update an already-running Gateway.

**3. Test native search and scraping**

Send the agent a read-only request:

```text theme={null}
Use context_search to find the latest official OpenClaw release notes and return the source URLs.
```

For a known page, ask it to use `context_scrape` instead.

## Connect the full MCP catalog

The plugin's native tools cover search and single-page scraping. Add the hosted MCP server when the agent also needs crawling, URL mapping, document parsing, brand data, monitors, screenshots, or batches.

```bash theme={null}
openclaw mcp add context \
  --url https://mcp.context.dev/mcp \
  --transport streamable-http \
  --auth oauth \
  --parallel \
  --connect-timeout 30 \
  --timeout 180 \
  --no-probe

openclaw mcp login context
```

Complete the Context.dev authorization flow in the browser. No API key is required for this MCP connection.

Verify the connection and list its tools:

```bash theme={null}
openclaw mcp probe context
```

## Use the integration

```text theme={null}
Use Context.dev to crawl the authentication section of this documentation site and summarize the setup paths with source URLs.
```

```text theme={null}
Use Context.dev to retrieve the brand profile for linear.app, including logos, colors, and social profiles. Retrieve the Styleguide for fonts.
```

```text theme={null}
Use Context.dev to scrape this pricing page and return the current tiers as JSON with name, price, and limits.
```

> [!WARNING]
>
> Creating, updating, running, or deleting monitors and batches changes persistent account state. Ask for those operations explicitly and review the proposed action before it runs.

## Troubleshooting

| Symptom | Fix |
| - | - |
| ClawHub rejects the installation | Update OpenClaw to a version supported by the plugin's current package metadata, then install again. |
| Native tools return an authentication error | Confirm `CONTEXT_API_KEY` is present in the Gateway process environment, then restart the Gateway. |
| MCP tools return `401` or request authorization | Run `openclaw mcp login context` and complete OAuth again. |
| MCP tools are missing | Run `openclaw mcp probe context` and confirm the connection is enabled and reachable. |

## Reference

> [card] [Plugin source](https://github.com/context-dot-dev/openclaw-context)
>
> README, package metadata, manifest, and release source.

> [card] [OpenClaw documentation](https://docs.openclaw.ai/)
>
> Gateway, plugins, environment, and MCP configuration.

> [card] [Context.dev MCP guide](https://docs.context.dev/install-mcp.md)
>
> Hosted MCP capabilities and OAuth behavior.

> [card] [Context.dev dashboard](https://context.dev/dashboard)
>
> Create an API key and review usage.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.