# Swytchcode

> Call Context.dev from AI agents through Swytchcode's managed API execution layer.

Swytchcode packages the Context.dev API as agent-ready tools with authentication, validation, retries, policies, and audit history handled by its execution layer.

> [card] [Open Context.dev on Swytchcode](https://www.swytchcode.com/apis/context-dev)
>
> Review the Context.dev manifest and setup guide in Swytchcode's integration directory.

## Install and connect

**1. Install the CLI**

```bash theme={null}
npm install -g swytchcode
swy login
```

**2. Add Context.dev to your project**

Run these commands from the project your agent will use:

```bash theme={null}
swy init
swy get context_dev
```

**3. Enable the tools you need**

Inspect the downloaded manifest, then add only the methods your agent should be allowed to call:

```bash theme={null}
swy list methods
swy add context_dev.<method>
```

**4. Connect Context.dev**

```bash theme={null}
swy auth connect context_dev
swy auth status
```

Enter a Context.dev API key from the [dashboard](https://context.dev/dashboard) when prompted.

> [!NOTE]
>
> Swytchcode uses a Context.dev API key for REST API calls. This is separate from the browser-based OAuth flow used by the hosted Context.dev MCP server.

## Verify the setup

Inspect an enabled method before calling it:

```bash theme={null}
swy list tooling
swy info context_dev.<method>
swy exec context_dev.<method> --dry-run
```

When the dry run validates, remove `--dry-run` and provide the method's required arguments.

## Use with an agent

Swytchcode can expose the enabled tools to supported MCP clients and agent frameworks. Follow its [MCP setup guide](https://docs.swytchcode.com/quickstarts/getting-started/mcp/) for your client, then ask the agent for a concrete result:

```text theme={null}
Use the Context.dev tool from Swytchcode to scrape https://www.context.dev and return the page title and source URL.
```

## Reference

> [card] [Context.dev on Swytchcode](https://www.swytchcode.com/apis/context-dev)
>
> Open the integration listing and manifest instructions.

> [card] [Swytchcode CLI guide](https://docs.swytchcode.com/quickstarts/getting-started/cli-only/)
>
> Install integrations, enable methods, connect accounts, and execute tools.

> [card] [Swytchcode MCP setup](https://docs.swytchcode.com/quickstarts/getting-started/mcp/)
>
> Add Swytchcode to supported AI clients.

> [card] [Context.dev API quickstart](https://docs.context.dev/quickstart.md)
>
> Call Context.dev directly with an SDK or REST.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.