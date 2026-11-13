# Sitemap monitors

> Watch a sitemap for URLs that are added or removed, filtered by path patterns.

A `sitemap` target watches the set of URLs in a sitemap. Detection is always `exact`: a change is any URL that appears or disappears after filtering.

## Fields

| Field | Default | Notes |
| - | - | - |
| `url` | Required | A URL ending in `.xml` or `.xml.gz` is read as that sitemap file. Any other URL reads the domain's sitemaps. |
| `include` | None | Up to 50 path patterns of 1–200 characters, such as `/blog/*`. A pattern must match the whole path, and `*` matches anything. |
| `exclude` | None | Path patterns to leave out, in the same format. |
| `max_urls` | `5000` | 1–10,000. The cap applies to URLs as read, before `include` and `exclude`. |

## How a run works

URLs are normalized (lowercase host, no trailing slash or fragment) and kept only for the site and its subdomains. When a run sees a difference, it reads the sitemap again and reports only the URLs both reads agree on, so a sitemap that is mid-rebuild doesn't produce a false change.

## Example

Report new blog posts and ignore tag pages.

```json theme={null}
{
  "name": "New blog posts",
  "target": {
    "type": "sitemap",
    "url": "https://example.com/sitemap.xml",
    "include": ["/blog/*"],
    "exclude": ["/blog/tag/*"]
  }
}
```

## Related

* [Targets](https://docs.context.dev/monitors/targets): detection rules and how to update a target.
* [Runs and changes](https://docs.context.dev/monitors/runs-and-changes.md): what a sitemap change contains.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.