# Build a company directory with logos

> Add recognizable company logos to directories, job boards, and account lists, with fallbacks and persistent corrections.

```text Recipe prompt theme={null}
Implement this recipe in my project:
https://docs.context.dev/use-cases/company-directory-logos.md

Read the recipe and linked API guides, inspect this project's stack, and build the complete flow using its existing conventions.

Build a company directory with direct Logo Link image embeds using a public client ID and allowed referring domains. Support icon or wordmark choices, light and dark backgrounds, missing-image fallbacks, and persistent domain corrections or logo removal. Keep names readable when logos fail. Do not download, persist, or rehost Logo Link images; use server-side Brand retrieval only if richer profiles are needed.

Reuse existing Logo Link configuration. Add focused tests, run the relevant checks, and document the public client ID, allowed referring domains, and how to try the directory.

If Context.dev is not set up yet, follow https://docs.context.dev/agent-quickstart.md first.
```

Start with company names and verified domains, then add a logo to each row. Keep the directory useful when an image is missing, a company changes its name, or the first match belongs to a parent company.

[Vizzy uses company branding in profiles and job boards](https://www.context.dev/blog/vizzy-beautifies-profiles-and-job-boards-with-brand-dev). This recipe applies that pattern to a React directory.

## Choose the logo source

| Your application needs | Use |
| - | - |
| One hosted image for direct display | [Logo Link](https://docs.context.dev/brand/logo-link.md) |
| Multiple logo variants, colors, or a company profile | [Brand retrieval](https://docs.context.dev/brand/overview) |
| Assets for a document or creative export | Brand retrieval, with your own asset review and rendering workflow |

Logo Link uses a public client ID. Configure allowed referring domains in the [Logo Link dashboard](https://context.dev/dashboard/logolink), including the domains used for development and production. Keep secret API keys on the server when using Brand retrieval.

Embed Logo Link images directly. Do not download, persist, or rehost the returned image files. Normal browser and CDN caching directed by the response headers is allowed.

## Keep identity separate from presentation

Use your own company ID as the record key. A domain is an input to logo lookup; it should not replace the identity of an existing directory entry.

```typescript Directory model theme={null}
type Company = {
  id: string;
  name: string;
  domain: string | null;
  // Saved separately from automatically refreshed company data.
  domainOverride: string | null;
  hideLogo: boolean;
};

function logoUrl(
  domain: string,
  publicClientId: string,
  theme: "light" | "dark",
  type: "icon" | "wordmark",
) {
  const params = new URLSearchParams({ publicClientId, domain, theme, type });
  return `https://logos.context.dev/?${params}`;
}
```

Validate domains when importing or editing a company: accept a hostname such as `stripe.com`, and keep paths, email addresses, and unrelated platform domains out of the lookup field. Confirm the company when several entities share a name.

## Render a resilient directory

This component receives persisted company records and an edit callback from your application. Copy `Company` and `logoUrl` above into the same module. The component key resets a failed image when the domain or display settings change.

```tsx CompanyDirectory.tsx theme={null}
"use client";

import { useState } from "react";

function CompanyLogo({
  company, src, wordmark,
}: { company: Company; src: string | null; wordmark: boolean }) {
  const [failed, setFailed] = useState(false);
  const initials = company.name.trim().slice(0, 2).toUpperCase() || "?";
  const width = wordmark ? 112 : 40;

  return (
    <span style={{ width, height: 40, display: "grid", placeItems: "center" }}>
      {src && !failed ? (
        <img
          src={src}
          alt={`${company.name} logo`}
          width={width}
          height={40}
          loading="lazy"
          decoding="async"
          style={{ objectFit: "contain", maxWidth: "100%" }}
          onError={() => setFailed(true)}
        />
      ) : (
        <span aria-hidden="true">{initials}</span>
      )}
    </span>
  );
}

export function CompanyDirectory({
  companies, publicClientId, onEdit,
}: {
  companies: Company[];
  publicClientId: string;
  onEdit: (company: Company) => void;
}) {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [type, setType] = useState<"icon" | "wordmark">("icon");

  return (
    <section style={{
      background: theme === "dark" ? "#171717" : "#ffffff",
      color: theme === "dark" ? "#fafafa" : "#171717",
      padding: 24,
    }}>
      <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
        Use {theme === "light" ? "dark" : "light"} background
      </button>
      <button onClick={() => setType(type === "icon" ? "wordmark" : "icon")}>
        Show {type === "icon" ? "wordmarks" : "icons"}
      </button>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {companies.map((company) => {
          const domain = company.domainOverride ?? company.domain;
          const src = domain && !company.hideLogo
            ? logoUrl(domain, publicClientId, theme, type)
            : null;
          return (
            <li key={company.id} style={{
              display: "flex", alignItems: "center", gap: 16, padding: "12px 0",
              flexWrap: "wrap",
            }}>
              <CompanyLogo
                key={src ?? "fallback"}
                company={company}
                src={src}
                wordmark={type === "wordmark"}
              />
              <span>{company.name}</span>
              <button onClick={() => onEdit(company)}
                aria-label={`Edit brand for ${company.name}`}>
                Edit brand
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
```

`theme` describes the background where the image will appear: `light` prefers a dark asset, and `dark` prefers a light asset. It does not recolor the company's logo. Keep the company name visible even when every image is blocked.

## Save corrections independently

Connect **Edit brand** to a form that can change the lookup domain or hide the logo. Save those decisions against the company ID in your database, with the editor and update time. Reload the saved record after a successful edit.

On automatic enrichment, update `domain` but leave `domainOverride` and `hideLogo` untouched. Provide a separate **Use automatic branding** action that clears the override. This lets a correction survive a refresh without preventing future automatic updates.

| Situation | Directory behavior |
| - | - |
| No domain or no available image | Show the name and initials. |
| Parent-company or platform logo | Let an editor correct the domain or hide the image. |
| Image does not fit the surface | Switch the theme or choose a reviewed Brand variant. |
| Temporary image failure | Keep the row usable; retry on a later visit. |
| Rebrand | Refresh automatic data and retain explicit user choices. |

A logo does not establish affiliation, endorsement, or legal identity. Keep any such claims in separately verified directory fields.

## Check the result

Try the directory with a known domain, no domain, and a deliberately unavailable image. Switch between light and dark backgrounds and between icons and wordmarks. Save a corrected domain, reload the page, then run enrichment again: the correction should remain.

> [card] [Logo Link setup](https://docs.context.dev/brand/logo-link.md)
>
> Configure the public client ID, referring domains, and image parameters.

> [card] [Branded documents](https://docs.context.dev/use-cases/branded-documents.md)
>
> Use reviewed brand assets in reports and proposals.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.