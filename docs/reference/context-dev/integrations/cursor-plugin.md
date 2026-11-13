# Cursor

> Add Context.dev tools and API guidance to Cursor with the marketplace plugin.

The Context.dev plugin combines live web tools with skills, commands, and rules for API development. Use it to research websites in Cursor or build Context.dev into your application.

> [card] [Install Context.dev for Cursor](https://cursor.com/marketplace/context.dev)
>
> Open the official Cursor Marketplace listing.

## Install and connect

**1. Install the plugin**

Open the [Context.dev Marketplace listing](https://cursor.com/marketplace/context.dev), select **Install**, and choose a user or project scope.

You can also run this in Cursor Agent:

```text theme={null}
/add-plugin context-dev
```

**2. Enable the MCP server**

Open **Customize → MCPs** (older versions: **Cursor Settings → Tools & MCP**), find the `context` server installed by the plugin, and enable it.

**3. Authorize Context.dev**

Select **Connect** or **Authenticate**. Cursor opens Context.dev in your browser. Sign in and approve access, then return to Cursor and confirm that the server lists its tools.

**4. Start a new Agent chat**

Plugin skills, rules, and commands load into new chats after installation. Open a new chat before testing the integration.

> [!NOTE]
>
> Cursor's interactive Context.dev tools use OAuth. Do not put an API key, bearer token, or custom header in the plugin's `mcp.json`.

## Verify the setup

Send a read-only request:

```text theme={null}
Use Context.dev to scrape https://www.context.dev and return the page title and source URL.
```

Cursor should call `web-scrape`. A successful result confirms that the plugin loaded, the `context` server is enabled, and OAuth completed.

## Use the plugin

Describe the result directly or use one of the bundled commands:

| Command | Use it for |
| - | - |
| `/search-web` | Find current sources when you do not know the URL |
| `/scrape-url` | Read a known page as Markdown |
| `/extract-web-data` | Extract structured JSON from a page with a task-specific schema |
| `/brand-colors` | Retrieve a company's detected brand colors |

Example requests:

```text theme={null}
Use Context.dev to find Stripe's latest official product announcements and cite the source URLs.
```

```text theme={null}
Use Context.dev to scrape this careers page and return every open engineering role as JSON with title, location, team, and application URL.
```

```text theme={null}
Use Context.dev to retrieve the brand profile for linear.app, including its logo, colors, and social profiles. Retrieve the Styleguide for fonts.
```

> [!WARNING]
>
> Monitor and batch tools can create or change persistent account state. Ask for create, update, run, cancel, or delete operations explicitly and review the call before approving it.

## Build with the API

OAuth authenticates Cursor's MCP tools. Code that you write to call the Context.dev REST API or SDKs directly uses a separate secret key from the [Context.dev dashboard](https://context.dev/dashboard). Store that key server-side as `CONTEXT_DEV_API_KEY`; never put it in browser code or commit it to source control.

## Troubleshooting

| Symptom | Fix |
| - | - |
| The `context` server is missing | Refresh or reinstall the plugin, then run **Developer: Reload Window**. |
| An older manual Context.dev server also appears | Remove the older manual server, then refresh the marketplace plugin. |
| Cursor reports `401` or authentication required | Disconnect `context`, reconnect it, and complete browser authorization again. |
| Tools remain unavailable after OAuth | Reload the Cursor window, re-enable `context`, and start a new Agent chat. |
| Calls fail for insufficient credits | Review usage in the [Context.dev dashboard](https://context.dev/dashboard); repeated retries will not add credits. |

## Reference

> [card] [Plugin source](https://github.com/context-dot-dev/cursor-plugin)
>
> Inspect the manifest, MCP configuration, skills, commands, and rules.

> [card] [Cursor plugin docs](https://cursor.com/docs/plugins)
>
> Installation scopes and plugin management in Cursor.

> [card] [Context.dev MCP guide](https://docs.context.dev/install-mcp.md)
>
> Hosted server tools and authentication details.

> [card] [Context.dev API quickstart](https://docs.context.dev/quickstart.md)
>
> Add Context.dev to application code with an SDK or REST.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.