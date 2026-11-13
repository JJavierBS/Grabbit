# Gemini CLI

> Add Context.dev live web and document intelligence to Gemini CLI with the official extension.

The Context.dev extension gives Gemini CLI live web and document context through a hosted MCP server and an on-demand skill. Search the web, follow company news, scrape pages and YouTube transcripts, map and crawl sites, parse documents, and retrieve brand intelligence without copying an API key into Gemini CLI.

> [card] [Install Context.dev for Gemini CLI](https://github.com/context-dot-dev/gemini-cli-context)
>
> Review the official extension source and latest release on GitHub.

## Prerequisites

* [Gemini CLI](https://github.com/google-gemini/gemini-cli) installed and signed in
* A browser available for Context.dev authorization
* A [Context.dev account](https://context.dev/signup)

## Install and connect

**1. Install the extension**

Run the following command in your terminal:

```bash theme={null}
gemini extensions install https://github.com/context-dot-dev/gemini-cli-context --auto-update --consent
```

The extension is installed from the latest public Context.dev release and will receive future updates automatically.

**2. Start a new Gemini CLI session**

Exit any session that was already open, then start Gemini CLI again. The extension loads the `context` MCP server and the `context-dev` skill when the new session starts.

**3. Authorize Context.dev**

In the new session, start sign-in:

```text theme={null}
/mcp auth context
```

Gemini CLI opens your browser so you can sign in or create an account, approve access, and return to the terminal.

**4. Confirm the extension loaded**

Run `gemini extensions list` in your terminal. The output should show `gemini-cli-context`, the `context` MCP server, and the `context-dev` agent skill.

Inside Gemini CLI, use `/mcp` to inspect the connected tools and `/skills list` to confirm that `context-dev` is available.

> [!NOTE]
>
> The extension uses Context.dev's browser-based OAuth flow. Do not add an API key, bearer token, or custom header to the extension configuration.

## Verify the setup

Send a small, read-only request whose output is easy to inspect:

```text theme={null}
Use Context.dev to scrape https://www.context.dev and return the page title and source URL.
```

Confirm that Gemini CLI shows a successful Context.dev tool call with live output. A response produced without a Context.dev tool call does not verify the connection.

## Use the extension

Ask for the result you want. The bundled skill routes the task to the smallest suitable Context.dev tool.

| Task | Example request |
| - | - |
| Search the live web | `Use Context.dev to find the latest official Gemini CLI announcements and cite the source URLs.` |
| Search company news | `Use Context.dev to find Stripe's latest company news and link every source.` |
| Read a known page | `Use Context.dev to scrape this page as clean Markdown: <url>` |
| Summarize a YouTube video | `Use Context.dev to scrape this YouTube video as a timestamped transcript and summarize it: <youtube-url>` |
| Capture a screenshot | `Use Context.dev to take a full-page screenshot of this page and describe its layout: <url>` |
| Parse a document | `Use Context.dev to parse this PDF and summarize the findings with page references: <file-url>` |
| Retrieve a brand profile | `Use Context.dev to retrieve the brand profile and style guide for linear.app, including logo, colors, fonts, and social profiles.` |
| Research one website | `Use Context.dev to map this site's URLs, then crawl the documentation pages about authentication: <url>` |

Context.dev also exposes website style guides, monitors, and asynchronous batches through the same connection.

> [!WARNING]
>
> Monitor and batch tools can create or change persistent account state. Ask for create, update, run, cancel, or delete operations explicitly and review the tool call before approving it.

## Manage the extension

```bash Update theme={null}
gemini extensions update gemini-cli-context
```

```bash List theme={null}
gemini extensions list
```

```bash Uninstall theme={null}
gemini extensions uninstall gemini-cli-context
```

## Troubleshooting

| Symptom | Fix |
| - | - |
| The extension is not listed | Install it again from the GitHub URL, then run `gemini extensions list`. |
| The `context` server is missing | Start a new Gemini CLI session and inspect `/mcp`. If the extension is disabled, run `gemini extensions enable gemini-cli-context`. |
| Authorization does not start | Run `/mcp auth context`, finish the browser flow, and return to Gemini CLI. |
| Gemini reports `401` or authentication required | Reconnect with `/mcp auth context` and complete authorization again. |
| The `context-dev` skill is missing | Start a new session and run `/skills list`. Update or reinstall the extension if it remains unavailable. |
| Calls fail for insufficient credits | Review usage in the [Context.dev dashboard](https://context.dev/dashboard); repeated retries will not add credits. |

## Reference

> [card] [Extension source](https://github.com/context-dot-dev/gemini-cli-context)
>
> Inspect the manifest, MCP configuration, skill, tests, and releases.

> [card] [Gemini CLI extension docs](https://geminicli.com/docs/extensions/)
>
> Official installation, management, and extension-authoring guidance.

> [card] [Context.dev MCP guide](https://docs.context.dev/install-mcp.md)
>
> Hosted server capabilities and OAuth details.

> [card] [Context.dev dashboard](https://context.dev/dashboard)
>
> Review account credits and usage.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.