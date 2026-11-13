# Ruby

> Install the Ruby SDK, scrape a page, look up a brand, and set timeouts and retries.

The `context.dev` gem requires Ruby 3.2 or later. [SDKs](https://docs.context.dev/sdks) covers the API key and the defaults all SDKs share.

## Install

```bash theme={null}
gem install context.dev
```

With Bundler, add `gem "context.dev"` to your `Gemfile`, run `bundle install`, and run the examples with `bundle exec ruby`.

## Scrape a page

Save this as `scrape.rb` and run `ruby scrape.rb`. It prints the page as Markdown, starting with `# Example Domain`.

```ruby scrape.rb theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.web.scrape(
  url: "https://example.com",
  formats: {markdown: true},
  shared_params: {main_content_only: true},
)

puts page.markdown.data
```

## Look up a brand

Replace the request and the `puts` line with this lookup. It prints the company name.

```ruby theme={null}
response = client.brand.retrieve(
  body: {type: :by_domain, domain: "stripe.com"}
)

puts response.brand&.title
```

## Notes

* Nested parameters are hashes with `snake_case` symbol keys.
* `brand.retrieve` takes the lookup as `body:`, because the lookup `type` decides which fields are valid.
* Set `timeout` in seconds and `max_retries` on the client: `ContextDev::Client.new(timeout: 120, max_retries: 0)`.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.