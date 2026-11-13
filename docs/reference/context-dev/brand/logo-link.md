# Logo Link

> Embed a company logo using a public client ID and referring-domain restrictions.

Logo Link returns image bytes for a company domain. Use the generated URL directly as an image source when you need lightweight logo display in a browser, email, or spreadsheet.

> [!NOTE]
>
> Logo Link is for direct image embedding. Do not download, persist, or rehost the returned image file. Browser and CDN caching directed by the response headers is allowed.

## Before you start

**1. Create a public client ID**

Open the [Logo Link dashboard](https://context.dev/dashboard/logolink) and copy the value under **Public Client ID**.

![Logo Link dashboard with the public client ID and domain restrictions](https://mintcdn.com/branddev/repamerS-LSYfOs8/images/logolink-page.png?fit=max\&auto=format\&n=repamerS-LSYfOs8\&q=85\&s=c2fa8a9bb11f94fd18f3562067a2bc8f)

**2. Restrict where it can be used**

Select **Domain Restrictions** and add every site that will embed the image, such as `app.example.com` and the exact localhost origin used during development.

![Allowed referring domains in the Logo Link dashboard](https://mintcdn.com/branddev/repamerS-LSYfOs8/images/domain-restrictions.png?fit=max\&auto=format\&n=repamerS-LSYfOs8\&q=85\&s=fa4fb96a65fa9c9ad0a164d429689fe7)

> [!WARNING]
>
> A public client ID is intentionally visible in frontend code. Treat it as frontend-safe only after you configure and test its referring-domain restrictions.

## Build the image URL

```text theme={null}
https://logos.context.dev/?publicClientId=brandLL_xxx&domain=github.com
```

| Parameter | Required | Description |
| - | - | - |
| `publicClientId` | Yes | Public client ID from the Logo Link dashboard. |
| `domain` | Yes | Company domain, such as `github.com`. |
| `theme` | No | Use `light` to prefer a dark asset for a light surface, or `dark` to prefer a light asset for a dark surface. |
| `type` | No | Use `icon` for a near-square mark or `wordmark` for a wider or taller wordmark. The default is `icon`. |

Logo Link accepts `GET` and `HEAD`. A successful `GET` returns raw image bytes rather than a JSON object. Follow its `Content-Type` and `Cache-Control` response headers.

## Embed the logo

> [tab] HTML
>
> ```html theme={null}
> <img
>   src="https://logos.context.dev/?publicClientId=brandLL_xxx&domain=stripe.com"
>   alt="Stripe logo"
>   width="40"
>   height="40"
>   loading="lazy"
> />
> ```

> [tab] React
>
> ```jsx theme={null}
> function CompanyLogo({ companyName, domain }) {
>   const publicClientId = process.env.NEXT_PUBLIC_LOGOLINK_CLIENT_ID;
>   if (!publicClientId) throw new Error("Missing Logo Link public client ID");
>
>   const params = new URLSearchParams({
>     publicClientId,
>     domain,
>     type: "icon",
>   });
>
>   return (
>     <img
>       src={`https://logos.context.dev/?${params}`}
>       alt={`${companyName} logo`}
>       width={40}
>       height={40}
>       loading="lazy"
>       onError={(event) => {
>         event.currentTarget.hidden = true;
>       }}
>     />
>   );
> }
> ```

> [tab] Spreadsheet
>
> ```text theme={null}
> =IMAGE("https://logos.context.dev/?publicClientId=brandLL_xxx&domain=" & ENCODEURL(A2))
> ```

Reserve image dimensions to prevent layout shift. If no logo is available, Logo Link returns a generated monogram SVG with status 200, or a generated name wordmark for `type=wordmark`. An invalid client ID, exhausted quota, or disallowed referring site can make the image fail to load.

## Choose the right product

| Need | Use |
| - | - |
| Display one hosted logo without storing the file | Logo Link |
| Retrieve multiple logos, colors, descriptions, or social links | [Brand API](https://docs.context.dev/brand/overview) |
| Extract visual tokens or font files for review | [Styleguide API](https://docs.context.dev/brand/styleguide.md) |

Logo Link has its own usage quota. Check allowances and usage in the [Logo Link dashboard](https://context.dev/dashboard/logolink).

## Usage restrictions

* Do not download, persist, or rehost image files returned by Logo Link.
* Normal caching performed according to the response headers is allowed.
* A returned logo identifies a company; it does not establish affiliation, sponsorship, or endorsement.
* Confirm that your presentation and use comply with applicable trademark rules and your agreement with Context.dev.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.