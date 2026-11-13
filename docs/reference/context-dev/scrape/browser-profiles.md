# Browser profiles

> Sign in to a website once, then reuse the saved browser session for authenticated scraping.

Use optional `sharedParams.profile` to scrape pages behind a website login. Subscribing to any paid plan enables browser profiles for your organization.

## Create a profile

Set `type` to `new` and provide the website's username or email and password. Context discovers the sign-in flow from your target URL, verifies authentication, and saves the session. Passwords are never stored in the profile.

Add an optional `description` of up to 500 characters to tell profiles apart when you [list them](#list-profiles).

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com/account",
  "formats": {
    "html": true,
    "markdown": true
  },
  "sharedParams": {
    "profile": {
      "type": "new",
      "identifier": "YOUR_WEBSITE_USERNAME",
      "password": "YOUR_WEBSITE_PASSWORD",
      "description": "Acme billing portal admin"
    }
  },
  "timeoutOpts": {
    "milliseconds": 120000
  }
}
```

Save the returned `profile.id`:

```json theme={null}
"profile": { "id": "prof_0123456789abcdef0123456789abcdef" }
```

The response contains `profile: null` when you omit `sharedParams.profile`. New and existing profile requests both return the profile ID.

## Reuse a profile

Set `type` to `existing` and pass the saved ID as `profileId`. Credentials are unnecessary for reuse.

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com/account",
  "formats": {
    "markdown": true
  },
  "sharedParams": {
    "profile": {
      "type": "existing",
      "profileId": "prof_0123456789abcdef0123456789abcdef"
    }
  }
}
```

Profiles belong to your organization and remain usable after API-key rotation. A different organization cannot access them. Use one request at a time per profile; concurrent use returns `PROFILE_BUSY`.

## List profiles

Call `GET /org/browser/profiles` to see the profiles your organization created, newest first. It costs no credits and requires [`logs:read`](https://docs.context.dev/account/api-keys) on restricted keys.

```json theme={null}
{
  "data": [
    {
      "id": "prof_0123456789abcdef0123456789abcdef",
      "description": "Acme billing portal admin",
      "created_at": "2026-10-15T14:03:11.000Z"
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

`description` is `null` when none was supplied. Pass `next_cursor` as `cursor` to fetch the next page, and `limit` to set the page size (1–100, default 25). See the [reference](https://docs.context.dev/api-reference/browser-profiles/list.md) for the complete contract.

A listed profile has not necessarily been verified recently. An expired session is detected, and the profile removed, the next time you use it.

## Handle expiry

When Context confirms that the website session has expired, it deletes the profile and returns HTTP `422`:

```json theme={null}
{
  "message": "The saved login expired and the profile was removed. Submit login credentials again.",
  "error_code": "PROFILE_SESSION_EXPIRED"
}
```

Create a new profile with credentials, then replace the old ID with the new `profile.id`. Context cannot sign in again automatically because the password is not saved.

| Error | HTTP | Action |
| - | - | - |
| `PROFILE_SESSION_EXPIRED` | `422` | Create a new profile. The expired profile was deleted. |
| `PROFILE_REAUTHENTICATION_REQUIRED` | `422` | Create a new profile. The pinned proxy or browser identity is no longer usable. |
| `PROFILE_NOT_FOUND` | `410` | Create a new profile or check the ID and organization. |
| `PROFILE_BUSY` | `409` | Wait for the other request to finish before reusing the profile. |
| `PROFILE_INVALID_CREDENTIALS` | `422` | Correct the website credentials. |
| `PROFILE_MISSING_CREDENTIALS` | `422` | The site asked for a login field you did not send. Add the missing credentials. |
| `PROFILE_ORIGIN_BLOCKED` | `400` or `422` | `400`: the URL is outside the saved profile's origins. `422`: the login flow left the permitted origins. |
| `PROFILE_INVALID_SESSION` | `502` | The browser could not export a session that can be stored safely. Submit the credentials again. |
| `PROFILE_SESSION_TOO_LARGE` | `413` | The browser session exceeds the profile storage limit. |
| `PROFILE_INTERACTION_REQUIRED` | `422` | The site requires an interactive step, such as MFA or CAPTCHA. |
| `PROFILE_AUTHENTICATION_UNKNOWN` | `422` | Authentication could not be verified. The saved profile is preserved. |
| `REQUEST_TIMEOUT` | `408` | Retry with a longer timeout. A timeout preserves the saved profile. |

## Constraints

* Target URLs must use HTTPS and stay within the profile's permitted origins.
* Browser profiles bypass shared caches. Requests and responses use normal logging, with passwords and session secrets redacted. Profiles persist session state, so `zdr: "enabled"` is unsupported.
* Custom headers, raw `bytes`, prebuilt parsers other than `emails`, `phone-numbers`, and `links`, iframe capture, popup dismissal, image enrichment, visual image deduplication, filtered image outputs, and product image deduplication are unsupported with profiles.
* Keep the viewport, theme, and proxy settings compatible with the saved profile. Profile viewports are 320–3840 pixels wide and 240–2160 pixels high.
* Residential proxy identities expire after 30 minutes. Static ISP identities remain pinned while their endpoint is available.
* MFA, CAPTCHA, passkeys, popup login, and HTTP authentication are unsupported. Cross-origin sign-in discovery is automatic.

You can combine profiles with [browser actions](https://docs.context.dev/scrape/browser-actions.md) and [waiting and rendering](https://docs.context.dev/scrape/waiting-and-rendering.md). See the [request and response reference](https://docs.context.dev/api-reference/web-scraping/scrape.md) for the complete contract.

The [emails](https://docs.context.dev/scrape/prebuilt-parsers/emails.md), [phone numbers](https://docs.context.dev/scrape/prebuilt-parsers/phone-numbers.md), and [links](https://docs.context.dev/scrape/prebuilt-parsers/links.md) parsers support browser profiles and run on the authenticated page HTML.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.