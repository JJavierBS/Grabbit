# Branded content from brand context

> Reuse reviewed brand data across documents, websites, email, and campaign assets.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/branded-documents.md

Read the recipe and linked API guides, inspect this project's stack, and build the flow using its existing conventions.

Build a shared brand-context flow for documents, websites, email, or campaign assets. Gather only the inputs the template needs, approve a small theme, preserve human edits, render a preview, and record source and theme versions with each export.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Build one source bundle and adapt it to the renderer. Context.dev supplies observed branding and page content; your application supplies approved claims, templates, and publishing.

| Output | Review before publishing |
| - | - |
| Reports, proposals, and decks | Keep author and recipient identities distinct; inspect the exported pages. |
| Websites | Check responsive layout, contrast, controls, and missing assets. |
| Email | Use an email renderer, supported fonts, and absolute HTTPS image URLs; test target clients. |
| Campaign assets | Keep imagery attached to the right offer; review each size and crop. |

## Gather the source bundle

Start with a verified domain and a server-side key from the [Quickstart](https://docs.context.dev/quickstart.md). Retrieve Brand for company identity and Styleguide for fonts and design styles. Screenshots and images are optional visual inputs; omit calls your template does not need.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({apiKey: process.env.CONTEXT_DEV_API_KEY});

export async function gatherBrandContext(domain: string) {
  const homepage = `https://${domain}`;

  const results = await Promise.allSettled([
    client.brand.retrieve({type: "by_domain", domain}),
    client.web.extractStyleguide({domain}),
    client.web.scrape({url: homepage, formats: {screenshot: true}}),
    client.web.scrape({url: homepage, formats: {images: true}}),
  ]);

  const [brand, styleguide, screenshot, images] = results;
  const names = ["brand", "styleguide", "screenshot", "images"];
  return {
    domain,
    gatheredAt: new Date().toISOString(),
    brand: brand.status === "fulfilled" ? brand.value : null,
    styleguide: styleguide.status === "fulfilled" ? styleguide.value : null,
    screenshot: screenshot.status === "fulfilled" ? screenshot.value.screenshot.data : null,
    images: images.status === "fulfilled" ? images.value.images.data : null,
    missingSources: results.flatMap((result, index) =>
      result.status === "rejected" ? [names[index]] : []),
  };
}

console.log(await gatherBrandContext("example.com"));
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
domain = "example.com"

brand = client.brand.retrieve(type="by_domain", domain=domain)
styleguide = client.web.extract_styleguide(domain=domain)
homepage = f"https://{domain}"
screenshot = client.web.scrape(url=homepage, formats={"screenshot": True})
images = client.web.scrape(url=homepage, formats={"images": True})

print({
    "brand": brand,
    "styleguide": styleguide,
    "screenshot": screenshot.screenshot.data,
    "images": images.images.data,
})
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))
domain = "example.com"

brand = client.brand.retrieve(body: {type: :by_domain, domain: domain})
styleguide = client.web.extract_styleguide(domain: domain)
homepage = "https://#{domain}"
screenshot = client.web.scrape(url: homepage, formats: {screenshot: true})
images = client.web.scrape(url: homepage, formats: {images: true})

puts({
  brand: brand,
  styleguide: styleguide,
  screenshot: screenshot.screenshot.data,
  images: images.images.data,
}.inspect)
```

```go Go theme={null}
package main

import (
    "context"
    "fmt"
    "os"

    contextdev "github.com/context-dot-dev/context-go-sdk/v2"
    "github.com/context-dot-dev/context-go-sdk/v2/option"
    "github.com/context-dot-dev/context-go-sdk/v2/packages/param"
)

func main() {
    client := contextdev.NewClient(
        option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")),
    )

    domain := "example.com"
    brand, err := client.Brand.Get(context.Background(), contextdev.BrandGetParams{
        OfByDomain: &contextdev.BrandGetParamsBodyByDomain{Domain: domain},
    })
    if err != nil {
        panic(err)
    }

    styleguide, err := client.Web.ExtractStyleguide(context.Background(), contextdev.WebExtractStyleguideParams{
        Domain: param.NewOpt(domain),
    })
    if err != nil {
        panic(err)
    }

    homepage := "https://" + domain
    screenshot, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
        URL:     homepage,
        Formats: contextdev.WebScrapeParamsFormats{Screenshot: contextdev.Bool(true)},
    })
    if err != nil {
        panic(err)
    }

    images, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
        URL:     homepage,
        Formats: contextdev.WebScrapeParamsFormats{Images: contextdev.Bool(true)},
    })
    if err != nil {
        panic(err)
    }

    fmt.Println(map[string]any{
        "brand": brand,
        "styleguide": styleguide,
        "screenshot": screenshot.Screenshot.Data,
        "images": images.Images.Data,
    })
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$domain = 'example.com';

// The PHP Brand helper requires fields from incompatible lookup types.
$raw = $client->request(
    method: 'post',
    path: 'brand/retrieve',
    body: ['type' => 'by_domain', 'domain' => $domain],
);
$brand = json_decode((string) $raw->getBody(), true, flags: JSON_THROW_ON_ERROR);
$styleguide = $client->web->extractStyleguide(domain: $domain);
$homepage = 'https://'.$domain;
$screenshot = $client->web->scrape(formats: ['screenshot' => true], url: $homepage);
$images = $client->web->scrape(formats: ['images' => true], url: $homepage);

print_r([
    'brand' => $brand,
    'styleguide' => $styleguide,
    'screenshot' => $screenshot->screenshot->data,
    'images' => $images->images->data,
]);
```

```bash cURL theme={null}
curl https://api.context.dev/v1/brand/retrieve \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{"type":"by_domain","domain":"example.com"}'

curl --get https://api.context.dev/v1/web/styleguide \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --data-urlencode "domain=example.com"

curl https://api.context.dev/v1/web/scrape \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{"url":"https://example.com","formats":{"screenshot":true}}'

curl https://api.context.dev/v1/web/scrape \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{"url":"https://example.com","formats":{"images":true}}'
```

Retain successful inputs when an optional call fails. Inspect each Scrape output's `success` and `data`; HTTP 200 alone does not mean every format succeeded. You can combine screenshot and image formats into one [Scrape](https://docs.context.dev/scrape/overview) request.

For source copy, [scrape](https://docs.context.dev/scrape/markdown.md) selected product pages or use a [scoped crawl](https://docs.context.dev/crawl/scope.md). Store source URLs with claims. Website imagery is an observed asset, not evidence that your application has rights to reuse it.

## Approve a small theme

Choose an accent, logo, and font stack rather than copying every observed style. Keep explicit overrides separate from the latest snapshot. Use Brand assets for downloaded exports; [Logo Link](https://docs.context.dev/brand/logo-link.md#usage-restrictions) has different usage restrictions.

> [tab] Documents
>
> Use `approveTheme` to validate a chosen logo and color. Keep headings and body text on a neutral surface, with an accent for bounded elements.
>
> ```typescript document-theme.ts theme={null}
> export type DocumentTheme = {
>   clientName: string;
>   accent: string;
>   accentText: string;
>   fontStack: string;
>   logo: { url: string; width: number; height: number } | null;
>   sourceDomain: string;
>   sourceVersion: string;
> };
>
> export function accentText(hex: string) {
>   if (!/^#[0-9a-f]{6}$/i.test(hex)) throw new Error("Use a six-digit hex color");
>   const rgb = [1, 3, 5].map((offset) => parseInt(hex.slice(offset, offset + 2), 16) / 255);
>   const [r, g, b] = rgb.map((c) => c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
>   const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
>   const blackContrast = (luminance + 0.05) / 0.05;
>   const whiteContrast = 1.05 / (luminance + 0.05);
>   return blackContrast >= whiteContrast ? "#000000" : "#ffffff";
> }
>
> export function approveTheme(input: {
>   clientName: string;
>   accent?: string;
>   logo?: DocumentTheme["logo"];
>   sourceDomain: string;
>   sourceVersion: string;
> }): DocumentTheme {
>   const accent = input.accent ?? "#334155";
>   const logo = input.logo ?? null;
>   if (logo && (
>     new URL(logo.url).protocol !== "https:" ||
>     !Number.isFinite(logo.width) || !Number.isFinite(logo.height) ||
>     logo.width <= 0 || logo.height <= 0
>   )) throw new Error("Approve a valid HTTPS logo with dimensions");
>
>   return {
>     ...input,
>     accent,
>     accentText: accentText(accent),
>     logo,
>     fontStack: "Arial, Helvetica, sans-serif",
>   };
> }
> ```

> [tab] Websites
>
> Map approved values into a small set of semantic CSS roles and preserve saved overrides:
>
> ```typescript site-theme.ts theme={null}
> export type Theme = {
>   background: string;
>   text: string;
>   accent: string;
>   onAccent: string;
>   fontStack: string;
>   radius: number;
> };
>
> type ThemeOverrides = Partial<Pick<Theme, "accent" | "fontStack" | "radius">>;
>
> function accentText(hex: string) {
>   if (!/^#[0-9a-f]{6}$/i.test(hex)) throw new Error("Use a six-digit hex color");
>   const rgb = [1, 3, 5].map((offset) => parseInt(hex.slice(offset, offset + 2), 16) / 255);
>   const [r, g, b] = rgb.map((c) => c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
>   const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
>   return (luminance + 0.05) / 0.05 >= 1.05 / (luminance + 0.05)
>     ? "#000000" : "#ffffff";
> }
>
> export function makeTheme(
>   approvedAccent: string | null,
>   overrides: ThemeOverrides,
> ): Theme {
>   const accent = overrides.accent ?? approvedAccent ?? "#334155";
>   const radius = overrides.radius ?? 12;
>   if (!Number.isFinite(radius) || radius < 0 || radius > 32) {
>     throw new Error("Choose a radius between 0 and 32 pixels");
>   }
>   return {
>     background: "#ffffff",
>     text: "#171717",
>     accent,
>     onAccent: accentText(accent),
>     fontStack: overrides.fontStack ?? "Arial, Helvetica, sans-serif",
>     radius,
>   };
> }
> ```

Custom fonts need a loadable, licensed source and a tested fallback. Retain the company name when an image is missing; reserve image dimensions to avoid layout shifts.

## Render an editable preview

Use a fixed content schema and renderer. Keep model-generated text as text; do not inject it as executable markup. These React examples accept approved content and theme values:

> [tab] Document
>
> ```tsx ClientReport.tsx theme={null}
> import type { DocumentTheme } from "./document-theme";
>
> type Report = {
>   title: string;
>   author: string;
>   date: string;
>   summary: string;
>   findings: Array<{ heading: string; text: string; sourceUrl: string | null }>;
> };
>
> export function ClientReport({ theme, report }: {
>   theme: DocumentTheme;
>   report: Report;
> }) {
>   const logo = theme.logo;
>   const width = logo ? Math.min(160, 48 * logo.width / logo.height) : 0;
>   const height = logo ? width * logo.height / logo.width : 0;
>
>   return (
>     <article className="client-report" style={{ fontFamily: theme.fontStack }}>
>       <section className="report-page">
>         <header>
>           {logo && <img src={logo.url} alt={`${theme.clientName} logo`}
>             width={width} height={height} style={{ objectFit: "contain" }} />}
>           <p>Prepared for {theme.clientName}</p>
>           <p>Prepared by {report.author} · {report.date}</p>
>         </header>
>         <span style={{ background: theme.accent, color: theme.accentText,
>           display: "inline-block", padding: "6px 12px" }}>Client report</span>
>         <h1>{report.title}</h1>
>         <p>{report.summary}</p>
>       </section>
>       <section className="report-page">
>         <h2>Findings</h2>
>         {report.findings.map((finding, index) => (
>           <section className="report-finding" key={index}>
>             <h3>{finding.heading}</h3>
>             <p>{finding.text}</p>
>             {finding.sourceUrl && <p><a href={finding.sourceUrl}>Source</a></p>}
>           </section>
>         ))}
>         <footer>Theme version: {theme.sourceVersion}</footer>
>       </section>
>     </article>
>   );
> }
> ```
>
> ```css report.css theme={null}
> @page { size: A4; margin: 16mm; }
> .client-report { color: #171717; background: #fff; line-height: 1.5; }
> .report-page { max-width: 178mm; margin: 0 auto 32px; overflow-wrap: anywhere; }
> .report-page img { max-width: 100%; }
> .report-finding { break-inside: avoid; }
> .client-report footer { margin-top: 24px; font-size: 12px; }
> @media print {
>   .report-page { margin: 0; break-after: page; }
>   .report-page:last-child { break-after: auto; }
>   .client-report { print-color-adjust: exact; }
> }
> ```

> [tab] Website
>
> ```tsx LandingPage.tsx theme={null}
> import type { CSSProperties } from "react";
> import type { Theme } from "./site-theme";
>
> type PageContent = {
>   eyebrow: string;
>   headline: string;
>   description: string;
>   cta: { label: string; url: string };
>   features: Array<{ title: string; description: string; sourceUrl: string }>;
> };
>
> export function LandingPage({ theme, content, companyName }: {
>   theme: Theme;
>   content: PageContent;
>   companyName: string;
> }) {
>   const style = {
>     "--accent": theme.accent,
>     "--on-accent": theme.onAccent,
>     "--radius": `${theme.radius}px`,
>     background: theme.background,
>     color: theme.text,
>     fontFamily: theme.fontStack,
>   } as CSSProperties;
>
>   return (
>     <div className="brand-page" style={style}>
>       <header>{companyName}</header>
>       <main>
>         <p>{content.eyebrow}</p>
>         <h1>{content.headline}</h1>
>         <p>{content.description}</p>
>         <a className="brand-cta" href={content.cta.url}>{content.cta.label}</a>
>         <div className="brand-features">
>           {content.features.map((feature) => (
>             <section key={feature.title}>
>               <h2>{feature.title}</h2>
>               <p>{feature.description}</p>
>             </section>
>           ))}
>         </div>
>       </main>
>     </div>
>   );
> }
> ```
>
> ```css landing-page.css theme={null}
> .brand-page { padding: clamp(20px, 5vw, 64px); overflow-wrap: anywhere; }
> .brand-page main { max-width: 1120px; margin: 64px auto; }
> .brand-page h1 { max-width: 18ch; font-size: clamp(2rem, 5vw, 4rem); line-height: 1.1; }
> .brand-page p { max-width: 65ch; line-height: 1.6; }
> .brand-cta { display: inline-block; padding: 12px 20px; border-radius: var(--radius);
>   color: var(--on-accent); background: var(--accent); }
> .brand-cta:focus-visible { outline: 3px solid #171717; outline-offset: 4px; }
> .brand-features { display: grid; gap: 24px; margin-top: 48px;
>   grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); }
> ```

For email, map the same approved theme into your provider's template. For campaign images, keep text, logo, and source imagery in separate layers so each size can be reviewed and edited. A change to one channel must not overwrite approved content in another.

## Review and save a version

Inspect the final PDF, slide deck, browser preview, email, or image at its intended size. Check clipping, logo contrast, font fallback, links, source claims, and the identity of the sender or author.

Save the source domain, retrieval time, approved theme, content version, and renderer version. Refresh suggestions independently of approved edits. Publish only after review; a successful API request does not approve the artifact.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.