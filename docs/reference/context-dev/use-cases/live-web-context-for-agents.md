# Give an AI agent live web context

> Build bounded search and read tools that return sourced Markdown, expose failed reads, and keep citations tied to retrieved evidence.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/live-web-context-for-agents.md

Read the recipe and linked API guides, inspect this project's stack, and build the complete flow using its existing conventions.

Add bounded search and read tools to the project's agent. Read known URLs directly, enforce allowed hosts and per-task page, token, and time budgets, and deduplicate reads. Return source IDs, URLs, titles, Markdown, timestamps, and explicit failure states. Treat retrieved content as untrusted data and cite only evidence from successful reads.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Give an agent two tools: find candidate sources and read a selected page. Context.dev handles web search and page scraping. Your agent chooses sources, manages its task budget, and answers from the evidence it actually retrieved.

[Construct built a web-search connector with Context.dev](https://www.context.dev/blog/construct-builds-a-working-web-search-connector-in-minutes-with-context-dev), and [Scira added live web search](https://www.context.dev/blog/scira-ai-adds-real-time-web-search-in-under-10-minutes). This recipe builds framework-independent TypeScript tools for a documentation assistant.

If you want a ready-made tool connection, [install the MCP server](https://docs.context.dev/install-mcp.md). Use the recipe below when you need application-specific source restrictions, budgets, or citation records.

## Separate discovery from evidence

| Tool | API | Output to the agent |
| - | - | - |
| `search` | [Search](https://docs.context.dev/api-reference/web-scraping/search.md), `POST /web/search` | Candidate URLs, titles, and snippets |
| `read` | [Scrape](https://docs.context.dev/api-reference/web-scraping/scrape.md), `POST /web/scrape` | Source ID, URL, title, Markdown, retrieval time, and status |

When the user supplies a known URL, call `read` directly. When searching, prefer official or otherwise relevant domains. Search accepts `numResults` from 1 to 100; returning only a few candidates to the model does not change how many results the API requested.

Search can also scrape results with `markdownOptions.enabled: true`. Check each result's `markdown.code`: only `SUCCESS` with nonempty `markdown.markdown` is usable evidence. A search result with `TIMEOUT`, `WEBSITE_ACCESS_ERROR`, `WEBSITE_BLOCKED`, or `NOT_REQUESTED` is still a candidate, not a successfully read source. Separate reads give this example tighter control over its page budget.

## Implement bounded tools

Use Node.js with a server-side `CONTEXT_DEV_API_KEY` from the [Quickstart](https://docs.context.dev/quickstart.md). The following application adapter uses HTTPS directly so the task limits and error states are visible. Pass your model's tokenizer as `countTokens`, and create a new instance for each user task.

```typescript agent-web-tools.ts theme={null}
export function createWebTools(
  allowedHosts: string[],
  countTokens: (text: string) => number,
) {
  const hosts = new Set(allowedHosts.map((host) => host.toLowerCase()));
  const deadline = Date.now() + 45_000;
  let searches = 0;
  let reads = 0;
  let remainingTokens = 6_000;
  const sources = new Map<string, {
    id: string; url: string; title: string; markdown: string;
    retrievedAt: string; truncated: boolean;
  }>();
  const byUrl = new Map<string, string>();

  function allowed(raw: string) {
    try {
      const url = new URL(raw);
      return url.protocol === "https:" && !url.username && !url.password &&
        (!url.port || url.port === "443") && hosts.has(url.hostname);
    } catch { return false; }
  }

  async function request(path: string, init: RequestInit = {}) {
    const remainingMs = deadline - Date.now();
    if (remainingMs <= 0) throw new Error("Task deadline reached");
    const response = await fetch(`https://api.context.dev/v1${path}`, {
      ...init,
      headers: {
        Authorization: `Bearer ${process.env.CONTEXT_DEV_API_KEY}`,
        "Content-Type": "application/json",
      },
      signal: AbortSignal.timeout(Math.min(15_000, remainingMs)),
    });
    if (!response.ok) throw new Error(`Upstream HTTP ${response.status}`);
    return response.json();
  }

  return {
    sources,
    async search(query: string) {
      if (!query.trim() || query.length > 500) return { status: "invalid_query" };
      if (searches >= 2 || Date.now() >= deadline) return { status: "budget_exhausted" };
      searches++;
      try {
        const data = await request("/web/search", {
          method: "POST",
          body: JSON.stringify({ query, numResults: 10, includeDomains: [...hosts] }),
        });
        const candidates = data.results
          .filter((item: { url: string }) => allowed(item.url))
          .slice(0, 5)
          .map((item: { url: string; title: string; description: string }) => ({
            url: item.url, title: item.title, snippet: item.description,
          }));
        return { status: candidates.length ? "ok" : "empty", candidates };
      } catch {
        return { status: "search_failed", candidates: [] };
      }
    },
    async read(url: string) {
      if (!allowed(url)) return { status: "outside_source_scope", url };
      if (Date.now() >= deadline) return { status: "budget_exhausted", url };
      const cachedId = byUrl.get(url);
      if (cachedId) return { status: "ok", ...sources.get(cachedId)! };
      if (reads >= 3 || remainingTokens <= 0) return { status: "budget_exhausted", url };
      reads++;
      try {
        const data = await request("/web/scrape", {
          method: "POST",
          body: JSON.stringify({
            url, formats: { markdown: true }, sharedParams: { mainContentOnly: true },
          }),
        });
        const sourceUrl: string = data.url;
        const fullMarkdown = data.markdown?.data;
        if (typeof fullMarkdown !== "string" || !fullMarkdown.trim()) {
          return { status: "empty", url };
        }
        if (!allowed(sourceUrl)) return { status: "outside_source_scope", url };

        let markdown = fullMarkdown.slice(0, 12_000);
        while (markdown && countTokens(markdown) > remainingTokens) {
          markdown = markdown.slice(0, Math.floor(markdown.length * 0.8));
        }
        if (!markdown.trim()) return { status: "budget_exhausted", url };
        remainingTokens -= countTokens(markdown);
        const source = {
          id: `source-${sources.size + 1}`,
          url: sourceUrl,
          title: data.metadata?.title || sourceUrl,
          markdown,
          retrievedAt: new Date().toISOString(),
          truncated: markdown.length < fullMarkdown.length,
        };
        sources.set(source.id, source);
        byUrl.set(url, source.id);
        byUrl.set(sourceUrl, source.id);
        return { status: "ok", ...source };
      } catch {
        return { status: "read_failed", url };
      }
    },
  };
}
```

Register `search(query)` and `read(url)` using your agent framework's tool interface. Keep the hostname policy in application configuration; page content must not expand it. This example permits exact hostnames, so include `docs.example.com` separately from `example.com` when both are intended sources.

The six-thousand-token limit applies to retained evidence. Budget the question, instructions, tool metadata, and answer separately. Pass a source ID instead of repeatedly appending an already-read source to the model's conversation. The adapter bounds API requests; your agent runner must also enforce a turn limit and overall model deadline.

The `read` tool sets `sharedParams.mainContentOnly` so the Markdown keeps only the page's main content. By default, Scrape can serve Markdown from cache when a copy up to three days old exists. For a task that requires a fresh read, add `maxAgeMs: 0` to the request body and account for the extra latency. See [Get Markdown](https://docs.context.dev/scrape/markdown.md) for the other content controls. Record retrieval time without presenting it as the page's publication time.

## Require resolvable citations

Keep the returned `sources` registry outside the model. Ask the model for claims that reference those source IDs:

```json Answer shape theme={null}
{
  "claims": [
    { "text": "A statement supported by the retrieved documentation.", "sourceIds": ["source-1"] }
  ],
  "limitations": ["One requested page could not be read."]
}
```

Validate that every claim has at least one ID in the registry. Resolve those IDs to URLs in your renderer rather than accepting arbitrary model-written links. Membership alone does not prove that a source supports a claim: inspect supporting passages or run an evidence check before showing the answer.

Tell the agent to treat retrieved Markdown as untrusted source text. Instructions inside a page cannot authorize new tools, reveal secrets, or change the user's task. If no successful read supports an answer, return that the available evidence is insufficient.

## Exercise failures before connecting a model

Use a question about a current API and a small official-documentation allowlist. Check these cases against the adapter and the answer renderer:

| Input or failure | Expected behavior |
| - | - |
| User supplies a documentation URL | Read it without an unnecessary search. |
| Search returns no candidates | Return an empty result, with no fabricated source. |
| Page is blocked or empty | Record a failed or empty read; exclude it from citations. |
| Fourth distinct read | Stop at the page budget. |
| Retrieved text exceeds the evidence budget | Mark it truncated and use only retained text. |
| Model invents a source ID | Reject the citation and regenerate or omit the claim. |

> [card] [Website RAG](https://docs.context.dev/use-cases/build-rag-from-websites.md)
>
> Build a persistent index when the same corpus serves many questions.

> [card] [Research with PDFs](https://docs.context.dev/use-cases/research-with-pdfs.md)
>
> Preserve document evidence and avoid invented page citations.

Use [Answers](https://docs.context.dev/answers/overview) when the input is a research task and you want the API to find evidence and shape a JSON answer. Preserve its source URLs and any partial-result marker. When the sources are already known, keep using the `read` tool above so each citation resolves to a retrieved page.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.