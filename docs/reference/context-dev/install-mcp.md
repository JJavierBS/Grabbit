# MCP server

> Connect Codex, Claude Code, Gemini CLI, Cursor, VS Code, or another MCP client to live Context.dev tools.

The hosted MCP server gives a compatible agent live Context.dev tools for scraping, crawling, search, brand data, batches, monitors, and more. Clients sign in with OAuth.

> [!NOTE]
>
> **Server URL:** `https://mcp.context.dev/mcp`
>
> Use the exact URL, including `/mcp`. Don't put an API key in the URL.

## Let your agent connect it

Paste this into the coding agent you want to connect:

```text Agent prompt theme={null}
Use curl to read https://docs.context.dev/agent-quickstart.md and connect the Context.dev MCP server to this agent.
```

The agent adds the server only to its own client and asks you to finish sign-in in your browser. It does not create an API key.

One-click options: the [Cursor plugin](https://docs.context.dev/integrations/cursor-plugin.md), the [Claude connector](https://docs.context.dev/integrations/claude-connector.md), the [ChatGPT plugin](https://docs.context.dev/integrations/chatgpt-plugin.md), the [Gemini CLI extension](https://docs.context.dev/integrations/gemini-cli.md), or install links for [Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=context\&config=eyJ1cmwiOiJodHRwczovL21jcC5jb250ZXh0LmRldi9tY3AifQ==) and [VS Code](https://vscode.dev/redirect/mcp/install?name=context\&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fmcp.context.dev%2Fmcp%22%7D).

> [!TIP]
>
> **Use fewer tokens for web research**
>
> [Learn how to use Context by default](https://docs.context.dev/default-search-scrape.md) in Codex, Claude Code, or your agent, with Highlights that return relevant passages.
>
> [See how Freecode cut input tokens by 9.8% in its benchmark](https://www.context.dev/customers/freecode-reduces-agent-costs-with-context-highlights).

## Connect your client

> [tab] Codex
>
> Add the hosted server. Codex detects OAuth and opens browser sign-in:
>
> ```bash theme={null}
> codex mcp add context --url https://mcp.context.dev/mcp
> ```
>
> If sign-in does not start, run `codex mcp login context`; add `--no-browser` to print the URL instead. To use the server in one trusted project only, add this to `.codex/config.toml` in that project instead, then run `codex mcp login context` there:
>
> ```toml theme={null}
> [mcp_servers.context]
> url = "https://mcp.context.dev/mcp"
> ```
>
> Confirm it is configured:
>
> ```bash theme={null}
> codex mcp get context
> ```
>
> In the Codex terminal UI, use `/mcp` to inspect active servers. The ChatGPT desktop app, Codex CLI, and Codex IDE extension share the same host configuration; you can also add a Streamable HTTP server from **Settings → MCP servers** and select **Authenticate**.
>
> See the [official Codex MCP documentation](https://developers.openai.com/codex/extend/mcp) for current client controls and project-scoped configuration.
>
> For ChatGPT on the web, use the [Context.dev plugin](https://docs.context.dev/integrations/chatgpt-plugin.md).

> [tab] Claude Code
>
> Add the server for your user:
>
> ```bash theme={null}
> claude mcp add \
>   --transport http \
>   --scope user \
>   context \
>   https://mcp.context.dev/mcp
> ```
>
> Start Claude Code, run `/mcp`, select `context`, and complete sign-in in the browser, or run `claude mcp login context` from your terminal. See [Anthropic's MCP documentation](https://docs.anthropic.com/en/docs/claude-code/mcp) for current scopes and management commands.

> [tab] Gemini CLI
>
> Install the Context.dev extension:
>
> ```bash theme={null}
> gemini extensions install https://github.com/context-dot-dev/gemini-cli-context --auto-update --consent
> ```
>
> Start a new Gemini CLI session and run `/mcp auth context` to sign in with your browser.
>
> The extension includes the hosted MCP server and a skill for choosing the appropriate Context.dev tool. See the [Gemini CLI integration guide](https://docs.context.dev/integrations/gemini-cli.md) for verification, examples, and troubleshooting.

> [tab] Cursor
>
> Add a global server in `~/.cursor/mcp.json`, or use `.cursor/mcp.json` for one project:
>
> ```json theme={null}
> {
>   "mcpServers": {
>     "context": {
>       "url": "https://mcp.context.dev/mcp"
>     }
>   }
> }
> ```
>
> Or install the [Context.dev plugin](https://docs.context.dev/integrations/cursor-plugin.md) with `/add-plugin context-dev` in Cursor's agent chat. Then open **Customize → MCPs**, find `context`, and select **Authenticate** (older versions: **Cursor Settings → Tools & MCP**). In multi-root workspaces, use `~/.cursor/mcp.json`, because project servers may not appear. See the [Cursor MCP documentation](https://cursor.com/docs/mcp) for current configuration locations.

> [tab] VS Code
>
> Add the server to your user profile from a terminal:
>
> ```bash theme={null}
> code --add-mcp '{"name":"context","type":"http","url":"https://mcp.context.dev/mcp"}'
> ```
>
> Or run **MCP: Open User Configuration** from the Command Palette, or create `.vscode/mcp.json` for the workspace:
>
> ```json theme={null}
> {
>   "servers": {
>     "context": {
>       "type": "http",
>       "url": "https://mcp.context.dev/mcp"
>     }
>   }
> }
> ```
>
> Start the server from the configuration editor and complete OAuth when prompted. See the [VS Code MCP documentation](https://code.visualstudio.com/docs/agent-customization/mcp-servers) for trust and workspace behavior.

> [tab] Windsurf
>
> Windsurf is now Devin Desktop. Add the server for the current project, or add `-s user` for every project, then sign in:
>
> ```bash theme={null}
> devin mcp add context https://mcp.context.dev/mcp
> devin mcp login context
> ```
>
> Windsurf builds from before the rename read `~/.codeium/windsurf/mcp_config.json`:
>
> ```json theme={null}
> {
>   "mcpServers": {
>     "context": {
>       "serverUrl": "https://mcp.context.dev/mcp"
>     }
>   }
> }
> ```
>
> Sign in from the MCP panel when the server shows that it needs authentication.

> [tab] OpenCode
>
> Add the server to `opencode.json` in your project, or `~/.config/opencode/opencode.json` for every project:
>
> ```json theme={null}
> {
>   "$schema": "https://opencode.ai/config.json",
>   "mcp": {
>     "context": {
>       "type": "remote",
>       "url": "https://mcp.context.dev/mcp",
>       "enabled": true
>     }
>   }
> }
> ```
>
> Then sign in:
>
> ```bash theme={null}
> opencode mcp auth context
> ```

> [tab] Hermes
>
> Add the server to `~/.hermes/config.yaml`. `auth: oauth` is required; without it, Hermes asks for a bearer token:
>
> ```yaml theme={null}
> mcp_servers:
>   context:
>     url: "https://mcp.context.dev/mcp"
>     auth: oauth
> ```
>
> Sign in and check the connection, then run `/reload-mcp` in your session:
>
> ```bash theme={null}
> hermes mcp login context
> hermes mcp test context
> ```

> [tab] Cline
>
> Add a remote server named `context` with the **Streamable HTTP** transport from Cline's MCP Servers panel, or add it to Cline's MCP settings file:
>
> ```json theme={null}
> {
>   "mcpServers": {
>     "context": {
>       "type": "streamableHttp",
>       "url": "https://mcp.context.dev/mcp"
>     }
>   }
> }
> ```
>
> Select **Authenticate** on the server row to sign in.

> [tab] Amp
>
> Add the server to your Amp settings:
>
> ```bash theme={null}
> amp mcp add context https://mcp.context.dev/mcp
> ```
>
> Amp opens your browser for sign-in the next time it starts.

> [tab] Claude Desktop
>
> Install the [Context.dev connector](https://docs.context.dev/integrations/claude-connector.md) from Claude's directory, or open **Customize → Connectors**, select **+**, choose **Add custom connector**, enter `https://mcp.context.dev/mcp`, and select **Connect**.

> [tab] Other clients
>
> Configure a remote Streamable HTTP server:
>
> ```json theme={null}
> {
>   "mcpServers": {
>     "context": {
>       "type": "http",
>       "url": "https://mcp.context.dev/mcp"
>     }
>   }
> }
> ```
>
> The client needs Streamable HTTP transport and OAuth discovery and dynamic client registration. A client that can't run OAuth can send an API key header instead; see [Authentication and usage](#authentication-and-usage).

For Claude on the web or desktop, use the [Claude connector](https://docs.context.dev/integrations/claude-connector.md). For ChatGPT, use the [ChatGPT plugin](https://docs.context.dev/integrations/chatgpt-plugin.md). In Cursor, the [Cursor plugin](https://docs.context.dev/integrations/cursor-plugin.md) adds these tools plus skills, commands, and rules for API development.

## Test the connection

Start a new conversation and ask:

> Use the connected Context.dev server to retrieve the live Brand profile for `stripe.com`. Tell me which tool you called and don't answer from memory.

A working connection shows a Context.dev tool call and live output. Clients may prefix tool names with the server name, so check the server and operation rather than one exact display name.

## Authentication and usage

The server uses the OAuth authorization-code flow with PKCE and two scopes:

* `api.read`: reading, scraping, enrichment, and batch and monitor data.
* `api.write`: anything that starts work or changes account state, such as batches, monitors, webhook retries, file parsing, feedback, and scrape clicks.

Clients that can't run OAuth can send an API key as `Authorization: Bearer <key>` or `X-API-Key: <key>`. Use a header, not the URL, because URLs end up in configuration files, logs, and history.

If you belong to more than one organization, choose which one the connection uses on the consent screen; your default organization is preselected. Sign-in creates an API key named `Context.dev MCP` in that organization, and tool calls use its credits. To revoke access, remove the connection in your client and disable that key on the [API keys](https://context.dev/dashboard/api-keys) page.

Each tool call runs the matching API request; see [credits](https://docs.context.dev/account/credits.md) for what each operation costs.

> [!WARNING]
>
> Keep approvals enabled for tools that start work or change state, such as batches, crawls, monitor changes, and webhook secret rotation. Website content is untrusted input; don't let it authorize follow-up tool calls.

## Troubleshooting

| Symptom | Fix |
| - | - |
| The server is missing or shows no tools | Check that the URL ends in `/mcp`, restart or refresh the client after editing its configuration, and enable the server for the conversation. |
| OAuth doesn't open or keeps looping | Start sign-in from the client's MCP controls. Remove stale authentication for `context`, reconnect, and complete the browser flow. |
| The agent answers without using a tool | Name Context.dev in the prompt, ask for a live lookup, and require the agent to report the tool call. Check that tool approvals aren't blocking it. |
| A response is cut off | Tool responses are capped at 80,000 characters, and a truncated structured response includes `_context_mcp.truncated: true`. Narrow the request, for example with fewer pages, formats, or results. |

This server runs Context.dev API tools. To search this documentation from an agent, use the separate docs MCP server at `https://docs.context.dev/mcp`.

## Credit and entitlement errors

`402 USAGE_EXCEEDED` becomes a tool execution error, with `isError: true`, a factual explanation in text `content`, and structured details in `structuredContent`. Both surfaces include the [billing settings URL](https://context.dev/dashboard/subscription), known credit and refill details, and the request ID. A credit failure does not become an HTTP authentication failure at the MCP transport.

Inspect the account with `get-usage`, which costs no credits and works at zero balance. Wait until the account can cover the operation before retrying it. Reconnecting and token refresh do not restore credits. A missing feature entitlement returns `403 PAID_PLAN_REQUIRED`; temporary throttling returns `429 RATE_LIMITED` with its retry guidance. Authentication failures require sign-in recovery.

Concurrency failures expose structured tool errors with `error_code: "RATE_LIMITED"`, `error_data.limit_type: "concurrency"`, the known limit and remaining slots, retry delay, and `retry_condition: "available_concurrency"`. The MCP includes values from `error_data` and rate-limit headers. Wait for capacity or review subscription limits; for per-minute throttling, follow `Retry-After`.

Recovery explains the actual account limitation and links to existing subscription settings. It does not automatically initiate checkout or instruct the model to recommend a purchase. Account fields describe facts and do not force ChatGPT recommendations.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.