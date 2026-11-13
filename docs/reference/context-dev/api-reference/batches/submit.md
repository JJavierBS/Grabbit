# Submit a batch

> Scrape up to 100,000 URLs, or crawl a site, asynchronously. Poll the batch ID or receive a webhook when it finishes.

From 1 credit per page

Requires [`batches:write` permission](https://docs.context.dev/account/api-keys). See the [guide](https://docs.context.dev/batches/submit.md) for examples and usage.


## OpenAPI

````yaml POST /batch/submit
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
  /batch/submit:
    post:
      tags:
        - Batches
      summary: Submit a batch
      description: >-
        Scrape up to 100,000 URLs, or crawl a site, asynchronously using the
        same formats and scrape parameters as POST /web/scrape. Choose Markdown,
        HTML, screenshots, images, bytes, parsed fields, products, highlights,
        and JSON. Submission persists the input and returns immediately with
        status pending. Organizations with fewer than 10 available credits and
        no overage are rejected with 402 up front. Each organization can submit
        up to 2,500 batches per minute, independently of its polling budget.
        Batches wait pending when execution capacity is full. Validation,
        sitemap discovery, the full credit quote, and shard scheduling happen
        afterward. Poll the batch ID or receive a webhook when it finishes.
        Deferred rejections appear as status failed with a failure code and
        message.
      operationId: submitBatch
      parameters:
        - schema:
            type: string
            maxLength: 200
            description: >-
              Unique key per submission. Retrying with the same key and body
              returns the original batch; a different body returns `409`.
          required: false
          description: >-
            Unique key per submission. Retrying with the same key and body
            returns the original batch; a different body returns `409`.
          name: Idempotency-Key
          in: header
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BatchSubmitRequest'
            examples:
              scrapeAnything:
                summary: Scrape URLs as Markdown and HTML
                value:
                  input:
                    mode: scrape
                    data:
                      urls:
                        - url: https://example.com/products/anvil
                          itemId: sku-1
                          meta:
                            category: tools
                        - url: https://example.com/products/hammer
                          itemId: sku-2
                      formats:
                        markdown: true
                        html: true
                      sharedParams:
                        mainContentOnly: true
              scrapeScreenshots:
                summary: Capture screenshots and images
                value:
                  input:
                    mode: scrape
                    data:
                      urls:
                        - url: https://example.com
                        - url: https://example.com/pricing
                      formats:
                        screenshot: true
                        images: true
                      screenshotParams:
                        area: fullPage
                        format: png
              scrapeJson:
                summary: Extract structured JSON from each URL
                value:
                  input:
                    mode: scrape
                    data:
                      urls:
                        - url: https://example.com/products/anvil
                      formats:
                        json: true
                      jsonParams:
                        schema:
                          type: object
                          properties:
                            name:
                              type: string
                            price:
                              type:
                                - number
                                - 'null'
                          required:
                            - name
                          additionalProperties: false
              crawlAnything:
                summary: Crawl a site with multiple output formats
                value:
                  input:
                    mode: crawl
                    data:
                      source:
                        type: start_url
                        url: https://example.com/docs
                        controls:
                          maxUrls: 500
                          maxDepth: 3
                      formats:
                        markdown: true
                        html: true
                      sharedParams:
                        mainContentOnly: true
              crawlSitemapAnything:
                summary: Scrape sitemap pages with selected formats
                value:
                  input:
                    mode: crawl
                    data:
                      source:
                        type: sitemap
                        domain: example.com
                        controls:
                          maxUrls: 250
                      formats:
                        markdown: true
                        images: true
      responses:
        '200':
          description: >-
            Batch stored. Reserved page counts and credits remain zero until
            background preparation finishes. Read progress and results from `GET
            /batch/{batch_id}`.
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
                allOf:
                  - $ref: '#/components/schemas/BatchAccepted'
                  - type: object
                    properties:
                      key_metadata:
                        $ref: '#/components/schemas/KeyMetadata'
                      request_id:
                        $ref: '#/components/schemas/RequestId'
                    required:
                      - request_id
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          description: Authentication failed.
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
            The key lacks `batches:write` (`INSUFFICIENT_PERMISSIONS`). Batch
            limits and the full credit quote are checked in the background.
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
            Idempotency-Key reused with a different body (error_code
            IDEMPOTENCY_KEY_CONFLICT).
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
          description: >-
            The organization exceeded 2,500 batch submissions per minute or its
            pending workload quota. Pending work is capped at 32,000 batches, 32
            million submitted URLs, and 4 GiB of input. Wait for batches to
            start or cancel pending batches before retrying.
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
          description: Batch input or its record could not be stored.
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
    BatchSubmitRequest:
      type: object
      properties:
        input:
          oneOf:
            - type: object
              properties:
                mode:
                  type: string
                  enum:
                    - scrape
                  description: Scrape the pages in `data.urls`.
                data:
                  title: Scrape data
                  description: Pages to scrape and their output format.
                  allOf:
                    - $ref: '#/components/schemas/BatchUnifiedScrapeData'
              required:
                - mode
                - data
              additionalProperties: false
              title: Scrape
              description: Scrape a list of up to 100,000 URLs.
            - type: object
              properties:
                mode:
                  type: string
                  enum:
                    - crawl
                  description: Discover and scrape pages from `data.source`.
                data:
                  title: Crawl data
                  description: Crawl source and output format.
                  allOf:
                    - $ref: '#/components/schemas/BatchUnifiedCrawlData'
              required:
                - mode
                - data
              additionalProperties: false
              title: Crawl
              description: Crawl pages starting from a URL or from a domain's sitemap.
          discriminator:
            propertyName: mode
          title: Batch input
          description: Choose a URL list or a site crawl.
        webhookUrl:
          type: string
          format: uri
          description: >-
            Legacy URL notified when the batch finishes. Preserves one
            best-effort attempt. Cannot be combined with webhook.
        webhook:
          type: object
          properties:
            url:
              type: string
              format: uri
              description: >-
                Public HTTP(S) URL that receives batch completion, failure, or
                cancellation events.
            retry:
              $ref: '#/components/schemas/WebhookRetry'
          required:
            - url
          additionalProperties: false
          description: >-
            Where to send the batch's final-status event. Omit `retry` for one
            attempt; `{}` uses the default retry schedule.
        tags:
          type: array
          items:
            type: string
            minLength: 1
            maxLength: 50
          maxItems: 20
          description: Tags stored on the batch. Filter the batch list by them later.
          example:
            - docs
            - competitor
        policies:
          type: array
          items:
            type: string
          description: >-
            Access policy IDs to apply to every page. A URL must pass every
            policy.
          example:
            - pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e
      required:
        - input
      additionalProperties: false
      title: Submit batch request
      description: Create an asynchronous scraping job.
    BatchAccepted:
      type: object
      properties:
        id:
          type: string
          example: batch_9f2c8a
          description: Batch ID. Poll GET /batch/{batch_id} with it.
        status:
          type: string
          enum:
            - pending
            - queued
            - running
            - cancelling
            - completed
            - cancelled
            - failed
          description: >-
            Current state. `pending` means waiting for execution capacity or
            background validation. Capacity-limited batches remain pending until
            a slot opens. `completed`, `cancelled`, and `failed` are final.
        mode:
          type: string
          enum:
            - scrape
            - crawl
          description: How pages will be selected.
        tags:
          type: array
          items:
            type: string
          description: Tags stored on the batch.
          example:
            - docs
        crawl:
          $ref: '#/components/schemas/BatchNullableCrawlControls'
        input:
          $ref: '#/components/schemas/BatchIntake'
        credits:
          type: object
          properties:
            reserved:
              type: integer
              example: 24817
              description: Credits reserved by background preparation. Zero while pending.
          required:
            - reserved
          description: >-
            Credits are reserved after background validation, before scraping
            starts.
        created_at:
          type: string
          description: When the batch was created.
        invalid_urls:
          type: array
          items:
            type: object
            properties:
              url:
                type: string
                description: Rejected URL.
              reason:
                type: string
                description: Why it was rejected.
                example: Must be a public http:// or https:// URL
            required:
              - url
              - reason
          description: Rejected URLs (first 100).
        cache_metadata:
          $ref: '#/components/schemas/CacheMetadata'
        webhook_secret:
          type: string
          description: >-
            Secret for verifying `X-Context-Signature`. Only submit returns it,
            so store it.
        formats:
          $ref: '#/components/schemas/ScrapeFormats'
          example:
            html: true
            markdown: true
          description: >-
            Outputs requested for each page. Matches input.data.formats on
            submission.
      required:
        - id
        - status
        - mode
        - tags
        - crawl
        - input
        - credits
        - created_at
        - invalid_urls
        - cache_metadata
        - formats
      title: Accepted batch
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
    BatchUnifiedScrapeData:
      type: object
      properties:
        urls:
          type: array
          items:
            type: object
            properties:
              url:
                type: string
                minLength: 1
                description: Page URL to scrape.
                example: https://example.com/products/anvil
              itemId:
                type: string
                minLength: 1
                maxLength: 200
                description: >-
                  Your ID for this page, returned with its result. The same URL
                  can use different IDs.
                example: sku-1
              meta:
                type: object
                additionalProperties: {}
                description: Custom JSON returned unchanged with this page result.
            required:
              - url
            additionalProperties: false
            description: A page to scrape, with optional data for matching results.
          minItems: 1
          maxItems: 100000
          description: Pages to scrape. Maximum 100000.
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
            - disabled
          default: disabled
          description: >-
            Batches persist their results. Only disabled is supported; enabled
            returns ZDR_NOT_SUPPORTED.
        timeoutOpts:
          $ref: '#/components/schemas/ScrapeTimeout'
          description: >-
            Deadline for each page, using the same behavior and defaults as POST
            /web/scrape.
        tags:
          $ref: '#/components/schemas/RequestTags'
      required:
        - urls
        - formats
      additionalProperties: false
      title: Scrape Anything
      description: >-
        Use the same formats and parameters as POST /web/scrape, replacing url
        with urls. Options apply to every page.
    BatchUnifiedCrawlData:
      type: object
      properties:
        source:
          oneOf:
            - type: object
              properties:
                type:
                  type: string
                  enum:
                    - start_url
                  description: Start from one page.
                url:
                  type: string
                  minLength: 1
                  description: >-
                    Page where crawling begins. A URL without a scheme is read
                    as https://.
                  example: https://example.com/docs
                controls:
                  type: object
                  properties:
                    maxUrls:
                      type: integer
                      minimum: 1
                      maximum: 100000
                      default: 100
                      description: >-
                        Maximum pages to fetch. Unused reserved credits are
                        refunded. Maximum 100000.
                    maxDepth:
                      type: integer
                      minimum: 0
                      maximum: 50
                      description: >-
                        Maximum link depth. Source pages are depth 0. No limit
                        when omitted.
                    followSubdomains:
                      type: boolean
                      default: false
                      description: Follow links to subdomains.
                    regex:
                      type: string
                      maxLength: 256
                      description: >-
                        Regex pattern for URLs to include. The `start_url`
                        itself is always included.
                      example: ^https://example\.com/docs/
                    excludeRegex:
                      type: string
                      maxLength: 256
                      description: >-
                        Regex pattern for URLs to exclude, even when they match
                        `regex`. The `start_url` itself is always included.
                      example: /tag/|/author/
                    languages:
                      anyOf:
                        - type: string
                          enum:
                            - same_as_start_url
                        - type: array
                          items:
                            type: string
                            enum:
                              - am
                              - ar
                              - az
                              - be
                              - bg
                              - bn
                              - ca
                              - ceb
                              - cs
                              - cy
                              - da
                              - de
                              - el
                              - en
                              - es
                              - et
                              - eu
                              - fa
                              - fi
                              - fr
                              - gu
                              - ha
                              - haw
                              - he
                              - hi
                              - hr
                              - hu
                              - hy
                              - id
                              - is
                              - it
                              - ja
                              - ka
                              - kk
                              - kn
                              - ko
                              - ku
                              - ky
                              - lo
                              - lt
                              - lv
                              - mk
                              - ml
                              - mn
                              - mr
                              - ms
                              - ne
                              - nl
                              - 'no'
                              - or
                              - pa
                              - pl
                              - ps
                              - pt
                              - ro
                              - ru
                              - sk
                              - sl
                              - so
                              - sq
                              - sr
                              - sv
                              - sw
                              - ta
                              - te
                              - th
                              - tl
                              - tr
                              - uk
                              - ur
                              - uz
                              - vi
                              - yo
                              - zh
                          minItems: 1
                      description: >-
                        Only follow pages in these languages, or
                        `same_as_start_url`; all languages when omitted.
                      example: same_as_start_url
                  default:
                    maxUrls: 100
                    followSubdomains: false
                  additionalProperties: false
                  description: Limits and filters for page discovery.
              required:
                - type
                - url
              additionalProperties: false
              description: Discover pages by following links from one URL.
              title: Start URL
            - type: object
              properties:
                type:
                  type: string
                  enum:
                    - sitemap
                  description: Scrape the URLs in the domain's sitemap.
                domain:
                  type: string
                  minLength: 3
                  description: >-
                    Domain whose sitemap lists the pages to scrape. A full URL
                    is reduced to its domain.
                  example: example.com
                controls:
                  type: object
                  properties:
                    maxUrls:
                      type: integer
                      minimum: 1
                      maximum: 100000
                      default: 100
                      description: >-
                        Maximum pages to fetch. Unused reserved credits are
                        refunded. Maximum 100000.
                    regex:
                      type: string
                      maxLength: 256
                      description: >-
                        Regex pattern; only sitemap URLs matching it are
                        scraped.
                      example: ^https://example\.com/docs/
                    excludeRegex:
                      type: string
                      maxLength: 256
                      description: >-
                        Regex pattern; sitemap URLs matching it are not scraped,
                        even when they match `regex`.
                      example: /tag/|/author/
                    excludePaths:
                      type: array
                      items:
                        type: string
                        minLength: 1
                        maxLength: 200
                      maxItems: 100
                      default:
                        - /feed
                        - /rss
                        - /atom
                        - /api/
                        - /cdn-cgi/
                        - /_next/
                        - /__
                      description: >-
                        Path fragments that skip a sitemap URL in a crawl. Works
                        separately from any regex inclusion or exclusion you
                        define. Defaults to
                        ["/feed","/rss","/atom","/api/","/cdn-cgi/","/_next/","/__"].
                        Pass `[]` to keep every listed URL.
                      example: []
                  default:
                    maxUrls: 100
                    excludePaths:
                      - /feed
                      - /rss
                      - /atom
                      - /api/
                      - /cdn-cgi/
                      - /_next/
                      - /__
                  additionalProperties: false
                  description: >-
                    Limits and filters for the sitemap URLs. A sitemap batch
                    scrapes exactly those URLs and never follows links off them,
                    so there is no crawl depth here.
              required:
                - type
                - domain
              additionalProperties: false
              description: >-
                Scrape the pages listed in a domain's sitemap. Links on those
                pages are not followed.
              title: Sitemap
          discriminator:
            propertyName: type
          title: Crawl source
          description: How to find pages to crawl.
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
            - disabled
          default: disabled
          description: >-
            Batches persist their results. Only disabled is supported; enabled
            returns ZDR_NOT_SUPPORTED.
        timeoutOpts:
          $ref: '#/components/schemas/ScrapeTimeout'
          description: >-
            Deadline for each page, using the same behavior and defaults as POST
            /web/scrape.
        tags:
          $ref: '#/components/schemas/RequestTags'
      required:
        - source
        - formats
      additionalProperties: false
      title: Crawl with Scrape Anything
      description: >-
        Use the same formats and parameters as POST /web/scrape, replacing url
        with source. Options apply to every page.
    WebhookRetry:
      type: object
      properties:
        delays_seconds:
          type: array
          items:
            type: integer
            minimum: 1
            maximum: 86400
          maxItems: 10
          description: >-
            Retry delays in seconds, totaling at most 72 hours. Use [] to
            disable automatic retries.
          example:
            - 30
            - 300
            - 3600
      additionalProperties: false
      description: Webhook retry settings. Use {} for the default schedule.
      example:
        delays_seconds:
          - 10
          - 60
          - 300
          - 1800
          - 7200
          - 21600
          - 57600
    BatchNullableCrawlControls:
      anyOf:
        - allOf:
            - $ref: '#/components/schemas/BatchCrawlControls'
        - type: 'null'
      description: How the crawl was configured. Null for scrape batches.
    BatchIntake:
      type: object
      properties:
        reserved:
          type: integer
          example: 24817
          description: Pages accepted; progress counts toward this total.
        reserved_is_ceiling:
          type: boolean
          example: false
          description: >-
            True when `reserved` is a crawl ceiling; false when it is an exact
            URL count.
        submitted:
          type:
            - integer
            - 'null'
          example: 25000
          description: >-
            URLs in the list you sent, before validation and de-duplication.
            Null for a crawl, which is given a source rather than a list.
        duplicates:
          type: integer
          example: 183
          description: >-
            URLs dropped before reserving because another entry resolved to the
            same page. Non-zero for sitemap crawls too, whose sitemaps routinely
            list a page more than once.
        invalid:
          type:
            - integer
            - 'null'
          example: 0
          description: Rejected input URLs; `null` for a crawl.
      required:
        - reserved
        - reserved_is_ceiling
        - submitted
        - duplicates
        - invalid
      x-stainless-model: batch.intake
      description: What the submission accepted.
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
    BatchCrawlControls:
      type: object
      properties:
        source:
          anyOf:
            - type: object
              properties:
                type:
                  type: string
                  enum:
                    - start_url
                url:
                  type: string
                  example: https://example.com/docs
                  description: Page the crawl started from.
              required:
                - type
                - url
              title: Start URL
              description: The crawl discovered pages by following links from one URL.
            - type: object
              properties:
                type:
                  type: string
                  enum:
                    - sitemap
                domain:
                  type: string
                  example: example.com
                  description: Domain whose sitemap supplied the pages.
              required:
                - type
                - domain
              title: Sitemap
              description: The crawl scraped the pages listed in the domain's sitemap.
          description: Where the crawl started.
        max_pages:
          type: integer
          example: 500
          description: >-
            The `maxUrls` submitted with the crawl. A sitemap crawl scrapes only
            the URLs its sitemap actually lists, up to this many, so
            `input.reserved` is often lower.
        max_depth:
          type:
            - integer
            - 'null'
          example: 0
          description: >-
            Link depth limit. Always 0 for a sitemap crawl, which never follows
            links off its URLs; null when a `start_url` crawl set no limit.
        follow_subdomains:
          type: boolean
          description: >-
            Whether links to subdomains were followed. Always false for a
            sitemap crawl.
        url_pattern:
          type:
            - string
            - 'null'
          example: ^https://example\.com/docs/
          description: >-
            Regex pattern URLs had to match to be crawled. Null when the crawl
            set none.
        exclude_url_pattern:
          type:
            - string
            - 'null'
          example: /tag/|/author/
          description: >-
            Regex pattern URLs must not match to be crawled. Null when the crawl
            set none.
        languages:
          anyOf:
            - type: string
              enum:
                - same_as_start_url
            - type: array
              items:
                type: string
                enum:
                  - am
                  - ar
                  - az
                  - be
                  - bg
                  - bn
                  - ca
                  - ceb
                  - cs
                  - cy
                  - da
                  - de
                  - el
                  - en
                  - es
                  - et
                  - eu
                  - fa
                  - fi
                  - fr
                  - gu
                  - ha
                  - haw
                  - he
                  - hi
                  - hr
                  - hu
                  - hy
                  - id
                  - is
                  - it
                  - ja
                  - ka
                  - kk
                  - kn
                  - ko
                  - ku
                  - ky
                  - lo
                  - lt
                  - lv
                  - mk
                  - ml
                  - mn
                  - mr
                  - ms
                  - ne
                  - nl
                  - 'no'
                  - or
                  - pa
                  - pl
                  - ps
                  - pt
                  - ro
                  - ru
                  - sk
                  - sl
                  - so
                  - sq
                  - sr
                  - sv
                  - sw
                  - ta
                  - te
                  - th
                  - tl
                  - tr
                  - uk
                  - ur
                  - uz
                  - vi
                  - yo
                  - zh
              minItems: 1
            - type: 'null'
          example: same_as_start_url
          description: Languages whose pages were followed; null when all languages were.
      required:
        - source
        - max_pages
        - max_depth
        - follow_subdomains
        - url_pattern
        - exclude_url_pattern
        - languages
      x-stainless-model: batch.crawl_controls
      title: Crawl controls
      description: Crawl settings as submitted.
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
  responses:
    BadRequest:
      description: Bad request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
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
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        Send `Authorization: Bearer <API_KEY>`. Keys have full access unless
        restricted to scopes.

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.