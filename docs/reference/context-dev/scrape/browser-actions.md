# Browser actions

> Interact with a page before capturing its outputs.

Use `sharedParams.actions` to click, scroll, or wait before capture. Actions run in order, require a paid plan, and bypass the cache.

## Load more content

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com/products",
  "formats": {
    "markdown": true,
    "screenshot": true
  },
  "sharedParams": {
    "actions": [
      {
        "type": "perform",
        "action": "Click the Load more button"
      },
      {
        "type": "waitFor",
        "selector": ".product:nth-child(20)"
      }
    ]
  }
}
```

## Action types

| Type | Fields |
| - | - |
| `perform` | `action`: a natural-language instruction, 1–500 characters. |
| `scroll` | `direction`: `down`, `up`, `left`, or `right`; `amount`: pixels, `viewport`, or `max`; optional `selector` and `maxScrolls`. |
| `wait` | `milliseconds`: 0–30,000. |
| `waitFor` | `selector`: CSS selector up to 2,048 characters. |

Send 1–5 actions. A scroll defaults to down, one viewport, once. Pixel amounts range from 1 to 100,000 and `maxScrolls` from 1 to 50. A scroll-container selector can be up to 2,000 characters.

## Scroll a lazy feed

```json theme={null}
{
  "url": "https://example.com/gallery",
  "formats": {
    "images": true
  },
  "sharedParams": {
    "actions": [
      {
        "type": "scroll",
        "direction": "down",
        "amount": "viewport",
        "maxScrolls": 3
      }
    ]
  }
}
```

For tabs or menus, use a precise `perform` instruction followed by `waitFor` for the resulting content. Use a [custom parser](https://docs.context.dev/scrape/parse-fields.md) to verify the expected element is present.

## Failures and deadlines

A failed action marks affected outputs as failed; the request can still return HTTP 200. Fixed waits, including the default `waitFor`, must fit within the [capture budget](https://docs.context.dev/scrape/timeouts-and-errors.md#set-a-deadline), which is shorter than the deadline with `return-partial`. A Free-plan request with actions returns `403 PAID_PLAN_REQUIRED`.

Use actions with Scrape. To visit several interactive pages, get their URLs through [Map](https://docs.context.dev/map/overview) and scrape them individually.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.