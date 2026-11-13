# List batches

> List your batches, newest first, with optional filters.

0 credits

Requires [`batches:read` permission](https://docs.context.dev/account/api-keys). See the [guide](https://docs.context.dev/batches/results.md) for examples and usage.


## OpenAPI

````yaml GET /batch/list
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
  /batch/list:
    get:
      tags:
        - Batches
      summary: List batches
      description: List your batches, newest first, with optional filters.
      operationId: listBatches
      parameters:
        - schema:
            type: boolean
            default: false
            description: >-
              Include batches submitted with Scrape Anything formats. Defaults
              to false.
          required: false
          description: >-
            Include batches submitted with Scrape Anything formats. Defaults to
            false.
          name: shouldIncludeUnified
          in: query
        - schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 25
            description: Batches per page. Defaults to 25.
          required: false
          description: Batches per page. Defaults to 25.
          name: limit
          in: query
        - schema:
            type: string
            description: Cursor from the previous page.
          required: false
          description: Cursor from the previous page.
          name: cursor
          in: query
        - schema:
            type: string
            enum:
              - pending
              - queued
              - running
              - cancelling
              - completed
              - cancelled
              - failed
            description: Filter by status.
          required: false
          description: Filter by status.
          name: status
          in: query
        - schema:
            type: string
            maxLength: 200
            description: >-
              Free-text search term, matched against the batch id, crawl source
              (start URL or sitemap domain), and tags.
            example: batch_1a2b
          required: false
          description: >-
            Free-text search term, matched against the batch id, crawl source
            (start URL or sitemap domain), and tags.
          name: q
          in: query
        - schema:
            type: string
            enum:
              - exact
              - prefix
            description: >-
              `prefix` for as-you-type prefix matching (default), `exact` for
              full-token matching.
          required: false
          description: >-
            `prefix` for as-you-type prefix matching (default), `exact` for
            full-token matching.
          name: search_type
          in: query
        - schema:
            anyOf:
              - type: string
              - type: array
                items:
                  type: string
            description: >-
              Tags to filter by (matches batches having any of them). Pass
              repeated `tags` params or one comma-separated list, e.g.
              `tags=docs,competitor`.
            example: docs,competitor
          required: false
          description: >-
            Tags to filter by (matches batches having any of them). Pass
            repeated `tags` params or one comma-separated list, e.g.
            `tags=docs,competitor`.
          name: tags
          in: query
      responses:
        '200':
          description: >-
            Your batches, newest first. Use `next_cursor` to page through the
            rest.
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
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Batch'
                    description: Batches on this page.
                  has_more:
                    type: boolean
                    description: Whether another page is available.
                  next_cursor:
                    type:
                      - string
                      - 'null'
                    description: Cursor for the next page.
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - request_id
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          description: >-
            API key permissions or organization settings do not allow this
            request.
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
          $ref: '#/components/responses/RateLimited'
        '503':
          description: >-
            Search is temporarily unavailable (`SEARCH_UNAVAILABLE`). Retry or
            list without search filters.
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
  schemas:
    Batch:
      type: object
      properties:
        id:
          type: string
          example: batch_9f2c8a
          description: Batch ID.
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
          description: '`scrape` (URL list) or `crawl`.'
        tags:
          type: array
          items:
            type: string
          description: Tags stored on the batch at submission.
          example:
            - docs
        crawl:
          $ref: '#/components/schemas/BatchNullableCrawlControls'
        input:
          $ref: '#/components/schemas/BatchIntake'
        progress:
          type: object
          properties:
            succeeded:
              type: integer
              example: 18091
              description: Pages scraped successfully.
            failed:
              type: integer
              example: 311
              description: Pages that could not be scraped.
            pending:
              type: integer
              example: 6415
              description: >-
                Accepted pages not yet attempted. Unused crawl capacity is
                excluded after completion.
          required:
            - succeeded
            - failed
            - pending
          description: Pages attempted so far. Use `status` to check completion.
        credits:
          type: object
          properties:
            reserved:
              type: integer
              example: 24817
              description: >-
                Credits held by background preparation before scraping starts.
                Zero while pending.
            refunded:
              type: integer
              example: 6726
              description: Credits returned for unsuccessful pages when the batch settles.
            ocr_charged:
              type: integer
              example: 42
              description: OCR usage charged when the batch settles.
            net:
              type: integer
              example: 18091
              description: '`reserved` minus `refunded` plus `ocr_charged`.'
          required:
            - reserved
            - refunded
            - ocr_charged
            - net
          description: Batch credit usage and settlement.
        timing:
          type: object
          properties:
            created_at:
              type: string
              description: When the batch was created.
            started_at:
              type:
                - string
                - 'null'
              description: When processing started. Null while queued.
            completed_at:
              type:
                - string
                - 'null'
              description: When processing finished. Null while active.
          required:
            - created_at
            - started_at
            - completed_at
        page_errors:
          type: array
          items:
            $ref: '#/components/schemas/BatchPageErrorCount'
          description: >-
            Individual page failures grouped by error code, sorted by count.
            Unrelated to `failure`, which is the batch itself failing.
        failure:
          $ref: '#/components/schemas/BatchNullableFailure'
        results:
          type:
            - object
            - 'null'
          properties:
            expires_at:
              type: string
              description: When these links expire (24 hours after this response).
            files:
              type: array
              items:
                type: object
                properties:
                  url:
                    type: string
                    description: Temporary URL for a gzipped NDJSON file.
                  items:
                    type: integer
                    description: Results in this file.
                  bytes:
                    type: integer
                    description: Compressed file size in bytes.
                required:
                  - url
                  - items
                  - bytes
              description: Result files. Order is not guaranteed.
          required:
            - expires_at
            - files
          description: >-
            Result download links; null until the batch finishes. Files are
            deleted 180 days after the batch finishes.
        formats:
          $ref: '#/components/schemas/ScrapeFormats'
          example:
            html: true
            markdown: true
          description: >-
            Outputs requested for each page. Matches input.data.formats on
            submission.
        policies:
          type: array
          items:
            type: string
          description: Access policy IDs applied to every page.
          example:
            - pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e
      required:
        - id
        - status
        - mode
        - tags
        - crawl
        - input
        - progress
        - credits
        - timing
        - page_errors
        - failure
        - results
        - formats
      title: Batch
      description: An asynchronous web scraping job.
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
    BatchPageErrorCount:
      type: object
      properties:
        code:
          type: string
          example: WEBSITE_ACCESS_ERROR
          description: Error code for these failures.
        count:
          type: integer
          example: 204
          description: Pages that failed with this code.
      required:
        - code
        - count
      x-stainless-model: batch.page_error_count
      description: Page failures sharing one error code.
    BatchNullableFailure:
      anyOf:
        - allOf:
            - $ref: '#/components/schemas/BatchFailure'
        - type: 'null'
      description: >-
        Why the batch as a whole stopped. Null unless `status` is `failed`.
        Individual pages that failed are counted in `page_errors` instead.
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
    BatchFailure:
      type: object
      properties:
        code:
          type: string
          example: stalled
          description: Why the batch itself stopped.
        message:
          type: string
          example: Batch stopped reporting progress and was finalized automatically
          description: Human-readable explanation.
      required:
        - code
        - message
      x-stainless-model: batch.failure
      description: >-
        A failure of the batch as a whole, distinct from the per-page failures
        in `page_errors`.
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
    Unauthorized:
      description: Unauthorized
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
    RateLimited:
      description: >-
        Rate limit exceeded. Organization concurrency rejections include
        structured error_data and subscription settings; follow Retry-After
        before retrying.
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
        Retry-After:
          description: Seconds to wait before retrying.
          schema:
            type: integer
            minimum: 1
            maximum: 60
      content:
        application/json:
          schema:
            type: object
            properties:
              message:
                type: string
                description: Human-readable error message.
              error_code:
                type: string
                enum:
                  - RATE_LIMITED
                description: Error code indicating the rate limit was exceeded
              error_data:
                $ref: '#/components/schemas/ConcurrencyErrorData'
              key_metadata:
                $ref: '#/components/schemas/KeyMetadata'
              request_id:
                $ref: '#/components/schemas/RequestId'
            required:
              - message
              - error_code
              - request_id
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        Send `Authorization: Bearer <API_KEY>`. Keys have full access unless
        restricted to scopes.

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.