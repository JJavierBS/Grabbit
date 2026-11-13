# Neon

> Run Context.dev APIs as Neon Functions.

[Neon's Context.dev template](https://neon.com/functions/templates/context-dev) includes web search and scraping, with optional Answers, Brand Retrieval, and News Search routes. Extend the generated function to call any other Context API.

## Prerequisites

* A Neon project and a local application
* A Context.dev secret API key from the [dashboard](https://context.dev/dashboard).
* The current Neon CLI, which includes `neon functions new`

If your CLI does not recognize the registry commands, update it:

```bash theme={null}
npm install -g neon@latest
```

From your application root, link the project and branch you want to use:

```bash theme={null}
neon link --project-id YOUR_PROJECT_ID --branch YOUR_BRANCH --no-env-pull
```

## Create the function

Run this from your application root:

```bash theme={null}
neon functions new context-dev --yes
```

This creates `functions/contextdev/index.ts` and adds it to `neon.ts`. The default routes are `/web-search` and `/web-scrape`.

To include all five routes, use this command **instead** when creating the function:

```bash theme={null}
neon functions new context-dev --all-operations --yes
```

To choose specific routes, repeat `--operation` with each route name instead:

```bash theme={null}
neon functions new context-dev --operation web-search --operation web-answers --yes
```

The route names are `web-search`, `web-scrape`, `web-answers`, `brand-retrieve`, and `news-search`.

## Configure authentication

Set these values in an uncommitted `.env.local` file:

```dotenv theme={null}
CONTEXT_DEV_API_KEY=YOUR_CONTEXT_DEV_SECRET_KEY
CONTEXT_FUNCTION_TOKEN=YOUR_RANDOM_CALLER_TOKEN
```

Generate `CONTEXT_FUNCTION_TOKEN` with `openssl rand -hex 32`. It must be at least 32 characters.

> [!WARNING]
>
> The API key lets the function call Context.dev; the caller token controls access to your function. Keep both server-side and add `.env.local` to `.gitignore`.

## Run and call the function

Start the function locally:

```bash theme={null}
neon dev --env .env.local --source ./functions/contextdev/index.ts --port 3001
```

In a second terminal, set `CONTEXT_FUNCTION_TOKEN` to the same caller token from `.env.local`, then send a request:

```bash theme={null}
curl --fail-with-body http://localhost:3001/web-search \
  -H "Authorization: Bearer $CONTEXT_FUNCTION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"Neon Postgres branching","numResults":5}'
```

The response contains `results` with source URLs. Calls use your Context.dev credits.

## Deploy the function

Review `neon.ts`, then deploy to the linked branch with both secrets:

```bash theme={null}
neon deploy --env .env.local --no-env-pull
```

This applies all services declared in `neon.ts` to the linked branch. Replace `http://localhost:3001` in the request above with the printed function URL, keeping `/web-search` and the bearer header.

## Available routes

See [Neon’s route documentation](https://neon.com/functions/templates/context-dev#what-this-function-exposes) for available operations and request parameters. To add other Context APIs, use the [API reference](https://docs.context.dev/api-reference/web-scraping/scrape.md).

## Troubleshooting

| Response | What to check |
| - | - |
| `401 Unauthorized` | Send the caller token in `Authorization: Bearer …`, not the Context.dev API key. |
| `503 Context.dev function is not configured` | Set both environment variables and ensure the caller token is at least 32 characters. |
| `404` | Include the route suffix and confirm that operation was selected when creating the function. |
| `502 Context.dev API key was rejected` | Replace the server-side Context.dev key. The template translates upstream authentication failures to `502`. |


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.