# Claude

> Connect Claude to Context.dev for live web research and company data.

Use the Context.dev connector to search and read websites, parse documents, and look up companies in Claude. Connect your account once, then enable it in the conversation where you need it.

> [card] [Connect Context.dev to Claude](https://claude.ai/directory/context-dev)
>
> Open the official Context.dev listing in Claude's Connectors Directory.

## Install and connect

**1. Connect Context.dev**

Open the [Context.dev connector listing](https://claude.ai/directory/context-dev) while signed in to Claude, then select **Connect**.

**2. Authorize your account**

Sign in to Context.dev when prompted and approve access. Claude returns you to the connector after authorization finishes.

**3. Enable the connector in a chat**

Start a new chat. Open the **+** menu, choose **Connectors**, and make sure **Context.dev** is enabled for the conversation.

> [!NOTE]
>
> The connector uses Context.dev's browser-based OAuth flow. You do not need to create or paste an API key into Claude.

## Verify the setup

Start with a request whose result you can inspect:

```text theme={null}
Use Context.dev to scrape https://www.context.dev and return the page title and source URL. Use the connected tool.
```

Confirm that Claude shows a successful Context.dev tool call. An answer without a tool call does not verify the connection.

## Use the connector

Ask Claude for the outcome you want and name Context.dev when you want to invoke the connector explicitly.

```text theme={null}
Use Context.dev to find Stripe's latest official product announcements. Summarize them and cite the source URLs.
```

```text theme={null}
Use Context.dev to scrape https://example.com/pricing and return every plan as JSON with name, price, and limits.
```

```text theme={null}
Use Context.dev to retrieve the brand profile for linear.app, including its logos, colors, and social profiles. Retrieve the Styleguide for fonts.
```

Use the narrowest operation that fits the task:

| Task | Ask Context.dev to |
| - | - |
| You do not know the source URL | Search the web and return cited results |
| You know the exact page | Scrape it as Markdown or rendered HTML |
| The answer spans one site | Map its URLs or run a focused crawl |
| You need a visual record of a page | Capture a screenshot |
| You have a PDF or other document | Parse the file into Markdown |
| You need recurring checks | Create a website monitor |
| You have a large URL collection | Submit an asynchronous batch |

> [!WARNING]
>
> Creating, updating, running, or deleting monitors and batches changes persistent Context.dev account state. Request those actions explicitly and review the tool call before approving it.

## Troubleshooting

| Symptom | Fix |
| - | - |
| Context.dev is missing from the chat's connector menu | Confirm the connector is connected, then start a new chat and enable it from **+ → Connectors**. |
| Claude asks you to connect repeatedly | Disconnect Context.dev, reconnect it from the directory listing, and complete the browser consent flow before returning to Claude. |
| The connector is unavailable in a managed workspace | Ask the workspace owner to allow Context.dev in the organization's connector settings. |
| Calls fail for insufficient credits | Review usage in the [Context.dev dashboard](https://context.dev/dashboard); repeated retries will not add credits. |

## Reference

> [card] [Context.dev connector](https://claude.ai/directory/context-dev)
>
> Open the official listing in Claude's Connectors Directory.

> [card] [Use connectors in Claude](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)
>
> Official instructions for connecting, enabling, and managing services in Claude.

> [card] [Context.dev MCP guide](https://docs.context.dev/install-mcp.md)
>
> Review the capabilities and OAuth model behind the connector.

> [card] [Get support](mailto:hello@context.dev)
>
> Contact Context.dev if authorization or a tool call fails.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.