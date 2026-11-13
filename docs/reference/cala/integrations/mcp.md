# MCP

> Connect your AI agent to Cala's MCP

```json theme={null}
https://api.cala.ai/mcp/
```

For more information about MCP and how it works, you can read more about it [here](https://modelcontextprotocol.io/docs/getting-started/intro).

> [!NOTE]
>
> **Pair with the agent skill.** The MCP server gives your agent access to Cala's tools. The [agent skill](https://docs.cala.ai/integrations/agent-skill.md) gives it the knowledge to use them well. Install both for the full experience.

## Connect your agent to Cala's MCP

You can use Cala via our MCP. To get started, you need to get an API key to authenticate your MCP client. Go to our [Console](https://console.cala.ai/api-keys) and create a new API key.

> [card] [Get Cala's API key](https://console.cala.ai/api-keys)
>
> Create a free Cala account and get your API key.

With your API key in hand, you can connect your AI agent such as Cursor, Claude Code and others to our MCP server. Cala MCP gives AI agents access to verified, structured and typed knowledge — both as natural-language answers and structured data — as well as entity information.

> [tab] Cursor
>
> Add to `~/.cursor/mcp.json`:
>
> ```json theme={null}
> {
>     "mcpServers": {
>         "Cala": {
>             "url": "https://api.cala.ai/mcp/",
>             "headers": {
>                 "X-API-KEY": "YOUR_CALA_API_KEY"
>             }
>         }
>     }
> }
> ```
>
> For more information, follow their documentation [here](https://cursor.com/docs/context/mcp#installing-mcp-servers).

> [tab] VS Code
>
> Add to `.vscode/mcp.json`:
>
> ```json theme={null}
> {
>     "servers": {
>         "Cala": {
>             "type": "http",
>             "url": "https://api.cala.ai/mcp/",
>             "headers": {
>                 "X-API-KEY": "YOUR_CALA_API_KEY"
>             }
>         }
>     }
> }
> ```
>
> For more information, follow their documentation [here](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)

> [tab] Claude Desktop
>
> Claude Desktop uses OAuth, so you don't need an API key.
>
> In Claude Desktop, go to **Customize → Connectors → Add → Browse connectors**, search for Cala and click on **Connect to Claude**.
>
> ![Claude Desktop Directory](https://mintcdn.com/calaai/WSudIyxF6Merq2Gf/images/claude-desktop-directory.png?fit=max\&auto=format\&n=WSudIyxF6Merq2Gf\&q=85\&s=455569d1960f6eb0156ed629edbf247c)
>
> A **browser tab** will open for you to log in to your Cala account. After you **authorize**, return to Claude Desktop and open the Cala connector to confirm all tools are enabled. If not, enable them manually.

> [tab] Claude Code
>
> To install Cala as a Claude **connector**, run the following command in your terminal adding your API key:
>
> ```text theme={null}
> claude mcp add --transport http cala https://api.cala.ai/mcp/   --header "X-API-KEY: YOUR_CALA_API_KEY"
> ```
>
> You can also install Cala as a **plugin**, it is part of Claude [community marketplace](https://github.com/anthropics/claude-plugins-community/blob/main/.claude-plugin/marketplace.json) for plugins. Cala plugin for Claude Code includes our remote MCP server as well as the skill so that Claude Code can use the MCP tools optimally.
>
> To do so, run this in your Claude Code terminal to install the community marketplace:
>
> ```text theme={null}
> /plugin marketplace add anthropics/claude-plugins-community
> ```
>
> Then, install Cala plugin:
>
> ```text theme={null}
> /plugin install cala@claude-community
> ```
>
> Run this to activate the plugin:
>
> ```text theme={null}
> /reload-plugins
> ```

> [tab] Mistral Vibe
>
> Add to `~/.vibe/config.json`:
>
> ```json theme={null}
> {
>   "mcpServers": {
>     "Cala": {
>       "url": "https://api.cala.ai/mcp",
>       "headers": {
>         "X-API-KEY": "YOUR_CALA_API_KEY"
>       }
>     }
>   }
> }
> ```

> [tab] Codex
>
> Add to `~/.codex/config.toml`:
>
> ```toml theme={null}
> [mcp_servers.cala]
> enabled = true
> command = "npx"
> args = [
>   "-y",
>   "mcp-remote",
>   "https://api.cala.ai/mcp",
>   "--header",
>   "X-API-Key:${CALA_API_KEY}"
> ]
>
> [mcp_servers.cala.env]
> CALA_API_KEY = "YOUR_CALA_API_KEY"
> ```

> [tab] OpenAI
>
> > [!NOTE]
> >
> > To support the full power of our graph's flexible schema, this MCP server utilizes dynamic JSON objects. This provides a "schema-less" experience for the LLM. Because of this, it is incompatible with OpenAI's "strict mode" so please ensure `strict: false` is set in your OpenAI specification.
>
> For more information, follow their documentation [here](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)

> [tab] Other
>
> For clients with built-in remote MCP support:
>
> ```json theme={null}
> {
>     "mcpServers": {
>         "Cala": {
>             "url": "https://api.cala.ai/mcp/",
>             "headers": {
>                 "X-API-KEY": "YOUR_CALA_API_KEY"
>             }
>         }
>     }
> }
> ```
>
> For clients without built-in remote MCP support:
>
> ```json theme={null}
> {
>     "mcpServers": {
>         "Cala": {
>             "command": "npx",
>             "args": [
>                 "mcp-remote",
>                 "https://api.cala.ai/mcp/",
>                 "--header",
>                 "X-API-KEY: YOUR_CALA_API_KEY"
>             ]
>         }
>     },
> }
> ```

## Available Tools

Here are the tools available to the Cala MCP:

> [card] knowledge\_search
>
> Get a succinct, token-optimized answer in natural-language markdown, with sources, explainability, and matching entities. Accepts either a natural-language question or a Cala QL expression as input.

> [card] knowledge\_query
>
> Get verified knowledge as structured, typed JSON rows plus matching entities. Accepts either a Cala QL expression or a natural-language question as input.

> [card] entity\_search
>
> Search entities by name with fuzzy matching.

> [card] entity\_introspection
>
> Get the field schema for an entity by its UUID. Returns the available properties, relationships, and numerical observations you can use when querying an entity.

> [card] entity\_retrieval
>
> Retrieve information about an entity by its UUID.

## Hubs & Marketplaces

You can also find Cala's MCP server listed on the following hubs and marketplaces:

> [card] [mcpservers.org](https://mcpservers.org/servers/docs-cala-ai-integrations-mcp)
>
> Browse Cala's MCP server listing on mcpservers.org.

> [card] [mcp.so](https://mcp.so/server/cala)
>
> Browse Cala's MCP server listing on mcp.so.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.