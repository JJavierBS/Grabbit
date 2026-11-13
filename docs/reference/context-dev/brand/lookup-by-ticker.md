# Lookup by ticker

> Resolve a stock ticker to a company profile.

Use `type: "by_ticker"` for a public company. Include the exchange when a symbol could refer to more than one listing.

## Request

Send this body to `POST /brand/retrieve`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "type": "by_ticker",
  "ticker": "AAPL",
  "ticker_exchange": "NASDAQ"
}
```

The default exchange is NASDAQ. The [reference](https://docs.context.dev/api-reference/brand-intelligence/brand.md) lists accepted exchanges and ticker constraints.

## Check the listing

Compare `brand.stock` and `brand.domain` with the requested company before saving the result. Preserve the ticker and exchange together as the lookup key.

An unresolved symbol can return `400 NOT_FOUND`. Correct its exchange or use [lookup by domain](https://docs.context.dev/brand/lookup-by-domain.md) when you have the website.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.