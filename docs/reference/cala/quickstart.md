# Quickstart

> Start using Cala in 30 seconds.

> [!TIP]
>
> **Using an AI assistant?** Install the Cala skill and your agent will know how to use Cala out of the box — no extra prompting needed.
>
> ```bash theme={null}
> npx skills add cala-ai/cala-skill
> ```
>
> [Learn more](https://docs.cala.ai/integrations/agent-skill.md)

## Create your API key

Get an API key to authenticate your requests. Go to our [Console](https://console.cala.ai/api-keys) and create a new API key.

> [card] [Get Cala's API key](https://console.cala.ai/api-keys)
>
> Create a free Cala account and get your API key.

## Make your first request

Both endpoints accept the same input — the difference is how they respond. Send a Cala QL expression (or a natural-language question) and choose the output shape you need.

```python Structured Answer (knowledge_query) icon=python theme={null}
import requests

url = "https://api.cala.ai/v1/knowledge/query"

query = "startups.location=Spain.funding>10M.funding<50M"
payload = { "input": query }
headers = {
    "X-API-KEY": "YOUR_API_KEY",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
```

```javascript Natural Language Answer (knowledge_search) icon=square-js theme={null}
const options = {
  method: 'POST',
  headers: {'X-API-KEY': 'YOUR_API_KEY', 'Content-Type': 'application/json'},
  body: JSON.stringify({input: 'startups.location=Spain.funding>10M.funding<50M'})
};

fetch('https://api.cala.ai/v1/knowledge/search', options)
  .then(res => res.json())
  .then(res => console.log(res))
  .catch(err => console.error(err));
```

Same input, two output shapes.

## Get a Structured Answer

`POST /v1/knowledge/query` returns JSON rows — ready for programmatic use.

```json theme={null}
[
  { "name": "Luzia", "funding": "13M", "location": "Spain" },
  { "name": "Nomad Solar", "funding": "15M", "location": "Spain" },
  { "name": "Embat", "funding": "21.5M", "location": "Spain" },
  { "name": "Matteco", "funding": "16M+", "location": "Spain" },
  { "name": "Exoticca", "funding": "25.2M", "location": "Spain" },
  { "name": "Multiverse Computing", "funding": "12.5M", "location": "Spain" }
]
```

## Get a Natural-Language Answer

`POST /v1/knowledge/search` returns a succinct, sourced answer in markdown.

```markdown theme={null}
## Spanish Startups (€10M–€50M funding)

**Luzia** — AI assistant, €13M raised.
**Nomad Solar** — Solar energy, €15M raised.
**Embat** — Treasury management, €21.5M raised.
**Matteco** — Green hydrogen materials, €16M+ raised.
**Exoticca** — Travel tech, €25.2M raised.
**Multiverse Computing** — Quantum computing, €12.5M raised.
```

No parsing. No deduplication. No hallucinated data. Verified, sourced, deterministic.

## Next steps

That's it! You can now start using Cala to build your own applications. Deep dive into the available endpoints, params and responses in our [API Reference](https://docs.cala.ai/api-reference/query.md) section.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.