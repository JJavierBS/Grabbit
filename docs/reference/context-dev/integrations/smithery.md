# Smithery

> Install Context.dev through Smithery or call its tools from the Smithery CLI.

Find Context.dev in the Smithery registry as `context/contextdotdev`. Use the listing to add web and company data tools to an MCP client, or call the tools directly from Smithery's CLI.

> [card] [Open Context.dev on Smithery](https://smithery.ai/servers/context/contextdotdev)
>
> Review the current server endpoint, tools, and input schemas in the Smithery registry.

## Prerequisites

* [Node.js 20 or newer](https://nodejs.org/en/download)
* A Context.dev account for browser authorization
* A Smithery account when using managed Smithery connections or CLI tool calls

> [!NOTE]
>
> Context.dev authentication uses OAuth. You do not need to create or paste a Context.dev API key into Smithery or an MCP client.

## Install in an MCP client

Use this path when you want Context.dev tools inside Cursor, Claude Code, Codex, VS Code, Windsurf, or another client supported by the Smithery CLI.

**1. Install the Smithery CLI**

```bash theme={null}
npm install -g smithery@latest
```

**2. Add Context.dev to your client**

Run one command for the client you use:

```bash theme={null}
# Cursor
smithery mcp add context/contextdotdev --client cursor

# Claude Code
smithery mcp add context/contextdotdev --client claude-code

# Codex
smithery mcp add context/contextdotdev --client codex

# VS Code
smithery mcp add context/contextdotdev --client vscode
```

The CLI writes the MCP server into that client's configuration. Run only the command for your client.

**3. Authorize and reload**

Complete the Context.dev authorization flow when the client opens it, then restart or reload the client so it discovers the new tools.

Verify the installation with a read-only request in the client:

```text theme={null}
Use Context.dev to scrape https://www.context.dev and return only the page title and source URL.
```

## Use Context.dev from the Smithery CLI

Use this path to let Smithery manage the connection and call Context.dev tools directly from a terminal.

**1. Sign in to Smithery**

```bash theme={null}
smithery auth login
smithery auth whoami
```

**2. Create the connection**

```bash theme={null}
smithery mcp add context/contextdotdev --id context
```

Smithery opens the browser authorization flow. If the browser does not open, visit the setup URL printed by the CLI. The stable `context` ID is used by later commands.

**3. List the available tools**

```bash theme={null}
smithery tool list context
```

**4. Make a test call**

```bash theme={null}
smithery tool call context web-scrape \
  '{"url":"https://www.context.dev","formats":{"markdown":true}}'
```

## Common tools

| Need | Tool |
| - | - |
| Find current sources | `web-search` |
| Read a known page | `web-scrape` with `formats.markdown` or `formats.html` |
| Find URLs on a website | `web-map` |
| Crawl several pages | `web-crawl` |
| Retrieve company data | `get-brand` or `brand-retrieve-unified` |
| Track website changes | Monitor tools such as `create-monitor` and `list-monitor-changes` |
| Process a large URL set | Batch tools such as `submit-batch` and `get-batch-results` |

To discover a site's URLs and available page metadata, ask your connected client:

```text theme={null}
Use Context.dev to map all URLs for example.com.
```

> [!WARNING]
>
> Creating, updating, running, or deleting monitors and batches changes persistent Context.dev account state. Request those operations explicitly and inspect their arguments before running them.

## Data path

Smithery connects through `https://contextdotdev--context.run.tools`, which proxies the hosted Context.dev MCP server. Smithery manages the connection and OAuth tokens; Context.dev executes the tools. Review [Smithery Connect security](https://smithery.ai/docs/use/connect) before sending sensitive data through this path.

## Troubleshooting

| Symptom | Fix |
| - | - |
| `smithery` is not found | Install Node.js 20 or newer, then rerun `npm install -g smithery@latest`. |
| The connection remains `auth_required` | Rerun `smithery mcp add context/contextdotdev --id context` and complete the printed setup URL. |
| A client does not show Context.dev tools | Reload the client, then confirm the install with `smithery mcp list --client <client-name>`. |
| `smithery tool list context` cannot find the connection | Run `smithery mcp list`, check the connection ID, and pass that ID instead of `context`. |
| Tool calls fail for insufficient credits | Review usage in the [Context.dev dashboard](https://context.dev/dashboard); repeated retries will not add credits. |

## Reference

> [card] [Smithery listing](https://smithery.ai/servers/context/contextdotdev)
>
> Live Context.dev tool catalog and schemas on Smithery.

> [card] [Smithery Connect docs](https://smithery.ai/docs/use/connect)
>
> Connection lifecycle, OAuth, credential storage, and direct tool calls.

> [card] [Smithery CLI source](https://github.com/smithery-ai/cli)
>
> Current install, connection, client, and tool commands.

> [card] [Context.dev MCP guide](https://docs.context.dev/install-mcp.md)
>
> Hosted MCP capabilities and authentication details.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.