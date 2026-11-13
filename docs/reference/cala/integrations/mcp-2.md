# Claude Desktop

> Connect Claude to Cala

Claude Desktop uses OAuth, so you don't need an API key.

In Claude Desktop, go to **Customize → Connectors → Add → Browse connectors**, search for Cala and click on **Connect to Claude**.

![Claude Desktop Directory](https://mintcdn.com/calaai/WSudIyxF6Merq2Gf/images/claude-desktop-directory.png?fit=max\&auto=format\&n=WSudIyxF6Merq2Gf\&q=85\&s=455569d1960f6eb0156ed629edbf247c)

A **browser tab** will open for you to log in to your Cala account. After you **authorize**, return to Claude Desktop and open the Cala connector to confirm all tools are enabled. If not, enable them manually.

> [!NOTE]
>
> **Pair with the agent skill.** The MCP server gives your agent access to Cala's tools. The [agent skill](https://docs.cala.ai/integrations/agent-skill.md) gives it the knowledge to use them well. Install both for the full experience.

[YouTube video player](https://www.youtube.com/embed/FItEDKQHx8Q)

## Available operations

> [card] [Search](https://docs.cala.ai/api-reference/search.md)
>
> Get a sourced, natural-language answer to a question. Maps to Cala's knowledge\_search endpoint.

> [card] [Query](https://docs.cala.ai/api-reference/query.md)
>
> Get structured, typed JSON rows from a Cala QL expression or natural-language question. Maps to Cala's knowledge\_query endpoint.

> [card] [Search Entities](https://docs.cala.ai/api-reference/search-entities.md)
>
> Find entities by name with fuzzy matching.

> [card] [Get Entity Fields](https://docs.cala.ai/api-reference/entity-introspection.md)
>
> Get available properties, relationships, and numerical observations for an entity.

> [card] [Get Entity](https://docs.cala.ai/api-reference/entities.md)
>
> Retrieve the full profile of an entity by its UUID.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.