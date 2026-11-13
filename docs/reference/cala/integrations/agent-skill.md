# Agent Skill

> Give your agent the knowledge it needs to use Cala well.

The Cala agent skill is a `SKILL.md` file that tells your agent what Cala is, when to use it, which tool to call, and how to handle edge cases — without you having to prompt-engineer any of it.

Install it once. It works across Claude Code, Cursor, Copilot, Amp, Codex, and any other agent that supports the [Agent Skills](https://agentskills.io) format.

## Install

```bash theme={null}
npx skills add cala-ai/cala-skill
```

Or download [`SKILL.md`](https://raw.githubusercontent.com/cala-ai/cala-skill/main/SKILL.md) and place it in your agent's skill directory manually.

## Use with MCP

The skill and the MCP server are complementary. The skill gives your agent the instructions — the MCP server gives it the live connection to execute queries. For the best results, use both.

> [card] [Set up the MCP server](https://docs.cala.ai/integrations/mcp.md)
>
> Connect your agent to Cala's live query tools.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.