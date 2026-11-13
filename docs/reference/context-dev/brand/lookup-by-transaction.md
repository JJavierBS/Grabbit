# Lookup by transaction

> Resolve a merchant descriptor with optional matching hints.

Use `type: "by_transaction"` for bank or card transaction descriptions. The response is a Brand profile; it does not contain a numeric confidence score.

## Request

Send this body to `POST /brand/retrieve`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "type": "by_transaction",
  "transaction_info": "STRIPE *EXAMPLE STORE",
  "country_gl": "us",
  "mcc": 5734,
  "high_confidence_only": true
}
```

## Add matching hints

| Field | Use |
| - | - |
| `transaction_info` | Original descriptor, 3–500 characters. |
| `mcc` | Merchant Category Code from the processor. |
| `country_gl` | Supported two-letter ISO country code. |
| `city` | Known city, when it helps distinguish merchants. |
| `phone` | Phone value present in the transaction data. |
| `high_confidence_only` | Prefer an unresolved result over a less certain match; defaults to false. |

Do not invent missing hints. Non-numeric MCC and phone strings are ignored. City hints are ignored when shorter than four characters, containing more than two digits, or matching a country name.

`maxSpeed`, `force_language`, `timeoutOpts`, and `tags` are supported. `maxAgeMs` is not accepted for this lookup.

## Unresolved merchants

`400 NOT_FOUND` means the merchant could not be identified reliably. Keep the descriptor and show an unresolved state. Distinguish this from a timeout or service error.

If you cache results, include the descriptor and all supplied matching hints in the cache key. Review ambiguous matches before using them in financial reports.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.