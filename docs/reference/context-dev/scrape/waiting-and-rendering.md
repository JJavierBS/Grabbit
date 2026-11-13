# Waiting and rendering

> Control page readiness, viewport size, theme, and popup handling.

Put rendering options inside `sharedParams`. Waiting happens after browser actions and before output capture.

## Wait for a page element

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "markdown": true,
    "screenshot": true
  },
  "sharedParams": {
    "waitFor": "main",
    "viewport": {
      "width": 1280,
      "height": 800
    }
  }
}
```

## Options

| Field | Default | Behavior |
| - | - | - |
| `waitFor` | 500 ms | Milliseconds (0–30,000) or a CSS selector. Defaults to 2,000 ms with frames or an XML URL. `0` skips the wait. |
| `settleAnimations` | `true` with screenshots | Wait for CSS animations to settle. Otherwise defaults to `false`. |
| `viewport` | 1920 × 1080 when omitted | Width 240–7,680; height 240–4,320. |
| `theme` | Browser default | `light` or `dark`. |
| `dismissCookies` | `true` | Accept detected cookie banners. |
| `dismissPopups` | `false` | Close other detected popups. |

An explicitly empty `viewport: {}` uses field defaults of 1440 × 900. Set both dimensions when the size matters.

## Mobile and consent views

For mobile rendering, use `viewport: {"width":390,"height":844}`. To keep a consent banner visible, set `dismissCookies: false` and leave `dismissPopups` false. Popup handling is heuristic and may not remove every overlay.

Choose selector waits when a specific element indicates readiness. Fixed waits count toward the [timeout budget](https://docs.context.dev/scrape/timeouts-and-errors.md). Content can still be incomplete when page rendering does not settle; inspect `isPartial` and each output’s `success`.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.