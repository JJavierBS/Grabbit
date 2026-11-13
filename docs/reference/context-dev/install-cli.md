# CLI

> Call Context.dev from your terminal with the context-dev CLI and use its JSON output in scripts and CI.

The `context-dev` CLI runs Context.dev operations from your terminal: brand lookups, crawls, web searches, batches, monitors, and more.

> [!NOTE]
>
> The CLI is generated from the API spec, so command names and flags can change between releases. Treat `--help` from your installed version as the source of truth.

## Install

> [tab] Release binary
>
> Download the archive for your operating system and architecture from the [latest GitHub release](https://github.com/context-dot-dev/context-dev-cli/releases/latest). Extract `context-dev`, move it to a directory on your `PATH`, and check it:
>
> ```bash theme={null}
> context-dev --version
> ```
>
> In CI, pin a release and verify its published checksums instead of downloading `latest` on every run.

> [tab] Go
>
> With Go 1.25 or later:
>
> ```bash theme={null}
> go install github.com/context-dot-dev/context-dev-cli/cmd/context-dev@latest
> context-dev --version
> ```
>
> Go installs the binary in `$(go env GOPATH)/bin`; add that directory to `PATH` if the command isn't found. Replace `@latest` with a release tag for reproducible builds.

## Set your API key

Using a coding agent? It can create and store a key through [agent registration](https://www.context.dev/auth.md) while you confirm in your browser; see the [Agent quickstart](https://docs.context.dev/agent-quickstart.md).

The CLI reads `CONTEXT_DEV_API_KEY` from the environment. Copy a key from the [API keys](https://context.dev/dashboard/api-keys) page and export it in the current shell:

```bash theme={null}
export CONTEXT_DEV_API_KEY="ctxt_secret_..."
```

In CI, load the key from a secret manager. Avoid the global `--api-key` flag, because command-line arguments can appear in shell history and process listings.

## Make your first request

`--type` picks the lookup, as in `POST /brand/retrieve`, and each type takes its own identifier flag:

```bash theme={null}
context-dev brand retrieve \
  --type by_domain \
  --domain stripe.com \
  --transform 'brand.title'
```

The command prints the company name. Remove `--transform` to see the full response. Other lookup types work the same way:

```bash theme={null}
# Company name
context-dev brand retrieve \
  --type by_name \
  --name "Stripe"

# Card transaction descriptor
context-dev brand retrieve \
  --type by_transaction \
  --transaction-info "SQ *CORNER CAFE" \
  --country-gl us \
  --high-confidence-only
```

## Find a command

```bash theme={null}
context-dev --help
context-dev web --help
context-dev brand retrieve --help
```

The command groups are `parse`, `web`, `brand`, `industry`, `utility`, `monitors`, `batch`, `webhooks:deliveries`, `people`, `news`, and `logs`. The CLI has no Scrape, Map URLs, or feedback command yet. Call [`POST /web/scrape`](https://docs.context.dev/api-reference/web-scraping/scrape), [`GET /web/urls`](https://docs.context.dev/api-reference/web-scraping/map), and [`POST /feedback`](https://docs.context.dev/api-reference/feedback/submit) directly or through an [SDK](https://docs.context.dev/sdks).

Common operations:

```bash theme={null}
# Crawl part of a site to Markdown.
context-dev web web-crawl-md \
  --url https://docs.example.com/product/ \
  --max-pages 50 \
  --max-depth 3 \
  --url-regex '^https://docs\.example\.com/product/' \
  --use-main-content-only

# Search the web within a freshness window.
context-dev web search \
  --query "payments API pricing" \
  --num-results 20 \
  --freshness last_month \
  --include-domain stripe.com

# Extract a site's colors, typography, and component styles.
context-dev web extract-styleguide \
  --domain example.com \
  --color-scheme light

# Warm the Brand cache before a later lookup. This only queues the work.
context-dev utility prefetch \
  --type brand \
  --identifier '{"domain":"example.com"}'
```

Flags that take an object, such as `--identifier` and `--timeout-opts`, accept a JSON value.

## Control output

Use `--format json` for stable output in scripts, and `--transform` with a GJSON path to keep only the fields you need, which also keeps large responses out of an agent's context window:

```bash theme={null}
context-dev web search \
  --query "payments API pricing" \
  --format json \
  --transform 'results.#.url' > urls.json
```

## Use with an agent

Add a short instruction to your repository's agent file:

```markdown AGENTS.md theme={null}
## Context.dev

The `context-dev` CLI is installed. Read `CONTEXT_DEV_API_KEY` from the
environment and never print it. Run `context-dev <resource> <command> --help`
before using an unfamiliar command. Bound crawls and batch jobs, use JSON output
for automation, and review state-changing monitor commands before running them.
```

## Troubleshoot

| Symptom | Check |
| - | - |
| `command not found` | Put the extracted binary or the Go bin directory on `PATH`. |
| Unknown command or missing flag | Run `--help` for that exact command; examples may target another release. |
| `flag provided but not defined: -type` | Update to version 0.8.0 or newer; `command -v context-dev` shows which copy runs first on `PATH`. |
| `401` | Check that `CONTEXT_DEV_API_KEY` is set in the CLI's environment, then read `error_code` in the response. |
| Unexpected JSON | Note `context-dev --version` and compare the output with the API reference. |


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.