# Product

> Extract product details from a product page.

Enable `formats.product` to read product details from the page. `product.data` contains `isProductPage` and `product`; a successful non-product result has `isProductPage: false` and `product: null`. If the page returns 404, the product output fails with `NOT_FOUND`.

## Request a product

```typescript TypeScript theme={null}
const page = await client.web.scrape({
  url: "https://example.com/products/travel-mug",
  formats: { product: true },
  productParams: { dedupeImages: true },
});

if (page.product.data?.isProductPage) {
  console.log(page.product.data.product?.name);
  console.log(page.product.data.product?.price);
}
```

```python Python theme={null}
page = client.web.scrape(
    url="https://example.com/products/travel-mug",
    formats={"product": True},
    product_params={"dedupe_images": True},
)

if page.product.data and page.product.data.is_product_page:
    print(page.product.data.product.name)
    print(page.product.data.product.price)
```

```ruby Ruby theme={null}
page = client.web.scrape(
  url: "https://example.com/products/travel-mug",
  formats: {product: true},
  product_params: {dedupe_images: true},
)

if page.product.data&.is_product_page
  puts page.product.data.product.name
  puts page.product.data.product.price
end
```

```go Go theme={null}
page, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
    URL:           "https://example.com/products/travel-mug",
    Formats:       contextdev.WebScrapeParamsFormats{Product: contextdev.Bool(true)},
    ProductParams: contextdev.WebScrapeParamsProductParams{DedupeImages: contextdev.Bool(true)},
})
if err != nil {
    panic(err)
}

if page.Product.Data != nil && page.Product.Data.IsProductPage {
    fmt.Println(page.Product.Data.Product.Name)
    fmt.Println(page.Product.Data.Product.Price)
}
```

```php PHP theme={null}
$page = $client->web->scrape(
    formats: ['product' => true],
    url: 'https://example.com/products/travel-mug',
    productParams: ['dedupeImages' => true],
);

if ($page->product->data?->isProductPage) {
    echo $page->product->data->product->name, PHP_EOL;
    echo $page->product->data->product->price, PHP_EOL;
}
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/scrape \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/products/travel-mug",
    "formats": { "product": true },
    "productParams": { "dedupeImages": true }
  }'
```

## Fields to use

| Field | Meaning |
| - | - |
| `name`, `description`, `brand` | Product identity. |
| `sku` | Product identifier such as a SKU or model number. |
| `price`, `regularPrice`, `currency` | Current price, list price before any discount, and ISO 4217 currency, when available. |
| `availability` | `in_stock`, `out_of_stock`, `limited_availability`, `preorder`, `backorder`, `made_to_order`, or `discontinued`; `null` when the page reports none. |
| `images` | Up to seven source image URLs, main image first. |
| `targetAudience` | Intended audience, as a list of strings. |
| `variants` | Product variations such as colors or sizes. Each variant has a `sku`, `attributes` (explicit variant attributes such as color, size, material, and pattern declared by the page), a `url` that may be shared by variants, and the source `images` attached to it. The list may not include every variation the store offers. |

Missing scalar values are `null`; missing lists are `[]`. Source images are not re-hosted.

## Deduplicate images

```json theme={null}
{
  "url": "https://example.com/products/chair",
  "formats": {
    "product": true
  },
  "productParams": {
    "dedupeImages": true
  }
}
```

Set `productParams.dedupeImages: true` to drop visually duplicate images from `images`, keeping the largest copy. `imageUrl` is the first remaining image. It defaults to `false` and adds no credits.

Product extraction uses the unfiltered page. For price updates, set `maxAgeMs: 0`. Use [Batches](https://docs.context.dev/batches/overview) with `formats.product: true` to extract products from a list of URLs.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.