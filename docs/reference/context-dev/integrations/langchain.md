# LangChain

> Use Context.dev as native LangChain tools for live web data, documents, brand intelligence, monitors, and batches.

The [`langchain-context`](https://pypi.org/project/langchain-context/) package exposes Context.dev operations as LangChain `BaseTool` classes. Use individual tools directly or give an agent a focused toolkit for live web research, scraping, crawling, URL mapping, document parsing, brand intelligence, monitors, and batch jobs.

> [card] [View Context.dev for LangChain](https://github.com/context-dot-dev/langchain-context)
>
> Inspect the package source, examples, tests, and releases.

## Prerequisites

* Python 3.10 through 3.14
* A [Context.dev account](https://context.dev/signup) with an API key

## Install and configure

**1. Install the package**

```bash theme={null}
pip install -U langchain-context
```

**2. Set your API key**

Copy a secret key from the [Context.dev dashboard](https://context.dev/dashboard), then set it in your server environment:

```bash theme={null}
export CONTEXT_API_KEY="ctxt_secret_your_key"
```

Tools read `CONTEXT_API_KEY` automatically. You can also pass `api_key` to a tool or toolkit when your application already manages secrets securely.

> [!WARNING]
>
> Keep `CONTEXT_API_KEY` in your server environment. Do not commit it or expose it in browser code.

## Use a tool directly

Every Context.dev operation supports LangChain's synchronous `invoke` interface:

```python theme={null}
from langchain_context import ContextScrape, ContextSearch

search = ContextSearch()
results = search.invoke(
    {
        "query": "latest official Stripe product announcements",
        "includeDomains": ["stripe.com"],
        "numResults": 10,
    }
)

scrape = ContextScrape()
page = scrape.invoke({"url": "https://stripe.com/newsroom"})
```

To read a YouTube video, pass its URL to `ContextScrape`. The returned Markdown includes the timestamped transcript when one is available.

## Give tools to an agent

`ContextToolkit` is safe by default: it includes read operations and removes browser actions from scraping tools. Pass its result to any LangChain agent that accepts a list of tools.

```python theme={null}
from langchain_context import ContextToolkit

context_tools = ContextToolkit(
    groups=("web", "brand"),
).get_tools()
```

Choose only the groups the agent needs:

| Group | Includes |
| - | - |
| `web` | Search, Markdown and HTML scraping, YouTube transcripts, crawling, URL mapping, screenshots, page images, and document parsing |
| `brand` | Brand profiles with industry labels and style guides |
| `monitors` | Read existing monitors, runs, changes, and credit usage |
| `batches` | Read existing batch jobs and results |

Use a focused toolkit when you do not need every group:

```python theme={null}
from langchain_context import ContextBrandToolkit, ContextWebToolkit

web_tools = ContextWebToolkit().get_tools()
brand_tools = ContextBrandToolkit().get_tools()
```

## Enable side effects explicitly

Monitor and batch mutations are excluded unless you opt in. Browser actions are also excluded from scraping tools by default.

```python theme={null}
from langchain_context import ContextToolkit

tools = ContextToolkit(
    include_write_tools=True,
    allow_browser_actions=True,
).get_tools()
```

Enable these options only for an agent that should create, update, run, cancel, or delete Context.dev resources or interact with third-party webpages.

## Use async tools

Every tool also supports LangChain's asynchronous `ainvoke` interface:

```python theme={null}
from langchain_context import ContextSearch

result = await ContextSearch().ainvoke(
    {"query": "latest Context.dev product announcements"}
)
```

## Troubleshooting

| Symptom | Fix |
| - | - |
| `CONTEXT_API_KEY` is missing | Set the environment variable before starting the application, or pass `api_key` securely. |
| Context.dev returns an authentication error | Replace the key with an active secret key from the Context.dev dashboard. |
| A mutating tool is not available | Set `include_write_tools=True` only when the agent should change monitors or batches. |
| Scraping does not expose browser actions | Set `allow_browser_actions=True` only when interactive browsing is required. |
| Calls fail for insufficient credits | Review usage in the [Context.dev dashboard](https://context.dev/dashboard). |

## Reference

> [card] [PyPI package](https://pypi.org/project/langchain-context/)
>
> Install the current release and review its Python requirements.

> [card] [Package source](https://github.com/context-dot-dev/langchain-context)
>
> Read the complete tool catalog, examples, and test suite.

> [card] [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
>
> Learn how tools are defined, invoked, and attached to agents.

> [card] [Context.dev API reference](https://docs.context.dev/api-reference/web-scraping/search.md)
>
> Review the underlying API operations and request schemas.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.