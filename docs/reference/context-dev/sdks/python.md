# Python

> Install the Python SDK, scrape a page, look up a brand, and set timeouts and retries.

The `context.dev` package requires Python 3.9 or later. [SDKs](https://docs.context.dev/sdks) covers the API key and the defaults all SDKs share.

## Install

Create a virtual environment, then install the SDK:

```bash theme={null}
python3 -m venv .venv
source .venv/bin/activate
python -m pip install context.dev
```

## Scrape a page

Save this as `scrape.py` and run `python scrape.py`. It prints the page as Markdown, starting with `# Example Domain`.

```python scrape.py theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

page = client.web.scrape(
    url="https://example.com",
    formats={"markdown": True},
    shared_params={"main_content_only": True},
)

print(page.markdown.data)
```

## Look up a brand

Replace the request and the `print` line with this lookup. It prints the company name.

```python theme={null}
response = client.brand.retrieve(
    type="by_domain",
    domain="stripe.com",
)

print(response.brand.title if response.brand else None)
```

## Notes

* Methods and parameters use `snake_case`. Nested parameters are dictionaries with `snake_case` keys, such as `shared_params={"main_content_only": True}`.
* Set `timeout` in seconds and `max_retries` on the client: `ContextDev(timeout=120.0, max_retries=0)`.
* `AsyncContextDev` has the same methods for `asyncio` code.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.