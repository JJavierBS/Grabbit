# Composio

> Connect Context.dev to your agent framework through Composio for web scraping, document parsing, and brand data.

Use the Context.dev toolkit in Composio to give your agents web and company data. Connect your Context.dev API key, then use the toolkit through Composio's SDKs or a hosted Model Context Protocol (MCP) session.

> [card] [Open Context.dev on Composio](https://composio.dev/toolkits/context_dev)
>
> Explore the toolkit and try its tools in Composio's playground.

## Prerequisites

* A [Context.dev account](https://context.dev/signup) with an API key
* A [Composio account](https://dashboard.composio.dev) with a project API key
* A TypeScript or Python project for the SDK examples below

## Install and connect

**1. Create a Context.dev auth config**

In the [Composio dashboard](https://dashboard.composio.dev), open **Platform → Auth Configs → Create Auth Config**. Choose **Context.dev** (`context_dev`) and **API Key**, then save the configuration. Copy its auth config ID, which starts with `ac_`.

Create this configuration once and reuse its ID. To test in Composio's playground, open the configuration, select **Connect Account**, and enter your Context.dev API key from the [Context.dev dashboard](https://context.dev/dashboard).

**2. Install the Composio SDK**

```bash TypeScript theme={null}
npm install @composio/core
```

```bash Python theme={null}
pip install composio
```

Set your Composio project API key and the auth config ID in your server environment:

```bash theme={null}
export COMPOSIO_API_KEY="your_composio_api_key"
export COMPOSIO_CONTEXT_AUTH_CONFIG_ID="ac_your_context_dev_config"
```

The Composio API key authenticates your application to Composio. Enter your separate Context.dev API key when connecting the account.

**3. Connect an application user**

Create a session restricted to `context_dev`. Replace `user_123` with a stable user ID from your application, then open the printed connection URL and enter that user's Context.dev API key.

```typescript TypeScript theme={null}
import { Composio } from "@composio/core";

const composio = new Composio({
  apiKey: process.env.COMPOSIO_API_KEY!,
});

const session = await composio.create("user_123", {
  toolkits: ["context_dev"],
  authConfigs: {
    context_dev: process.env.COMPOSIO_CONTEXT_AUTH_CONFIG_ID!,
  },
  mcp: true,
});

const connection = await session.authorize("context_dev");
console.log("Connect Context.dev:", connection.redirectUrl);
await connection.waitForConnection();

const mcpUrl = session.mcp.url;
const mcpHeaders = session.mcp.headers;
```

```python Python theme={null}
import os
from composio import Composio

composio = Composio(api_key=os.environ["COMPOSIO_API_KEY"])

session = composio.create(
    user_id="user_123",
    toolkits=["context_dev"],
    auth_configs={
        "context_dev": os.environ["COMPOSIO_CONTEXT_AUTH_CONFIG_ID"],
    },
    mcp=True,
)

connection = session.authorize("context_dev")
print("Connect Context.dev:", connection.redirect_url)
connection.wait_for_connection()

mcp_url = session.mcp.url
mcp_headers = session.mcp.headers
```

Composio stores the connected account for that user. Reuse the same user ID in later sessions. The dashboard's **Connect Account** button creates a playground connection; use the SDK connection flow above for your application's users.

**4. Add the session to your framework**

Pass `session.mcp.url` and `session.mcp.headers` to your framework's HTTP MCP client. Follow Composio's [MCP framework examples](https://docs.composio.dev/docs/sessions-via-mcp) for the client configuration.

For native framework tools, use a [Composio provider](https://docs.composio.dev/docs/providers) and register the tools returned by `session.tools()`. Keep the same toolkit, auth config, and user ID when creating that session.

## Verify the setup

Ask your agent, or the Composio playground, to make a request you can inspect:

```text theme={null}
Use Context.dev to scrape https://www.context.dev and return the page title and source URL. Use the connected tool.
```

Confirm that `CONTEXT_DEV_SCRAPE_WEBPAGE_MARKDOWN` returns live output.

## Available tools

The [Composio toolkit reference](https://docs.composio.dev/toolkits/context_dev) lists every tool and its input schema. Common tools:

| Tool | Use it to |
| - | - |
| `CONTEXT_DEV_SCRAPE_WEBPAGE_MARKDOWN` | Read a webpage as Markdown. |
| `CONTEXT_DEV_PARSE_FILE` | Convert a file to Markdown. |
| `CONTEXT_DEV_GET_BRAND` | Retrieve a company's brand profile. |
| `CONTEXT_DEV_SEARCH_BRANDS` | Find brands by a name or domain prefix. |
| `CONTEXT_DEV_GET_WEBSITE_STYLEGUIDE` | Extract a website's design styles. |
| `CONTEXT_DEV_LIST_BATCHES` | Find existing batch jobs. |
| `CONTEXT_DEV_LIST_MONITORS` | Find existing website monitors. |
| `CONTEXT_DEV_GET_MONITOR_LIMITS` | Check monitor usage and limits. |

## Troubleshooting

| Symptom | Fix |
| - | - |
| The connection URL expires | Run `session.authorize()` again and finish connecting before the wait times out. |
| An auth config or connection is missing | Check that the Composio API key and auth config belong to the same project, and reuse the user ID used during authorization. |
| The Context.dev key is rejected | Copy an active API key from the Context.dev dashboard into the connection form. |
| Calls fail for insufficient credits | Check usage in the [Context.dev dashboard](https://context.dev/dashboard). |

## Reference

> [card] [Composio framework providers](https://docs.composio.dev/docs/providers)
>
> Use Context.dev tools with your agent framework's native tool interface.

> [card] [Composio authentication](https://docs.composio.dev/docs/authentication/manually-authenticating)
>
> Manage connection links and account status for your users.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.