# Go

> Install the Go SDK, scrape a page, look up a brand, and set timeouts and retries.

The Go SDK requires Go 1.22 or later. Import the `/v2` module path shown below. [SDKs](https://docs.context.dev/sdks) covers the API key and the defaults all SDKs share.

## Install

In a new directory, create a module, then add the SDK. Skip `go mod init` if the project already has a `go.mod`.

```bash theme={null}
go mod init example.com/context-quickstart
go get github.com/context-dot-dev/context-go-sdk/v2
```

## Scrape a page

Save this as `main.go` and run `go run main.go`. It prints the page as Markdown, starting with `# Example Domain`.

```go main.go theme={null}
package main

import (
    "context"
    "fmt"
    "os"

    contextdev "github.com/context-dot-dev/context-go-sdk/v2"
    "github.com/context-dot-dev/context-go-sdk/v2/option"
)

func main() {
    client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))

    page, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
        URL:          "https://example.com",
        Formats:      contextdev.WebScrapeParamsFormats{Markdown: contextdev.Bool(true)},
        SharedParams: contextdev.WebScrapeParamsSharedParams{MainContentOnly: contextdev.Bool(true)},
    })
    if err != nil {
        panic(err)
    }

    fmt.Println(page.Markdown.Data)
}
```

## Look up a brand

In `main`, replace the scrape request, error check, and print statement with this lookup. It prints the company name.

```go theme={null}
response, err := client.Brand.Get(context.Background(), contextdev.BrandGetParams{
    OfByDomain: &contextdev.BrandGetParamsBodyByDomain{
        Domain: "stripe.com",
    },
})
if err != nil {
    panic(err)
}

fmt.Println(response.Brand.Title)
```

## Notes

* Optional fields take helpers, such as `contextdev.Bool(true)`, `contextdev.Int(0)`, and `contextdev.String("US")`; enum fields take plain strings.
* Requests have no default timeout. Set one per attempt with `option.WithRequestTimeout(120 * time.Second)`, or for the whole call with a `context` deadline. `option.WithMaxRetries(0)` turns off retries.
* If a params struct has no field for an option you need, such as `HighlightsParams`, `JsonParams`, or `ProductParams`, your installed version predates it. Send the request with `client.Post`, as described in [SDKs](https://docs.context.dev/sdks#use-the-low-level-request-method).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.