# Industry classification

> Read industry and subindustry labels from a Brand profile.

Enriched Industry Classification (EIC) describes what a company does with industry and subindustry pairs. It is included in [Brand profiles](https://docs.context.dev/brand/overview); there is no separate EIC endpoint.

## Read the labels

Request a Brand profile, then inspect `brand.industries.eic`. Abridged profile:

```json theme={null}
{"brand":{"industries":{"eic":[{"industry":"Finance","subindustry":"Payments & Money Movement"},{"industry":"Finance","subindustry":"Financial Infrastructure & APIs"}]}}}
```

The taxonomy contains 24 industries and 220 subindustries. A company can have more than one pair; an empty array means no classification was returned.

## Store and display classifications

Keep the industry and subindustry together and preserve all returned pairs. Use a primary label for compact displays while retaining the others for filtering. Store any user correction separately so a later enrichment does not overwrite it.

The [Brand reference](https://docs.context.dev/api-reference/brand-intelligence/brand.md) lists current enum values. Classification is a discovered company attribute; review ambiguous labels before using them in decisions that need verified industry data.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.