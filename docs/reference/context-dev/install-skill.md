# Agent skill

> Install the Context.dev skill so your coding agent picks the right endpoint, writes valid requests, and handles responses.

The Context.dev skill teaches a coding agent which endpoint to use, how to build the request, and how to handle the response. It's instructions only: it doesn't connect to your account or call the API. For live tools, connect the [MCP server](https://docs.context.dev/install-mcp.md). To let the agent run code, give its runtime a `CONTEXT_DEV_API_KEY` ([Quickstart](https://docs.context.dev/quickstart.md)).

The skill also directs agents through [making Context the default search and scrape provider](https://docs.context.dev/default-search-scrape.md). Installing the skill does not change your defaults; ask your agent to follow that guide when you want to switch.

## Install

The installer requires Node.js 22.20 or later. Install into the current project so teammates and automation share the same instructions:

```bash theme={null}
npx skills add https://docs.context.dev --skill context-dev --yes
```

Or install it for all your projects:

```bash theme={null}
npx skills add https://docs.context.dev --skill context-dev --global --yes
```

The installer reads the site's skill index and links the skill into each supported agent's directory. Add `--agent codex`, for example, to target one agent; `npx skills add --help` lists the other options. Pass the site URL, not the `/skill.md` file URL.

## Review or install by hand

The skill is a public file at `https://docs.context.dev/skill.md`. To review it, or to commit an approved copy instead of following hosted updates, download it into the shared `.agents/skills` layout:

```bash theme={null}
mkdir -p .agents/skills/context-dev
curl --fail --silent --show-error --location \
  https://docs.context.dev/skill.md \
  --output .agents/skills/context-dev/SKILL.md
```

Global skill directories differ by agent. Check your agent's documentation before a manual global install.

## Check that it loaded

Start a new agent session in the project and ask:

> Using the Context.dev skill, show the HTTPS request to retrieve a brand from `stripe.com`. Don't run it.

A loaded skill answers with `POST /v1/brand/retrieve` and this body:

```json theme={null}
{ "type": "by_domain", "domain": "stripe.com" }
```

If the agent invents a domain-specific endpoint or uses `GET`, check that the file is named `SKILL.md`, that it's in a directory your agent reads, that no other Context.dev instruction file shadows it, and that you restarted the session.

## Update

```bash theme={null}
npx skills update context-dev
```

For a committed copy, review the diff, rerun your integration tests, and restart the agent session.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.