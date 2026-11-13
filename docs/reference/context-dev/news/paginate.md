# Paginate news

> Continue a news search using the returned cursor.

Set `limit` from 1 to 100; it defaults to 10. When `has_more` is true, send `next_cursor` as `cursor` on the next request. A natural-language search returns up to 100 matches across all pages.

## Continue the same search

Keep `searchBy`, `filterBy`, and `sortBy` unchanged. Only add the returned cursor or adjust the page limit. A cursor is opaque; do not construct or edit one.

```text theme={null}
cursor = absent
repeat:
  request the same search with cursor
  save data, deduplicating by article id
  stop when has_more is false or next_cursor is absent
  cursor = next_cursor
```

For a backfill, set a fixed date window and save the cursor after each processed page. Stop on a repeated cursor rather than creating an endless loop. Handle [rate limits](https://docs.context.dev/optimization/rate-limits.md) before requesting the next page.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.