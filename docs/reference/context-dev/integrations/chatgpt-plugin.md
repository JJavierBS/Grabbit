# ChatGPT

> Search the web, read pages, and retrieve company data from a ChatGPT conversation.

Connect the Context.dev plugin to give ChatGPT access to live web and company data. Sign in with your Context.dev account, then ask for a result in a new conversation.

> [card] [Install Context.dev in ChatGPT](https://chatgpt.com/plugins/plugin_asdk_app_6a70eca71e948191aea49dbb9b674477)
>
> Open the public Context.dev listing in ChatGPT's plugin directory.

## Install and connect

**1. Install the plugin**

Open the [Context.dev plugin listing](https://chatgpt.com/plugins/plugin_asdk_app_6a70eca71e948191aea49dbb9b674477) while signed in to ChatGPT, then select the plus button to install it.

**2. Authorize Context.dev**

Connect the Context.dev account when ChatGPT prompts you during installation or on the first tool call. Sign in to Context.dev in the browser and approve the requested access.

**3. Start a new chat**

Installed plugin tools become available to new chats. Start a new Chat or Work conversation after installation.

> [!NOTE]
>
> The plugin uses Context.dev's browser-based OAuth connection. You do not need to create or paste a Context.dev API key into ChatGPT.

## Verify the setup

Start with a request whose result you can inspect:

```text theme={null}
@Context.dev Scrape https://www.context.dev and return the page title and source URL. Use the connected tool.
```

Confirm that ChatGPT shows a successful Context.dev tool call. An answer without a tool call does not verify the connection.

## Use the plugin

Describe the outcome directly, or type `@` and choose **Context.dev** when you want to invoke it explicitly.

```text theme={null}
@Context.dev Search for OpenAI's latest official Apps SDK announcements. Summarize them and cite the source URLs.
```

```text theme={null}
@Context.dev Scrape https://example.com/pricing and return every plan as JSON with name, price, and limits.
```

```text theme={null}
@Context.dev Retrieve the brand profile for linear.app, including its logos, colors, and social profiles. Retrieve the Styleguide for fonts.
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
| Context.dev does not appear in the prompt's `@` menu | Confirm the plugin is installed, then start a new chat. |
| ChatGPT asks you to connect repeatedly | Reopen the plugin details, reconnect Context.dev, and finish the browser consent flow before returning to the chat. |
| A tool is unavailable in a managed workspace | Ask the workspace administrator whether that plugin or connector is allowed. |
| Calls fail for insufficient credits | Ask for `get-usage` (free), then review [credit and entitlement information](https://docs.context.dev/account/billing.md). `402 USAGE_EXCEEDED` does not require reconnection; wait for sufficient credits. |

A missing paid-feature entitlement is separate from credit exhaustion. The plugin explains the limitation and links to informational documentation, following the [OpenAI plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines). It does not initiate checkout or require a purchase recommendation.

## Reference

> [card] [Use plugins in ChatGPT](https://learn.chatgpt.com/docs/plugins)
>
> Official OpenAI instructions for installing, connecting, invoking, and removing plugins.

> [card] [Context.dev MCP guide](https://docs.context.dev/install-mcp.md)
>
> The capabilities and authentication model behind the plugin.

> [card] [Context.dev documentation](https://docs.context.dev/introduction.md)
>
> Guides and API references for each underlying operation.

> [card] [Get support](mailto:hello@context.dev)
>
> Contact Context.dev if the connection or a tool call fails.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.