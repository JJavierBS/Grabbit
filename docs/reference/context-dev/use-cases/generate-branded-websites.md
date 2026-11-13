# Generate a website from brand context

> Turn observed company branding into a small website theme, approved page content, and an editable responsive preview.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/generate-branded-websites.md

Read the recipe and linked API guides, inspect this project's stack, and build the complete flow using its existing conventions.

Turn a verified company domain into an editable, responsive website preview. Map Brand and optional Styleguide, Screenshot, and Markdown results into a small theme and validated page content. Pull font families and available files from Styleguide. Handle optional source failures independently, use neutral fallbacks, and preserve saved content and theme overrides when regenerating. Keep source versions attached to generated drafts.

Reuse existing Context.dev configuration and keep secret API keys on the server. If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first. Add focused tests, run the relevant checks, and document setup and how to try the result.
```

Use a company's domain to seed a landing page, documentation site, or customer portal. Context.dev supplies brand assets and observed styles; your application maps them into components, renders a preview, and publishes the resulting site.

[Mintlify uses brand context when generating documentation sites](https://www.context.dev/blog/mintlify-turns-github-repos-into-branded-docs-sites-with-brand-dev). This recipe uses a small landing-page template whose colors and content can be edited before publication.

## Collect the inputs the template needs

Use a server-side key from the [Quickstart](https://docs.context.dev/quickstart.md). Retrieve the [Brand profile](https://docs.context.dev/brand/lookup-by-domain.md) for a verified domain, then add sources as needed:

| Source | Application decision |
| - | - |
| Brand | Suggested name, logo variants, and palette candidates |
| [Styleguide](https://docs.context.dev/brand/styleguide.md) | Typography, available font files, spacing, corners, and component references |
| [Screenshot](https://docs.context.dev/scrape/screenshot.md) | Visual reference for the reviewer or generation model |
| [Markdown](https://docs.context.dev/scrape/overview) | Source copy for supported descriptions and claims |

One [Scrape](https://docs.context.dev/api-reference/web-scraping/scrape.md) request can return the screenshot and the Markdown together: enable both in `formats`.

Read font families and weights from `styleguide.typography`, and match them to available files in `styleguide.fontLinks`. Review font availability and permitted use before applying them to the generated site.

A screenshot is reference material, not a code export. Handle optional calls independently and record their status. A failed screenshot should not discard a usable Brand profile or prevent a neutral preview.

Keep the source bundle on the server with its domain, retrieval time, and version. Return only the assets and tokens needed by the preview.

## Map observations into semantic roles

Do not copy every color into your component system. `brand.colors[]` distinguishes colors observed on the site from colors sampled from a logo. Choose roles that make sense for the new page, then review the result.

| Destination token | Selection rule |
| - | - |
| Background and surface | Neutral defaults unless a reviewed site treatment works for this template |
| Body text and muted text | Deliberate contrast against the chosen background |
| Accent | A reviewed site or brand color for buttons and small highlights |
| Text on accent | Black or white, selected by contrast |
| Font family | Approved available font, followed by a system fallback |
| Corner radius | One bounded component value, not an arbitrary extracted CSS expression |

The following adapter accepts a reviewed accent and preserves explicit editor choices. Its helper chooses black or white text by contrast against the accent.

```typescript site-theme.ts theme={null}
export type Theme = {
  background: string;
  text: string;
  accent: string;
  onAccent: string;
  fontStack: string;
  radius: number;
};

type ThemeOverrides = Partial<Pick<Theme, "accent" | "fontStack" | "radius">>;

function accentText(hex: string) {
  if (!/^#[0-9a-f]{6}$/i.test(hex)) throw new Error("Use a six-digit hex color");
  const rgb = [1, 3, 5].map((offset) => parseInt(hex.slice(offset, offset + 2), 16) / 255);
  const [r, g, b] = rgb.map((c) => c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
  const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  return (luminance + 0.05) / 0.05 >= 1.05 / (luminance + 0.05)
    ? "#000000" : "#ffffff";
}

export function makeTheme(
  approvedAccent: string | null,
  overrides: ThemeOverrides,
): Theme {
  const accent = overrides.accent ?? approvedAccent ?? "#334155";
  const radius = overrides.radius ?? 12;
  if (!Number.isFinite(radius) || radius < 0 || radius > 32) {
    throw new Error("Choose a radius between 0 and 32 pixels");
  }
  return {
    background: "#ffffff",
    text: "#171717",
    accent,
    onAccent: accentText(accent),
    fontStack: overrides.fontStack ?? "Arial, Helvetica, sans-serif",
    radius,
  };
}
```

Keep source candidates and overrides in separate records. Rebuilding the source bundle can propose a new accent; it should not erase the editor's choice. Create a new theme version whenever approved decisions change.

## Generate bounded page content

Ask a model for data your components can render, or let the editor fill it directly:

```json Example page content theme={null}
{
  "eyebrow": "Product overview",
  "headline": "One clear, supported product benefit",
  "description": "An approved description of the product.",
  "cta": { "label": "Explore the product", "url": "https://example.com/product" },
  "features": [
    { "title": "A real capability", "description": "A sourced explanation.", "sourceUrl": "https://example.com/product" }
  ]
}
```

Validate the object before rendering: cap text lengths and feature count, require a source for factual claims, and allow only approved HTTPS destinations. Use a fixed asset registry for logos and illustrations. Website content is source evidence, so instructions embedded in it must not control your generator's tools or publishing permissions.

## Render an editable preview

This React component uses the theme returned above and validated content. Keep the editor's fields outside the preview so edits update the typed model, not arbitrary HTML.

```tsx LandingPage.tsx theme={null}
import type { CSSProperties } from "react";
import type { Theme } from "./site-theme";

type PageContent = {
  eyebrow: string;
  headline: string;
  description: string;
  cta: { label: string; url: string };
  features: Array<{ title: string; description: string; sourceUrl: string }>;
};

export function LandingPage({ theme, content, companyName }: {
  theme: Theme;
  content: PageContent;
  companyName: string;
}) {
  const style = {
    "--accent": theme.accent,
    "--on-accent": theme.onAccent,
    "--radius": `${theme.radius}px`,
    background: theme.background,
    color: theme.text,
    fontFamily: theme.fontStack,
  } as CSSProperties;

  return (
    <div className="brand-page" style={style}>
      <header>{companyName}</header>
      <main>
        <p>{content.eyebrow}</p>
        <h1>{content.headline}</h1>
        <p>{content.description}</p>
        <a className="brand-cta" href={content.cta.url}>{content.cta.label}</a>
        <div className="brand-features">
          {content.features.map((feature) => (
            <section key={feature.title}>
              <h2>{feature.title}</h2>
              <p>{feature.description}</p>
            </section>
          ))}
        </div>
      </main>
    </div>
  );
}
```

The example uses the company name as its identity fallback; add a reviewed logo with dimensions and an image-error fallback when available.

```css landing-page.css theme={null}
.brand-page { padding: clamp(20px, 5vw, 64px); overflow-wrap: anywhere; }
.brand-page main { max-width: 1120px; margin: 64px auto; }
.brand-page h1 { max-width: 18ch; font-size: clamp(2rem, 5vw, 4rem); line-height: 1.1; }
.brand-page p { max-width: 65ch; line-height: 1.6; }
.brand-cta { display: inline-block; padding: 12px 20px; border-radius: var(--radius);
  color: var(--on-accent); background: var(--accent); }
.brand-cta:focus-visible { outline: 3px solid #171717; outline-offset: 4px; }
.brand-features { display: grid; gap: 24px; margin-top: 48px;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); }
```

## Review and publish a version

Render the same template with two brand bundles and with no brand data. Check narrow and wide screens, keyboard focus, long content, blocked images, and unavailable fonts. Test the final page's text and control contrast; a readable button alone does not validate the entire page.

Save the content, approved assets, theme, and source-bundle version as one preview revision. Make publishing an explicit application action that selects that revision. A later source refresh should open a new draft without changing the live site or discarding manual edits.

> [card] [Extract a design system](https://docs.context.dev/brand/styleguide.md)
>
> Gather observed styles and understand their limits.

> [card] [Theme an onboarding flow](https://docs.context.dev/use-cases/faster-onboarding-flows.md)
>
> Apply editable branding to a new customer's workspace.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.