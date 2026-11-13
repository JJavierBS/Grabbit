# Scrape Anything

> Scrape anything from a URL on the internet. Returns the outputs you enable in formats. Handles PDFs, DOCX, PPT, XLSX, and 40 other file formats.

From 1 credit

See the [guide](https://docs.context.dev/scrape/overview) for examples and usage.

Use a [custom parser](https://docs.context.dev/scrape/parse-fields.md) or [pre-built parser](https://docs.context.dev/scrape/prebuilt-parsers) to return structured data in `parsed.data`.


## OpenAPI

````yaml POST /web/scrape
openapi: 3.1.0
info:
  title: Context.dev API
  description: >-
    Scrape, crawl, search, and monitor websites, and retrieve brand, people, and
    news data.
  version: 1.0.0
servers:
  - url: https://api.context.dev/v1
security: []
tags:
  - name: Webhooks
    description: Inspect and retry batch and monitor webhook deliveries.
  - name: Logs
    description: Read your organization's API request logs.
  - name: Usage
    description: Read your organization's credit balance and usage history.
  - name: Browser Profiles
    description: See the authenticated browser profiles your organization created.
  - name: Agent Feedback
    description: Report API issues and documentation mismatches.
  - name: Batches
    description: Scrape many pages or crawl a site asynchronously.
  - name: Monitors
    description: Watch websites for exact or meaningful changes.
  - name: Access Policies
    description: Control which websites your requests can access.
  - name: News
    description: Search live and historical news about a company.
  - name: Answers
    description: Answer a research task from the live web in the JSON shape you ask for.
paths:
  /web/scrape:
    post:
      tags:
        - Web Scraping
      summary: Scrape Anything
      description: >-
        Scrape anything from a URL on the internet. Returns the outputs you
        enable in formats. Handles PDFs, DOCX, PPT, XLSX, and 40 other file
        formats.
      operationId: scrapeWeb
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ScrapeRequest'
            examples:
              Default:
                summary: Markdown
                value:
                  url: https://example.com
                  formats:
                    markdown: true
              Screenshot:
                summary: Take a screenshot
                value:
                  url: https://example.com
                  formats:
                    screenshot: true
              Highlights:
                summary: Extract passages that answer a question
                value:
                  url: https://en.wikipedia.org/wiki/IEEE_Frank_Rosenblatt_Award
                  formats:
                    highlights: true
                  highlightsParams:
                    query: Who received the IEEE Frank Rosenblatt Award in 2010?
              Parse fields:
                summary: Parse fields
                value:
                  url: https://example.com
                  formats:
                    parse: true
                  parseParams:
                    rules:
                      title: h1
              All outputs:
                summary: Every output except JSON
                value:
                  url: https://example.com
                  formats:
                    html: true
                    markdown: true
                    screenshot: true
                    images: true
                    bytes: true
                    parse: true
                    highlights: true
                    product: true
                  parseParams:
                    rules:
                      title: h1
                  highlightsParams:
                    query: What is this page about?
              With options:
                summary: Shared settings, specific params, and request controls
                value:
                  url: https://example.com
                  formats:
                    markdown: true
                    screenshot: true
                    images: true
                  sharedParams:
                    theme: dark
                    waitFor: main
                    mainContentOnly: true
                    excludeSelectors:
                      - nav
                      - footer
                  markdownParams:
                    includeLinks: false
                  screenshotParams:
                    area: fullPage
                  imageParams:
                    enrich:
                      - dimensions
                  maxAgeMs: 0
                  timeoutOpts:
                    milliseconds: 60000
                    behavior: fail
                  tags:
                    - product-sync
              Shared inputs:
                summary: Country, headers, waiting, and freshness
                value:
                  url: https://example.com
                  formats:
                    screenshot: true
                    images: true
                    bytes: true
                  sharedParams:
                    country: US
                    headers:
                      Accept-Language: en-US
                    waitFor: 500
                  maxAgeMs: 0
              JSON extraction:
                summary: Extract JSON with a schema
                value:
                  url: https://example.com
                  formats:
                    json: true
                  jsonParams:
                    schema:
                      type: object
                      properties:
                        title:
                          type: string
                          description: Main heading.
                        isPlaceholder:
                          type: boolean
                          description: Whether the page is a placeholder domain.
                      required:
                        - title
                        - isPlaceholder
                      additionalProperties: false
                    instructions: Use the first heading as the title.
              Product:
                summary: Extract a product
                value:
                  url: https://example.com/products/travel-mug
                  formats:
                    product: true
                  productParams:
                    dedupeImages: true
      responses:
        '200':
          description: >-
            Every output key is present; check each output's `success`. Failed
            outputs include `error_code` and `message`.
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ScrapeResponse'
              examples:
                Default:
                  summary: Markdown
                  value:
                    url: https://example.com/
                    html:
                      requested: false
                      success: null
                      data: null
                    markdown:
                      requested: true
                      success: true
                      data: '# Example Domain'
                    screenshot:
                      requested: false
                      success: null
                      data: null
                    images:
                      requested: false
                      success: null
                      data: null
                    bytes:
                      requested: false
                      success: null
                      data: null
                    parsed:
                      type: custom
                      requested: false
                      success: null
                      data: null
                    highlights:
                      requested: false
                      success: null
                      data: null
                    json:
                      requested: false
                      success: null
                      data: null
                    product:
                      requested: false
                      success: null
                      data: null
                    profile: null
                    metadata:
                      sourceUrl: https://example.com
                      finalUrl: https://example.com/
                      title: Example Domain
                    request_id: d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37
                    cache_metadata:
                      status: miss
                      age_ms: 0
                    key_metadata:
                      credits_consumed: 1
                      credits_remaining: 999
                Partial success:
                  summary: HTML and Markdown returned when a screenshot fails
                  value:
                    url: https://example.com/
                    html:
                      requested: true
                      success: true
                      data: <h1>Example Domain</h1>
                    markdown:
                      requested: true
                      success: true
                      data: '# Example Domain'
                    screenshot:
                      requested: true
                      success: false
                      data: null
                      error_code: REQUEST_TIMEOUT
                      message: >-
                        This output was not ready before the deadline. Raise
                        timeoutOpts.milliseconds or retry.
                    images:
                      requested: false
                      success: null
                      data: null
                    bytes:
                      requested: false
                      success: null
                      data: null
                    parsed:
                      type: custom
                      requested: false
                      success: null
                      data: null
                    highlights:
                      requested: false
                      success: null
                      data: null
                    json:
                      requested: false
                      success: null
                      data: null
                    product:
                      requested: false
                      success: null
                      data: null
                    profile: null
                    isPartial: true
                    metadata:
                      sourceUrl: https://example.com/
                      finalUrl: https://example.com/
                    request_id: d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37
                    cache_metadata:
                      status: miss
                      age_ms: 0
                Screenshot:
                  summary: Screenshot
                  value:
                    url: https://example.com/
                    html:
                      requested: false
                      success: null
                      data: null
                    markdown:
                      requested: false
                      success: null
                      data: null
                    screenshot:
                      requested: true
                      success: true
                      data: >-
                        data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQmcAAAAASUVORK5CYII=
                    images:
                      requested: false
                      success: null
                      data: null
                    bytes:
                      requested: false
                      success: null
                      data: null
                    parsed:
                      type: custom
                      requested: false
                      success: null
                      data: null
                    highlights:
                      requested: false
                      success: null
                      data: null
                    json:
                      requested: false
                      success: null
                      data: null
                    product:
                      requested: false
                      success: null
                      data: null
                    profile: null
                    metadata:
                      sourceUrl: https://example.com/
                      finalUrl: https://example.com/
                    request_id: d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37
                    cache_metadata:
                      status: miss
                      age_ms: 0
                All outputs:
                  summary: Every output except JSON
                  value:
                    url: https://example.com/
                    html:
                      requested: true
                      success: true
                      data: <h1>Example Domain</h1>
                    markdown:
                      requested: true
                      success: true
                      data: '# Example Domain'
                    screenshot:
                      requested: true
                      success: true
                      data: >-
                        data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQmcAAAAASUVORK5CYII=
                    images:
                      requested: true
                      success: true
                      data:
                        - url: https://example.com/hero.jpg
                          alt: Product photo
                    bytes:
                      requested: true
                      success: true
                      data:
                        contentType: text/html
                        base64: PGgxPkV4YW1wbGUgRG9tYWluPC9oMT4=
                    parsed:
                      type: custom
                      requested: true
                      success: true
                      data:
                        title: Example Domain
                    highlights:
                      requested: true
                      success: true
                      data:
                        - Example Domain
                    json:
                      requested: false
                      success: null
                      data: null
                    product:
                      requested: true
                      success: true
                      data:
                        isProductPage: false
                        product: null
                    profile: null
                    metadata:
                      sourceUrl: https://example.com/
                      finalUrl: https://example.com/
                    request_id: d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37
                    cache_metadata:
                      status: miss
                      age_ms: 0
                Parse fields:
                  summary: Parsed fields without an HTML output
                  value:
                    url: https://example.com/
                    html:
                      requested: false
                      success: null
                      data: null
                    markdown:
                      requested: false
                      success: null
                      data: null
                    screenshot:
                      requested: false
                      success: null
                      data: null
                    images:
                      requested: false
                      success: null
                      data: null
                    bytes:
                      requested: false
                      success: null
                      data: null
                    parsed:
                      type: custom
                      requested: true
                      success: true
                      data:
                        title: Example Domain
                    highlights:
                      requested: false
                      success: null
                      data: null
                    json:
                      requested: false
                      success: null
                      data: null
                    product:
                      requested: false
                      success: null
                      data: null
                    profile: null
                    metadata:
                      sourceUrl: https://example.com/
                      finalUrl: https://example.com/
                    request_id: d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37
                    cache_metadata:
                      status: miss
                      age_ms: 0
                Shared inputs:
                  summary: Shared browser settings
                  value:
                    url: https://example.com/
                    html:
                      requested: false
                      success: null
                      data: null
                    markdown:
                      requested: false
                      success: null
                      data: null
                    screenshot:
                      requested: true
                      success: true
                      data: >-
                        data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQmcAAAAASUVORK5CYII=
                    images:
                      requested: true
                      success: true
                      data:
                        - url: https://example.com/hero.jpg
                          alt: Product photo
                    bytes:
                      requested: true
                      success: true
                      data:
                        contentType: text/html; charset=utf-8
                        base64: >-
                          PGh0bWw+PGJvZHk+PGgxPkV4YW1wbGUgRG9tYWluPC9oMT48L2JvZHk+PC9odG1sPg==
                    parsed:
                      type: custom
                      requested: false
                      success: null
                      data: null
                    highlights:
                      requested: false
                      success: null
                      data: null
                    json:
                      requested: false
                      success: null
                      data: null
                    product:
                      requested: false
                      success: null
                      data: null
                    profile: null
                    metadata:
                      sourceUrl: https://example.com/
                      finalUrl: https://example.com/
                    request_id: d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37
                    cache_metadata:
                      status: miss
                      age_ms: 0
                JSON:
                  summary: JSON extraction
                  value:
                    url: https://example.com/
                    html:
                      requested: false
                      success: null
                      data: null
                    markdown:
                      requested: false
                      success: null
                      data: null
                    screenshot:
                      requested: false
                      success: null
                      data: null
                    images:
                      requested: false
                      success: null
                      data: null
                    bytes:
                      requested: false
                      success: null
                      data: null
                    parsed:
                      type: custom
                      requested: false
                      success: null
                      data: null
                    highlights:
                      requested: false
                      success: null
                      data: null
                    json:
                      requested: true
                      success: true
                      data:
                        title: Example Domain
                        isPlaceholder: true
                    product:
                      requested: false
                      success: null
                      data: null
                    profile: null
                    metadata:
                      sourceUrl: https://example.com/
                      finalUrl: https://example.com/
                    request_id: d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37
                    cache_metadata:
                      status: miss
                      age_ms: 0
                Product:
                  summary: Product detail page
                  value:
                    url: https://example.com/products/travel-mug
                    html:
                      requested: false
                      success: null
                      data: null
                    markdown:
                      requested: false
                      success: null
                      data: null
                    screenshot:
                      requested: false
                      success: null
                      data: null
                    images:
                      requested: false
                      success: null
                      data: null
                    bytes:
                      requested: false
                      success: null
                      data: null
                    parsed:
                      type: custom
                      requested: false
                      success: null
                      data: null
                    highlights:
                      requested: false
                      success: null
                      data: null
                    json:
                      requested: false
                      success: null
                      data: null
                    product:
                      requested: true
                      success: true
                      data:
                        isProductPage: true
                        product:
                          name: Insulated Travel Mug 16 oz
                          description: >-
                            Double-wall stainless steel mug that keeps drinks
                            hot for six hours.
                          brand: Example Goods
                          sku: MUG-16-BLK
                          price: 24.99
                          regularPrice: 29.99
                          currency: USD
                          availability: in_stock
                          category: Drinkware
                          imageUrl: https://example.com/images/travel-mug-black.jpg
                          images:
                            - https://example.com/images/travel-mug-black.jpg
                            - https://example.com/images/travel-mug-lid.jpg
                          dimensions:
                            - 'Height: 18 cm'
                          features:
                            - 'Capacity: 16 oz'
                            - Dishwasher safe
                          targetAudience: []
                          tags:
                            - travel
                            - insulated
                          variants:
                            - sku: MUG-16-BLK
                              attributes:
                                color: Black
                              url: >-
                                https://example.com/products/travel-mug?variant=1
                              images:
                                - >-
                                  https://example.com/images/travel-mug-black.jpg
                    profile: null
                    metadata:
                      sourceUrl: https://example.com/products/travel-mug
                      finalUrl: https://example.com/products/travel-mug
                    request_id: d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37
                    cache_metadata:
                      status: miss
                      age_ms: 0
        '400':
          description: >-
            Invalid request: unknown or conflicting options, a non-public URL,
            or waits longer than the timeout.
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '401':
          description: >-
            Missing, invalid, or disabled API key. Legacy deployments may return
            401 USAGE_EXCEEDED for credit exhaustion.
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '402':
          description: >-
            Insufficient credits (`USAGE_EXCEEDED`); authentication is valid.
            Retry once funded. Legacy deployments may return 401.
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '403':
          description: >-
            Browser actions need a paid plan, `zdr` isn't enabled, or the API
            key lacks permission. An access policy can also block the website
            (`ACCESS_POLICY_DENIED`).
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '408':
          description: 'The request reached its deadline with `behavior: "fail"`.'
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '409':
          description: >-
            The browser profile is already in use. Wait for that request to
            finish.
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '410':
          description: >-
            The browser profile is unavailable. Create a new profile or check
            the ID and organization.
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '422':
          description: >-
            Authentication failed or a saved session or identity expired. Check
            error_code before retrying. PROFILE_SESSION_EXPIRED and
            PROFILE_REAUTHENTICATION_REQUIRED require a new profile.
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '429':
          description: Rate limit exceeded.
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: The scrape could not be completed.
          headers:
            X-Request-Id:
              $ref: '#/components/headers/RequestId'
            X-RateLimit-Limit:
              $ref: '#/components/headers/RateLimitLimit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/RateLimitRemaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/RateLimitReset'
            X-RateLimit-Mode:
              $ref: '#/components/headers/RateLimitMode'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
      security:
        - bearerAuth: []
components:
  schemas:
    ScrapeRequest:
      type: object
      properties:
        url:
          type: string
          minLength: 1
          format: uri
          pattern: ^[Hh][Tt][Tt][Pp][Ss]?://
          description: Public HTTP or HTTPS URL to scrape.
        formats:
          $ref: '#/components/schemas/ScrapeFormats'
        sharedParams:
          $ref: '#/components/schemas/ScrapeSharedParams'
        markdownParams:
          $ref: '#/components/schemas/ScrapeMarkdownParams'
        screenshotParams:
          $ref: '#/components/schemas/ScrapeScreenshotParams'
        imageParams:
          $ref: '#/components/schemas/ScrapeImageParams'
        parseParams:
          $ref: '#/components/schemas/ScrapeParseParams'
        productParams:
          $ref: '#/components/schemas/ScrapeProductParams'
        highlightsParams:
          $ref: '#/components/schemas/ScrapeHighlightsParams'
        jsonParams:
          $ref: '#/components/schemas/ScrapeJsonParams'
        maxAgeMs:
          type: integer
          minimum: 0
          maximum: 31536000000
          default: 259200000
          description: >-
            Maximum age of a cached output, in milliseconds. `0` fetches fresh.
            Defaults to 3 days (259200000 ms). Maximum: 1 year (31536000000 ms).
        zdr:
          type: string
          enum:
            - enabled
            - disabled
          default: disabled
          description: >-
            `enabled` turns on zero data retention. Your organization must have
            ZDR enabled.
        timeoutOpts:
          $ref: '#/components/schemas/ScrapeTimeout'
        tags:
          $ref: '#/components/schemas/RequestTags'
        policies:
          type: array
          items:
            type: string
          description: Access policy IDs to apply. A URL must pass every policy.
          example:
            - pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e
      required:
        - url
        - formats
      additionalProperties: false
      allOf:
        - if:
            required:
              - markdownParams
          then:
            properties:
              formats:
                required:
                  - markdown
                properties:
                  markdown:
                    const: true
        - if:
            required:
              - screenshotParams
          then:
            properties:
              formats:
                required:
                  - screenshot
                properties:
                  screenshot:
                    const: true
        - if:
            required:
              - imageParams
          then:
            properties:
              formats:
                required:
                  - images
                properties:
                  images:
                    const: true
        - if:
            required:
              - parseParams
          then:
            properties:
              formats:
                required:
                  - parse
                properties:
                  parse:
                    const: true
        - if:
            properties:
              formats:
                required:
                  - parse
                properties:
                  parse:
                    const: true
          then:
            required:
              - parseParams
        - if:
            required:
              - productParams
          then:
            properties:
              formats:
                required:
                  - product
                properties:
                  product:
                    const: true
        - if:
            required:
              - highlightsParams
          then:
            properties:
              formats:
                required:
                  - highlights
                properties:
                  highlights:
                    const: true
        - if:
            properties:
              formats:
                required:
                  - highlights
                properties:
                  highlights:
                    const: true
          then:
            required:
              - highlightsParams
        - if:
            required:
              - jsonParams
          then:
            properties:
              formats:
                required:
                  - json
                properties:
                  json:
                    const: true
        - if:
            properties:
              formats:
                required:
                  - json
                properties:
                  json:
                    const: true
          then:
            required:
              - jsonParams
    ScrapeResponse:
      type: object
      additionalProperties: false
      properties:
        url:
          type: string
          format: uri
          pattern: ^https?://
          description: Final URL after redirects and browser actions.
        html:
          type: object
          additionalProperties: false
          properties:
            error_code:
              type: string
              description: Why the output failed. Present only when `success` is `false`.
            message:
              type: string
              description: Explanation of the failure and possible next steps.
            requested:
              type: boolean
            success:
              type:
                - boolean
                - 'null'
              description: >-
                `true` if returned, `false` if it failed, `null` if not
                requested.
            data:
              type:
                - string
                - 'null'
          required:
            - requested
            - success
            - data
          allOf:
            - if:
                properties:
                  requested:
                    const: true
              then:
                properties:
                  success:
                    type: boolean
              else:
                properties:
                  success:
                    type: 'null'
          if:
            properties:
              success:
                const: true
          then:
            properties:
              data:
                type: string
          else:
            properties:
              data:
                type: 'null'
          description: Rendered HTML after content filters.
        markdown:
          type: object
          additionalProperties: false
          properties:
            error_code:
              type: string
              description: Why the output failed. Present only when `success` is `false`.
            message:
              type: string
              description: Explanation of the failure and possible next steps.
            requested:
              type: boolean
            success:
              type:
                - boolean
                - 'null'
              description: >-
                `true` if returned, `false` if it failed, `null` if not
                requested.
            data:
              type:
                - string
                - 'null'
          required:
            - requested
            - success
            - data
          allOf:
            - if:
                properties:
                  requested:
                    const: true
              then:
                properties:
                  success:
                    type: boolean
              else:
                properties:
                  success:
                    type: 'null'
          if:
            properties:
              success:
                const: true
          then:
            properties:
              data:
                type: string
          else:
            properties:
              data:
                type: 'null'
          description: Markdown after content filters.
        screenshot:
          type: object
          additionalProperties: false
          properties:
            error_code:
              type: string
              description: Why the output failed. Present only when `success` is `false`.
            message:
              type: string
              description: Explanation of the failure and possible next steps.
            requested:
              type: boolean
            success:
              type:
                - boolean
                - 'null'
              description: >-
                `true` if returned, `false` if it failed, `null` if not
                requested.
            data:
              type:
                - string
                - 'null'
              format: uri
              pattern: ^data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/]+={0,2}$
          required:
            - requested
            - success
            - data
          allOf:
            - if:
                properties:
                  requested:
                    const: true
              then:
                properties:
                  success:
                    type: boolean
              else:
                properties:
                  success:
                    type: 'null'
          if:
            properties:
              success:
                const: true
          then:
            properties:
              data:
                type: string
                format: uri
                pattern: ^data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/]+={0,2}$
          else:
            properties:
              data:
                type: 'null'
          description: Screenshot as a base64 image data URL.
        images:
          type: object
          additionalProperties: false
          properties:
            error_code:
              type: string
              description: Why the output failed. Present only when `success` is `false`.
            message:
              type: string
              description: Explanation of the failure and possible next steps.
            requested:
              type: boolean
            success:
              type:
                - boolean
                - 'null'
              description: >-
                `true` if returned, `false` if it failed, `null` if not
                requested.
            data:
              type:
                - array
                - 'null'
              items:
                $ref: '#/components/schemas/ScrapeImage'
          required:
            - requested
            - success
            - data
          allOf:
            - if:
                properties:
                  requested:
                    const: true
              then:
                properties:
                  success:
                    type: boolean
              else:
                properties:
                  success:
                    type: 'null'
          if:
            properties:
              success:
                const: true
          then:
            properties:
              data:
                type: array
                items:
                  $ref: '#/components/schemas/ScrapeImage'
          else:
            properties:
              data:
                type: 'null'
          description: Images after content filters. `[]` when none are found.
        bytes:
          type: object
          additionalProperties: false
          properties:
            error_code:
              type: string
              description: Why the output failed. Present only when `success` is `false`.
            message:
              type: string
              description: Explanation of the failure and possible next steps.
            requested:
              type: boolean
            success:
              type:
                - boolean
                - 'null'
              description: >-
                `true` if returned, `false` if it failed, `null` if not
                requested.
            data:
              type:
                - object
                - 'null'
              additionalProperties: false
              properties:
                contentType:
                  type: string
                  examples:
                    - text/html; charset=utf-8
                base64:
                  type: string
                  contentEncoding: base64
                  pattern: >-
                    ^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$
                  description: >-
                    Body as base64, after HTTP decompression. Up to 50 MiB
                    decoded.
              required:
                - contentType
                - base64
          required:
            - requested
            - success
            - data
          allOf:
            - if:
                properties:
                  requested:
                    const: true
              then:
                properties:
                  success:
                    type: boolean
              else:
                properties:
                  success:
                    type: 'null'
          if:
            properties:
              success:
                const: true
          then:
            properties:
              data:
                type: object
                additionalProperties: false
                properties:
                  contentType:
                    type: string
                    examples:
                      - text/html; charset=utf-8
                  base64:
                    type: string
                    contentEncoding: base64
                    pattern: >-
                      ^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$
                    description: >-
                      Body as base64, after HTTP decompression. Up to 50 MiB
                      decoded.
                required:
                  - contentType
                  - base64
          else:
            properties:
              data:
                type: 'null'
          description: >-
            The original HTTP response body, unchanged by waits, actions, and
            filters.
        parsed:
          type: object
          additionalProperties: false
          properties:
            error_code:
              type: string
              description: Why the output failed. Present only when `success` is `false`.
            message:
              type: string
              description: Explanation of the failure and possible next steps.
            type:
              type: string
              enum:
                - custom
                - google-maps
                - google-maps-reviews
                - google-play
                - google-play-reviews
                - app-store
                - app-store-reviews
                - g2-reviews
                - instagram-profile
                - instagram-post
                - instagram-feed
                - tiktok-profile
                - tiktok-video
                - tiktok-feed
                - tiktok-comments
                - tiktok-followers
                - tiktok-following
                - tiktok-user-search
                - reddit-post
                - reddit-search
                - reddit-subreddit
                - reddit-user
                - yelp-search
                - yelp-reviews
                - tripadvisor-reviews
                - emails
                - phone-numbers
                - links
              description: >-
                The selected prebuilt parser name, or custom when type is
                omitted, custom rules are used, or parsing is not requested.
            requested:
              type: boolean
            success:
              type:
                - boolean
                - 'null'
              description: >-
                `true` if returned, `false` if it failed, `null` if not
                requested.
            data:
              type:
                - object
                - 'null'
              additionalProperties: true
          required:
            - requested
            - success
            - data
            - type
          allOf:
            - if:
                properties:
                  requested:
                    const: true
              then:
                properties:
                  success:
                    type: boolean
              else:
                properties:
                  success:
                    type: 'null'
          if:
            properties:
              success:
                const: true
          then:
            properties:
              data:
                type: object
                additionalProperties: true
          else:
            properties:
              data:
                type: 'null'
          description: >-
            Custom rules return fields after content filters; unmatched fields
            are null ([] for lists). Prebuilt parsers return source-specific
            structured data. See
            https://docs.context.dev/scrape/prebuilt-parsers for output schemas
            and request options.
        highlights:
          type: object
          additionalProperties: false
          properties:
            error_code:
              type: string
              description: Why the output failed. Present only when `success` is `false`.
            message:
              type: string
              description: Explanation of the failure and possible next steps.
            requested:
              type: boolean
            success:
              type:
                - boolean
                - 'null'
              description: >-
                `true` if returned, `false` if it failed, `null` if not
                requested.
            data:
              type:
                - array
                - 'null'
              items:
                type: string
          required:
            - requested
            - success
            - data
          allOf:
            - if:
                properties:
                  requested:
                    const: true
              then:
                properties:
                  success:
                    type: boolean
              else:
                properties:
                  success:
                    type: 'null'
          if:
            properties:
              success:
                const: true
          then:
            properties:
              data:
                type: array
                items:
                  type: string
          else:
            properties:
              data:
                type: 'null'
          description: >-
            Relevant Markdown excerpts in page order. `[Heading]` adds context;
            `…` marks omitted text.
        json:
          type: object
          additionalProperties: false
          properties:
            error_code:
              type: string
              description: Why the output failed. Present only when `success` is `false`.
            message:
              type: string
              description: Explanation of the failure and possible next steps.
            requested:
              type: boolean
            success:
              type:
                - boolean
                - 'null'
              description: >-
                `true` if returned, `false` if it failed, `null` if not
                requested.
            data:
              type:
                - object
                - 'null'
              additionalProperties: true
            isTruncated:
              type: boolean
              const: true
              description: >-
                True when the page was too long to read in full, so values found
                only in the unread parts may be missing.
          required:
            - requested
            - success
            - data
          allOf:
            - if:
                properties:
                  requested:
                    const: true
              then:
                properties:
                  success:
                    type: boolean
              else:
                properties:
                  success:
                    type: 'null'
          if:
            properties:
              success:
                const: true
          then:
            properties:
              data:
                type: object
                additionalProperties: true
          else:
            properties:
              data:
                type: 'null'
          description: Object matching `jsonParams.schema`.
        product:
          type: object
          additionalProperties: false
          properties:
            error_code:
              type: string
              description: Why the output failed. Present only when `success` is `false`.
            message:
              type: string
              description: Explanation of the failure and possible next steps.
            requested:
              type: boolean
            success:
              type:
                - boolean
                - 'null'
              description: >-
                `true` if returned, `false` if it failed, `null` if not
                requested.
            data:
              oneOf:
                - $ref: '#/components/schemas/ScrapeProductResult'
                - type: 'null'
          required:
            - requested
            - success
            - data
          allOf:
            - if:
                properties:
                  requested:
                    const: true
              then:
                properties:
                  success:
                    type: boolean
              else:
                properties:
                  success:
                    type: 'null'
          if:
            properties:
              success:
                const: true
          then:
            properties:
              data:
                $ref: '#/components/schemas/ScrapeProductResult'
          else:
            properties:
              data:
                type: 'null'
          description: Product details found on the page.
        profile:
          type:
            - object
            - 'null'
          additionalProperties: false
          properties:
            id:
              type: string
              pattern: ^prof_[a-f0-9]{32}$
              description: >-
                Save this ID after creating a profile, then reuse it as
                sharedParams.profile.profileId with type "existing".
          required:
            - id
          description: >-
            Authenticated browser profile used for this scrape, or null when no
            profile was requested. New and existing profile requests both return
            the profile ID.
        isPartial:
          type: boolean
          const: true
          description: >-
            True when at least one requested output succeeds but the response
            has failed or incomplete outputs. Absent when all requested outputs
            fail.
        metadata:
          $ref: '#/components/schemas/ScrapeMetadata'
          description: Page metadata. Fields are omitted when not found.
        cache_metadata:
          $ref: '#/components/schemas/CacheMetadata'
        key_metadata:
          $ref: '#/components/schemas/KeyMetadata'
        request_id:
          $ref: '#/components/schemas/RequestId'
      required:
        - url
        - html
        - markdown
        - screenshot
        - images
        - bytes
        - parsed
        - highlights
        - json
        - product
        - profile
        - metadata
        - cache_metadata
        - request_id
      not:
        properties:
          html:
            properties:
              requested:
                const: false
          markdown:
            properties:
              requested:
                const: false
          screenshot:
            properties:
              requested:
                const: false
          images:
            properties:
              requested:
                const: false
          bytes:
            properties:
              requested:
                const: false
          parsed:
            properties:
              requested:
                const: false
          highlights:
            properties:
              requested:
                const: false
          json:
            properties:
              requested:
                const: false
          product:
            properties:
              requested:
                const: false
    ErrorResponse:
      type: object
      properties:
        message:
          type: string
          description: Human-readable error message.
        error_code:
          type: string
          enum:
            - PROFILE_NOT_FOUND
            - PROFILE_BUSY
            - PROFILE_SESSION_EXPIRED
            - PROFILE_REAUTHENTICATION_REQUIRED
            - PROFILE_INVALID_CREDENTIALS
            - PROFILE_MISSING_CREDENTIALS
            - PROFILE_INTERACTION_REQUIRED
            - PROFILE_AUTHENTICATION_UNKNOWN
            - PROFILE_ORIGIN_BLOCKED
            - PROFILE_INVALID_SESSION
            - PROFILE_SESSION_TOO_LARGE
            - INTERNAL_ERROR
            - VALID
            - NOT_FOUND
            - FORBIDDEN
            - ACCESS_POLICY_DENIED
            - ACCESS_POLICIES_NOT_ENABLED
            - USAGE_EXCEEDED
            - RATE_LIMITED
            - UNAUTHORIZED
            - DISABLED
            - PAID_PLAN_REQUIRED
            - INSUFFICIENT_PERMISSIONS
            - TIMEOUT_EXCEEDS_MAXIMUM
            - TIMEOUT_TOO_SHORT_FOR_WAIT
            - WEBSITE_ACCESS_ERROR
            - WEBSITE_BLOCKED
            - WEBSITE_NOT_FOUND
            - PDF_SKIPPED
            - PDF_IMAGES_ONLY
            - NO_PUBLISHED_MARKDOWN
            - INPUT_VALIDATION_ERROR
            - ZDR_NOT_SUPPORTED
            - ZDR_NOT_ENABLED
            - FREE_EMAIL_DETECTED
            - DISPOSABLE_EMAIL_DETECTED
            - REQUEST_TIMEOUT
            - COLD_DOMAIN_TIMEOUT_TOO_LOW
            - UNSUPPORTED_CONTENT
            - CONTENT_TOO_LARGE
            - MONITOR_PAUSED
            - MONITOR_NO_WEBHOOK
            - COLLECTION_PAUSED
            - MONITOR_LIMIT_EXCEEDED
            - SEARCH_UNAVAILABLE
            - BATCH_LIMIT_EXCEEDED
            - BATCH_NOT_CANCELLABLE
            - BATCH_NOT_COMPLETED
            - IDEMPOTENCY_KEY_CONFLICT
            - DELIVERY_IN_PROGRESS
            - DELIVERY_ALREADY_DELIVERED
            - DELIVERY_EXPIRED
            - DELIVERY_CANCELLED
          description: Machine-readable error code.
        error_data:
          anyOf:
            - $ref: '#/components/schemas/BillingErrorData'
            - $ref: '#/components/schemas/ConcurrencyErrorData'
            - $ref: '#/components/schemas/AccessPolicyErrorData'
        required_permission:
          type: string
          enum:
            - logs:read
            - data:execute
            - monitors:read
            - monitors:write
            - batches:read
            - batches:write
            - access_policies:read
            - access_policies:write
          description: >-
            Permission required for this request when error_code is
            INSUFFICIENT_PERMISSIONS. Manage (write) also grants read access to
            the same resource group.
        key_metadata:
          $ref: '#/components/schemas/KeyMetadata'
        request_id:
          $ref: '#/components/schemas/RequestId'
      required:
        - request_id
    ScrapeFormats:
      type: object
      properties:
        html:
          type: boolean
          default: false
          description: Rendered HTML.
        markdown:
          type: boolean
          default: false
          description: Page content as Markdown.
        screenshot:
          type: boolean
          default: false
          description: A screenshot of the page.
        images:
          type: boolean
          default: false
          description: Images found on the page.
        bytes:
          type: boolean
          default: false
          description: The original HTTP response body.
        parse:
          type: boolean
          default: false
          description: >-
            Fields extracted with custom rules or a prebuilt parser, returned as
            `parsed`.
        product:
          type: boolean
          default: false
          description: Product details such as name, price, and availability.
        highlights:
          type: boolean
          default: false
          description: Markdown excerpts relevant to `highlightsParams.query`.
        json:
          type: boolean
          default: false
          description: >-
            An object matching `jsonParams.schema`, extracted from the page text
            and its embedded data (JSON-LD, meta tags, framework state).
      additionalProperties: false
      description: Outputs to return. Set at least one to `true`.
      not:
        allOf:
          - not:
              required:
                - html
              properties:
                html:
                  const: true
          - not:
              required:
                - markdown
              properties:
                markdown:
                  const: true
          - not:
              required:
                - screenshot
              properties:
                screenshot:
                  const: true
          - not:
              required:
                - images
              properties:
                images:
                  const: true
          - not:
              required:
                - bytes
              properties:
                bytes:
                  const: true
          - not:
              required:
                - parse
              properties:
                parse:
                  const: true
          - not:
              required:
                - product
              properties:
                product:
                  const: true
          - not:
              required:
                - highlights
              properties:
                highlights:
                  const: true
          - not:
              required:
                - json
              properties:
                json:
                  const: true
    ScrapeSharedParams:
      type: object
      properties:
        profile:
          $ref: '#/components/schemas/ScrapeProfile'
          description: >-
            Create or reuse an authenticated browser profile. Requires a paid
            plan and an HTTPS target. Profiles persist session state, bypass
            shared caches, and cannot be combined with ZDR, custom headers, or
            raw bytes. Of the prebuilt parsers, only emails, phone-numbers, and
            links support profiles.
        country:
          type: string
          description: Proxy country as a two-letter code, such as `US`. Case-insensitive.
          pattern: ^[A-Za-z]{2}$
          examples:
            - US
        headers:
          type: object
          additionalProperties:
            type: string
            maxLength: 8192
            pattern: ^[^\r\n]*$
          examples:
            - Accept-Language: en-US
          propertyNames:
            pattern: ^[!#$%&'*+.^_`|~0-9A-Za-z-]+$
            not:
              pattern: >-
                ^(?:[Hh][Oo][Ss][Tt]|[Cc][Oo][Nn][Tt][Ee][Nn][Tt]-[Ll][Ee][Nn][Gg][Tt][Hh]|[Cc][Oo][Nn][Nn][Ee][Cc][Tt][Ii][Oo][Nn]|[Kk][Ee][Ee][Pp]-[Aa][Ll][Ii][Vv][Ee]|[Tt][Rr][Aa][Nn][Ss][Ff][Ee][Rr]-[Ee][Nn][Cc][Oo][Dd][Ii][Nn][Gg]|[Uu][Pp][Gg][Rr][Aa][Dd][Ee]|[Pp][Rr][Oo][Xx][Yy]-[Aa][Uu][Tt][Hh][Ee][Nn][Tt][Ii][Cc][Aa][Tt][Ee]|[Pp][Rr][Oo][Xx][Yy]-[Aa][Uu][Tt][Hh][Oo][Rr][Ii][Zz][Aa][Tt][Ii][Oo][Nn]|[Pp][Rr][Oo][Xx][Yy]-[Cc][Oo][Nn][Nn][Ee][Cc][Tt][Ii][Oo][Nn]|[Tt][Ee]|[Tt][Rr][Aa][Ii][Ll][Ee][Rr]|[Ee][Xx][Pp][Ee][Cc][Tt])$
          description: >-
            HTTP headers to send to the target site. Requests with headers skip
            the cache.
        viewport:
          type: object
          properties:
            width:
              type: integer
              minimum: 240
              maximum: 7680
              default: 1440
              description: Browser viewport width in pixels.
            height:
              type: integer
              minimum: 240
              maximum: 4320
              default: 900
              description: Browser viewport height in pixels.
          additionalProperties: false
          description: >-
            Browser size in pixels. Omit for 1920 × 1080. When provided, missing
            dimensions default to 1440 × 900.
        theme:
          type: string
          enum:
            - light
            - dark
          description: Emulate a light or dark color scheme.
        dismissCookies:
          type: boolean
          default: true
          description: Accept cookie banners before actions and capture.
        dismissPopups:
          type: boolean
          default: false
          description: Close other popups before actions and capture.
        actions:
          type: array
          items:
            $ref: '#/components/schemas/ScrapeAction'
          minItems: 1
          maxItems: 5
          description: >-
            Browser steps run in order before capture. Requires a paid plan.
            Skips the cache.
        waitFor:
          anyOf:
            - type: integer
              minimum: 0
              maximum: 30000
            - type: string
              minLength: 1
              maxLength: 2048
              pattern: \S
          description: >-
            Milliseconds, or a CSS selector to wait for, after actions. Defaults
            to 500 (2000 with frames or XML).
          examples:
            - 500
            - '#content'
        settleAnimations:
          type: boolean
          description: >-
            Wait for CSS animations to finish before capture. Defaults to `true`
            when `screenshot` is requested.
        mainContentOnly:
          type: boolean
          default: false
          description: >-
            Keep only the main content. Doesn't affect `screenshot`, `bytes`, or
            `product`.
        includeSelectors:
          type: array
          items:
            type: string
            minLength: 1
            maxLength: 2048
            pattern: \S
          minItems: 1
          maxItems: 50
          uniqueItems: true
          description: Keep only elements matching these CSS selectors.
        excludeSelectors:
          type: array
          items:
            type: string
            minLength: 1
            maxLength: 2048
            pattern: \S
          minItems: 1
          maxItems: 50
          uniqueItems: true
          description: >-
            Remove elements matching these CSS selectors. Overrides
            `includeSelectors`.
        includeFrames:
          type: boolean
          default: false
          description: >-
            Include iframe content in HTML and text outputs. Screenshots always
            show visible frames.
        parsers:
          type: object
          properties:
            pdf:
              $ref: '#/components/schemas/ScrapePdfOptions'
          additionalProperties: false
          description: Document parsing options.
      additionalProperties: false
      description: Browser and content settings shared by all outputs.
    ScrapeMarkdownParams:
      type: object
      properties:
        includeLinks:
          type: boolean
          default: true
          description: Keep link URLs in the Markdown (`html-conversion` only).
        includeImages:
          type: boolean
          default: false
          description: Include images in the Markdown (`html-conversion` only).
        inlineImages:
          type: string
          enum:
            - placeholder
            - preserve
          default: placeholder
          description: >-
            How base64 images appear when `includeImages` is set
            (`html-conversion` only).
        sourcePreference:
          type: array
          items:
            type: string
            enum:
              - html-conversion
              - markdown-direct
          minItems: 1
          default:
            - html-conversion
            - markdown-direct
          uniqueItems: true
          description: >-
            Markdown sources in order of preference: `html-conversion` converts
            the page HTML, `markdown-direct` uses Markdown the site publishes.
      additionalProperties: false
      description: Markdown options. Requires `formats.markdown`.
    ScrapeScreenshotParams:
      type: object
      properties:
        area:
          anyOf:
            - type: string
              enum:
                - viewport
                - fullPage
              x-stainless-variantName: Page
            - type: object
              properties:
                selector:
                  type: string
                  minLength: 1
                  maxLength: 2048
                  pattern: \S
                  description: CSS selector matching exactly one visible element.
              required:
                - selector
              additionalProperties: false
              x-stainless-variantName: Element
            - type: object
              properties:
                x:
                  type: integer
                  minimum: 0
                  maximum: 100000
                  description: >-
                    Left edge of the capture, in pixels from the document
                    origin.
                'y':
                  type: integer
                  minimum: 0
                  maximum: 100000
                  description: Top edge of the capture, in pixels from the document origin.
                width:
                  type: integer
                  minimum: 1
                  maximum: 7680
                  description: Width of the capture in pixels.
                height:
                  type: integer
                  minimum: 1
                  maximum: 100000
                  description: Height of the capture in pixels.
              required:
                - x
                - 'y'
                - width
                - height
              additionalProperties: false
              x-stainless-variantName: Rectangle
              description: Pixels from the document origin.
          default: viewport
          description: >-
            What to capture: `viewport`, `fullPage`, one element, or a
            rectangle. Max 40 megapixels.
        format:
          type: string
          enum:
            - png
            - jpeg
            - webp
          default: png
          description: Image format for the screenshot.
      additionalProperties: false
      description: 'Screenshot options. Requires formats.screenshot: true.'
    ScrapeImageParams:
      type: object
      properties:
        enrich:
          type: array
          items:
            type: string
            enum:
              - dimensions
              - classification
              - file
          maxItems: 3
          uniqueItems: true
          description: >-
            Extra data per image: `dimensions`, `classification`, or a hosted
            `file` URL.
        dedupe:
          type: string
          enum:
            - none
            - visual
          default: none
          description: Set `visual` to drop visual duplicates, keeping the largest copy.
      additionalProperties: false
      description: 'Image options. Requires formats.images: true.'
    ScrapeParseParams:
      oneOf:
        - type: object
          properties:
            type:
              type: string
              enum:
                - custom
              default: custom
              const: custom
              description: >-
                Extract fields using custom CSS rules. This is the default when
                type is omitted.
            rules:
              $ref: '#/components/schemas/ScrapeParseRules'
          required:
            - rules
          additionalProperties: false
          x-stainless-variantName: CustomParser
        - type: object
          properties:
            type:
              type: string
              enum:
                - prebuilt
              const: prebuilt
              description: Use a prebuilt parser instead of custom rules.
            parser:
              type: string
              enum:
                - google-maps
                - google-maps-reviews
                - google-play
                - google-play-reviews
                - app-store
                - app-store-reviews
                - g2-reviews
                - instagram-profile
                - instagram-post
                - instagram-feed
                - tiktok-profile
                - tiktok-video
                - tiktok-feed
                - tiktok-comments
                - tiktok-followers
                - tiktok-following
                - tiktok-user-search
                - reddit-post
                - reddit-search
                - reddit-subreddit
                - reddit-user
                - yelp-search
                - yelp-reviews
                - tripadvisor-reviews
                - emails
                - phone-numbers
                - links
              description: >-
                The prebuilt parser to use. See
                https://docs.context.dev/scrape/prebuilt-parsers for supported
                sources, request options, and output schemas.
            sort:
              type: string
              enum:
                - newest
                - oldest
                - relevant
                - highest
                - lowest
              default: newest
              description: >-
                google-maps-reviews only. Order of data.reviews. newest,
                relevant, highest, and lowest follow Google; oldest returns the
                earliest reviews first, which Google itself does not offer.
            limit:
              type: integer
              minimum: 1
              maximum: 1000
              default: 100
              description: >-
                google-maps-reviews and reddit parsers only. Maximum number of
                reviews (google-maps-reviews, default 100), comments
                (reddit-post, default 100), or results (reddit-search,
                reddit-subreddit, and reddit-user, default 100) to return;
                maximum 1000.
          required:
            - type
            - parser
          additionalProperties: false
          x-stainless-variantName: PrebuiltParser
      description: 'Requires `formats.parse: true`; required when it is set.'
    ScrapeProductParams:
      type: object
      properties:
        dedupeImages:
          type: boolean
          default: false
          description: Drop visually duplicate product images, keeping the largest copy.
        useAIFallback:
          type: boolean
          deprecated: true
          description: Ignored. The AI fallback runs automatically.
      additionalProperties: false
      description: 'Product options. Requires formats.product: true.'
    ScrapeHighlightsParams:
      type: object
      properties:
        query:
          type: string
          minLength: 1
          maxLength: 2000
          description: The question or topic to find passages for.
        maxCharacters:
          type: integer
          minimum: 100
          maximum: 20000
          default: 4000
          description: Maximum combined length of returned passages.
      required:
        - query
      additionalProperties: false
      description: 'Requires `formats.highlights: true`; required when it is set.'
    ScrapeJsonParams:
      type: object
      properties:
        schema:
          type: object
          additionalProperties: true
          description: >-
            JSON Schema (not an example object) for a top-level object, up to 50
            KB. Use optional or nullable fields for missing facts.
          example:
            type: object
            properties:
              name:
                type: string
                description: Product name.
              price:
                type: number
                description: Current price as a plain number.
              inStock:
                type: boolean
            required:
              - name
            additionalProperties: false
        instructions:
          type: string
          maxLength: 2000
          description: >-
            Extra guidance, such as which facts to prefer or how to read a
            field.
      required:
        - schema
      additionalProperties: false
      description: 'Requires `formats.json: true`; required when it is set.'
    ScrapeTimeout:
      type: object
      properties:
        milliseconds:
          type: integer
          minimum: 1
          maximum: 300000
          description: Deadline in milliseconds.
        behavior:
          type: string
          enum:
            - fail
            - return-partial
          default: fail
          description: >-
            "fail" returns 408 at the deadline. "return-partial" returns
            available results; inspect the response’s partial flag.
            "return-partial" requires at least 5000 ms.
      required:
        - milliseconds
      additionalProperties: false
      description: Request deadline and what to return when it passes.
    RequestTags:
      type: array
      items:
        type: string
        minLength: 1
        maxLength: 50
      maxItems: 20
      description: Labels for filtering usage in the dashboard.
      example:
        - production
        - team-alpha
    ScrapeImage:
      type: object
      additionalProperties: false
      properties:
        url:
          type: string
          format: uri
          pattern: ^(https?://|data:image/)
          description: Image URL, or a data URI for inline images.
        alt:
          type:
            - string
            - 'null'
          description: Alt text, if present.
        width:
          type: integer
          minimum: 1
        height:
          type: integer
          minimum: 1
        classification:
          type: string
          enum:
            - photography
            - illustration
            - logo
            - wordmark
            - icon
            - pattern
            - graphic
            - other
        fileUrl:
          type: string
          format: uri
          pattern: ^https?://
          description: >-
            Hosted image URL, valid for 24 hours after capture. Requires `file`
            enrichment and ZDR disabled.
      required:
        - url
        - alt
    ScrapeProductResult:
      type: object
      additionalProperties: false
      properties:
        isProductPage:
          type: boolean
          description: Whether the page is a product detail page.
        product:
          oneOf:
            - $ref: '#/components/schemas/ScrapeProduct'
            - type: 'null'
          description: >-
            The extracted product, or null when the page is not a product detail
            page.
      required:
        - isProductPage
        - product
    ScrapeMetadata:
      type: object
      additionalProperties: false
      properties:
        title:
          type: string
          description: Best title extracted from the page.
        description:
          type: string
          description: >-
            Best description extracted from standard, Open Graph, or Twitter
            metadata.
        language:
          type: string
          description: Language extracted from html lang or language meta tags.
        keywords:
          type: array
          items:
            type: string
          description: Keywords extracted from the page's keywords meta tag.
        canonicalUrl:
          type: string
          description: Resolved canonical URL, when present.
        author:
          type: string
          description: Author metadata, when present.
        siteName:
          type: string
          description: Site or application name from page metadata.
        image:
          type: string
          description: >-
            Primary resolved preview image from Open Graph, Twitter, or image
            metadata.
        favicon:
          type: string
          description: Resolved favicon URL, when present.
        publishedTime:
          type: string
          description: Published timestamp/date from page metadata, when present.
        modifiedTime:
          type: string
          description: Modified timestamp/date from page metadata, when present.
        robots:
          type: string
          description: Robots meta directive, when present.
        openGraph:
          type: object
          additionalProperties:
            $ref: '#/components/schemas/PageMetadataValue'
          description: >-
            Open Graph metadata with the og: prefix removed and keys
            camel-cased.
        twitter:
          type: object
          additionalProperties:
            $ref: '#/components/schemas/PageMetadataValue'
          description: >-
            Twitter card metadata with the twitter: prefix removed and keys
            camel-cased.
        alternates:
          type: array
          items:
            $ref: '#/components/schemas/PageMetadataAlternate'
          description: Resolved alternate links from link rel=alternate tags.
        headings:
          type: array
          items:
            $ref: '#/components/schemas/PageMetadataHeading'
          description: >-
            Up to 500 h1–h6 headings in document order, before content
            filtering.
        jsonLd:
          type: array
          items:
            type: object
            additionalProperties: true
          description: JSON-LD structured data blocks parsed from the page.
        additionalMeta:
          type: object
          additionalProperties:
            $ref: '#/components/schemas/PageMetadataValue'
          description: >-
            Additional non-social meta tags not promoted to top-level metadata
            fields.
    CacheMetadata:
      type: object
      properties:
        status:
          type: string
          enum:
            - hit
            - miss
            - zdr
          description: >-
            Whether the response was served from cache, required fresh work, or
            honored zero-data-retention cache bypass.
        age_ms:
          type: integer
          minimum: 0
          description: >-
            Age of the cached data in milliseconds. Zero for miss and zdr
            responses.
      required:
        - status
        - age_ms
      additionalProperties: false
      description: Whether this response came from cache.
    KeyMetadata:
      type: object
      properties:
        credits_consumed:
          type: integer
          description: Credits charged for this request.
        credits_remaining:
          type: integer
          description: Credits remaining for your organization.
      required:
        - credits_consumed
        - credits_remaining
      description: Credits this request used and your remaining balance.
    RequestId:
      type: string
      format: uuid
      description: >-
        Unique ID of this request, also in `X-Request-Id`. Include it when
        contacting support.
      example: 3f1c2a6e-8b4d-4c1e-9f0a-2d7b5e6c8a91
    BillingErrorData:
      type: object
      properties:
        is_authenticated:
          type: boolean
          enum:
            - true
        credits_remaining:
          type: number
          minimum: 0
        credits_required:
          type: number
          minimum: 0
        is_credits_required_estimated:
          type: boolean
        credits_charged:
          type: number
          minimum: 0
        should_retry:
          type: boolean
          enum:
            - false
        retry_condition:
          type: string
          enum:
            - sufficient_credits
        next_refill_at:
          type: string
          format: date-time
        next_refill_credits:
          type: number
          exclusiveMinimum: 0
        info_url:
          type: string
          enum:
            - https://context.dev/dashboard/subscription
      required:
        - is_authenticated
        - should_retry
        - retry_condition
        - info_url
      description: >-
        Credit admission or reservation failure details. credits_required is an
        admission estimate, not a final charge. should_retry is false for an
        unchanged request immediately; retry_condition requires sufficient
        account credits. Unknown balances, costs, and refill details are
        omitted. next_refill_at is an ISO 8601 UTC timestamp. Existing
        request_id and key_metadata remain on the error envelope.
    ConcurrencyErrorData:
      type: object
      properties:
        is_authenticated:
          type: boolean
          enum:
            - true
        limit_type:
          type: string
          enum:
            - concurrency
        limit:
          type: number
          minimum: 0
        remaining:
          type: number
          minimum: 0
        retry_after_seconds:
          type: number
          minimum: 0
        credits_remaining:
          type: number
          minimum: 0
        credits_charged:
          type: number
          enum:
            - 0
        should_retry:
          type: boolean
          enum:
            - false
        retry_condition:
          type: string
          enum:
            - available_concurrency
        recovery_options:
          type: array
          items:
            type: string
            enum:
              - wait_for_in_flight_requests
              - increase_concurrency_limit
        info_url:
          type: string
          enum:
            - https://context.dev/dashboard/subscription
      required:
        - is_authenticated
        - limit_type
        - limit
        - remaining
        - retry_after_seconds
        - credits_charged
        - should_retry
        - retry_condition
        - recovery_options
        - info_url
      description: >-
        Organization concurrency rejection details. Authentication is valid and
        no credits were charged. should_retry is false immediately; respect
        retry_after_seconds and wait for an in-flight request to finish or for
        the effective concurrency limit to increase. info_url opens subscription
        settings; no higher allowance is guaranteed for a particular account.
    AccessPolicyErrorData:
      type: object
      properties:
        url:
          type: string
          description: The URL that was blocked.
        denied_by:
          type: array
          items:
            type: string
          description: IDs of the access policies that blocked it.
      required:
        - url
        - denied_by
      description: Sent with `ACCESS_POLICY_DENIED`.
    ScrapeProfile:
      oneOf:
        - type: object
          properties:
            type:
              type: string
              enum:
                - existing
              const: existing
              description: Reuse a saved browser profile.
            profileId:
              type: string
              pattern: ^prof_[a-f0-9]{32}$
              description: The ID returned in profile.id by an earlier scrape.
          required:
            - type
            - profileId
          additionalProperties: false
          x-stainless-variantName: Existing
        - type: object
          properties:
            type:
              type: string
              enum:
                - new
              const: new
              description: Sign in and create a browser profile.
            identifier:
              type: string
              minLength: 1
              maxLength: 1024
              description: Username or email for the target website.
            password:
              type: string
              minLength: 1
              maxLength: 4096
              description: Password used to sign in. It is never stored in the profile.
              writeOnly: true
            description:
              type: string
              minLength: 1
              maxLength: 500
              description: >-
                Optional label shown when listing profiles with `GET
                /org/browser/profiles`.
          required:
            - type
            - identifier
            - password
          additionalProperties: false
          x-stainless-variantName: New
      discriminator:
        propertyName: type
      description: >-
        Create or reuse an authenticated browser profile. Requires a paid plan
        and an HTTPS target. Profiles persist session state, bypass shared
        caches, and cannot be combined with ZDR, custom headers, raw bytes, or
        prebuilt parsers.
    ScrapeAction:
      oneOf:
        - type: object
          properties:
            type:
              type: string
              enum:
                - perform
              description: Use `perform` for a plain-language browser instruction.
            action:
              type: string
              minLength: 1
              maxLength: 500
              description: >-
                One browser instruction, such as clicking a button or entering
                text.
              examples:
                - Click the product details tab
          required:
            - type
            - action
          additionalProperties: false
          x-stainless-variantName: Perform
        - type: object
          properties:
            type:
              type: string
              enum:
                - scroll
              description: Use `scroll` to move through the page or a container.
            direction:
              type: string
              enum:
                - down
                - up
                - left
                - right
              default: down
              description: Direction to scroll.
            amount:
              anyOf:
                - type: integer
                  minimum: 1
                  maximum: 100000
                - type: string
                  enum:
                    - viewport
                    - max
              default: viewport
              description: >-
                Distance per scroll: pixels, one `viewport`, or `max` to reach
                the end.
            selector:
              type: string
              minLength: 1
              maxLength: 2000
              pattern: \S
              description: Scroll this container. Omit to scroll the page.
            maxScrolls:
              type: integer
              minimum: 1
              maximum: 50
              default: 1
              description: Maximum number of scroll steps for this action.
          required:
            - type
          additionalProperties: false
          x-stainless-variantName: Scroll
        - type: object
          properties:
            type:
              type: string
              enum:
                - wait
              description: Use `wait` to pause for a fixed duration.
            milliseconds:
              type: integer
              minimum: 0
              maximum: 30000
              description: Time to pause in milliseconds before the next action.
          required:
            - type
            - milliseconds
          additionalProperties: false
          x-stainless-variantName: Wait
        - type: object
          properties:
            type:
              type: string
              enum:
                - waitFor
              description: Use `waitFor` to wait for a matching element.
            selector:
              type: string
              minLength: 1
              maxLength: 2048
              pattern: \S
              description: CSS selector to wait for before continuing.
          required:
            - type
            - selector
          additionalProperties: false
          x-stainless-variantName: WaitFor
      discriminator:
        propertyName: type
      title: Browser action
    ScrapePdfOptions:
      type: object
      properties:
        startPage:
          type: integer
          minimum: 1
          description: First page to parse, starting at 1.
        endPage:
          type: integer
          minimum: 1
          description: Last page to parse. Must be at least `startPage`.
        ocr:
          type: string
          enum:
            - 'off'
            - auto
          default: 'off'
          description: Set `auto` to read scanned pages with OCR.
        includeNumberedPages:
          type: boolean
          default: false
          description: >-
            Start each page in the Markdown with a `<!-- page N -->` line using
            its original 1-based page number; these responses are never served
            from cache.
      additionalProperties: false
      description: PDF page range and OCR.
    ScrapeParseRules:
      type: object
      additionalProperties:
        anyOf:
          - type: string
            minLength: 1
            maxLength: 2048
          - type: object
            properties:
              selector:
                type: string
                minLength: 1
                maxLength: 2048
                description: CSS selector to match within the current page or parent rule.
              type:
                type: string
                enum:
                  - item
                  - list
                description: Return the first match with `item` or all matches with `list`.
              output:
                description: >-
                  Return text, HTML, an attribute such as `@href`, or nested
                  field rules. Defaults to text.
                anyOf:
                  - type: string
                    enum:
                      - text
                      - html
                  - type: string
                    pattern: ^@.*$
                  - $ref: '#/components/schemas/ScrapeParseRules'
            required:
              - selector
            additionalProperties: false
      description: >-
        Field names mapped to CSS selectors (`h1`, `a@href`) or rule objects.
        Max 100 fields, 5 levels.
      minProperties: 1
      examples:
        - title: h1
          links:
            selector: a
            type: list
            output: '@href'
    ScrapeProduct:
      type: object
      additionalProperties: false
      properties:
        name:
          type: string
          description: Product name.
        description:
          type:
            - string
            - 'null'
          description: Product description.
        brand:
          type:
            - string
            - 'null'
          description: Brand or vendor.
        sku:
          type:
            - string
            - 'null'
          description: Product identifier such as a SKU or model number.
        price:
          type:
            - number
            - 'null'
          description: Current price.
        regularPrice:
          type:
            - number
            - 'null'
          description: List price before any discount.
        currency:
          type:
            - string
            - 'null'
          description: ISO 4217 currency code.
        availability:
          type:
            - string
            - 'null'
          enum:
            - in_stock
            - out_of_stock
            - limited_availability
            - preorder
            - backorder
            - made_to_order
            - discontinued
            - null
          description: Stock or ordering availability.
        category:
          type:
            - string
            - 'null'
          description: Product category.
        imageUrl:
          type:
            - string
            - 'null'
          format: uri
          description: Main product image URL.
        images:
          type: array
          items:
            type: string
            format: uri
          description: Product image URLs, main image first.
        dimensions:
          type: array
          items:
            type: string
          description: Product dimensions as shown on the page.
        features:
          type: array
          items:
            type: string
          description: Key features and specifications.
        targetAudience:
          type: array
          items:
            type: string
          description: Intended audience.
        tags:
          type: array
          items:
            type: string
          description: Product tags.
        variants:
          $ref: '#/components/schemas/ProductVariants'
      required:
        - name
        - description
        - brand
        - sku
        - price
        - regularPrice
        - currency
        - availability
        - category
        - imageUrl
        - images
        - dimensions
        - features
        - targetAudience
        - tags
        - variants
    PageMetadataValue:
      oneOf:
        - type: string
        - type: array
          items:
            type: string
    PageMetadataAlternate:
      type: object
      properties:
        href:
          type: string
          description: Resolved alternate URL.
        hreflang:
          type: string
          description: Language or locale for the alternate URL, when present.
        type:
          type: string
          description: Alternate resource MIME type, when present.
        title:
          type: string
          description: Alternate resource title, when present.
      required:
        - href
      additionalProperties: false
    PageMetadataHeading:
      type: object
      properties:
        level:
          type: integer
          minimum: 1
          maximum: 6
          description: Heading level, 1–6 (from h1–h6).
        text:
          type: string
          description: >-
            Heading text with whitespace collapsed, truncated to 1000
            characters.
      required:
        - level
        - text
      additionalProperties: false
    ProductVariants:
      type: array
      items:
        type: object
        properties:
          sku:
            type:
              - string
              - 'null'
          attributes:
            type: object
            additionalProperties:
              type: string
            description: >-
              Explicit variant attributes such as color, size, material, pattern
              and properties declared by page.
          url:
            type:
              - string
              - 'null'
            description: >-
              Variant or offer URL when provided by the source. May be shared by
              variants.
          images:
            type: array
            items:
              type: string
            description: Original source image URLs explicitly attached to this variant.
        required:
          - sku
          - attributes
          - url
          - images
      description: >-
        Product variations, such as different colors or sizes, with their
        attributes and images. Empty if none are found. May not include every
        variation offered by the store.
  headers:
    RequestId:
      description: Unique ID of this request; also `request_id` in JSON bodies.
      schema:
        type: string
        format: uuid
    RateLimitLimit:
      description: >-
        Maximum request units per minute, or maximum concurrent requests when
        X-RateLimit-Mode is concurrency.
      schema:
        type: integer
        minimum: 1
    RateLimitRemaining:
      description: >-
        Request units remaining in the current minute, or concurrent requests
        still available when X-RateLimit-Mode is concurrency.
      schema:
        type: integer
        minimum: 0
    RateLimitReset:
      description: >-
        Unix timestamp in seconds when the per-minute rate limit resets. Omitted
        for concurrency limits.
      schema:
        type: integer
    RateLimitMode:
      description: >-
        Set to concurrency when these headers report concurrent requests. When a
        per-minute limit also applies, its rejections report per-minute headers
        without this header. New Free accounts have 2 concurrent requests and 10
        requests per minute; paid plans have no per-minute limit by default.
        Existing and custom allowances can differ.
      schema:
        type: string
        enum:
          - concurrency
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        Send `Authorization: Bearer <API_KEY>`. Keys have full access unless
        restricted to scopes.

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.