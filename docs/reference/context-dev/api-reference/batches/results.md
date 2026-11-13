# List batch results

> Page through a finished batch’s results as JSON. Results remain available for 180 days.

0 credits

Requires [`batches:read` permission](https://docs.context.dev/account/api-keys). See the [guide](https://docs.context.dev/batches/results.md) for examples and usage.


## OpenAPI

````yaml GET /batch/{batch_id}/results
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
  /batch/{batch_id}/results:
    get:
      tags:
        - Batches
      summary: List batch results
      description: >-
        Page through a finished batch’s results as JSON. Each record contains
        result with the same outputs and per-format errors as POST /web/scrape.
        Results remain available for 180 days.
      operationId: getBatchResults
      parameters:
        - schema:
            type: string
            example: batch_9f2c8a
            description: Batch ID.
          required: true
          description: Batch ID.
          name: batch_id
          in: path
        - schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 25
            description: >-
              Records per page. Defaults to 25. A page can close early so its
              payload stays under ~8 MB; rely on next_cursor rather than
              counting records.
          required: false
          description: >-
            Records per page. Defaults to 25. A page can close early so its
            payload stays under ~8 MB; rely on next_cursor rather than counting
            records.
          name: limit
          in: query
        - schema:
            type: string
            pattern: ^\d+:\d+$
            description: next_cursor from the previous page.
          required: false
          description: next_cursor from the previous page.
          name: cursor
          in: query
      responses:
        '200':
          description: >-
            One page of result records. Keep paging with `next_cursor` while
            `has_more` is true.
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
                      $ref: '#/components/schemas/BatchResultRecord'
                    description: Result records on this page.
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
        '404':
          $ref: '#/components/responses/NotFound'
        '409':
          description: Batch has not finished yet (error_code BATCH_NOT_COMPLETED).
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
    BatchResultRecord:
      title: Batch result record
      description: >-
        One scrape outcome. result uses the single Scrape Anything response
        schema; itemId and meta identify your input.
      discriminator:
        propertyName: status
      oneOf:
        - type: object
          additionalProperties: false
          title: Scraped page
          description: >-
            At least one requested output succeeded. Check result.isPartial and
            each output success for incomplete results.
          properties:
            url:
              type: string
              example: https://example.com/products/anvil
              description: URL as submitted, or as discovered by the crawl.
            itemId:
              type: string
              example: sku-1
              description: Your `itemId` from submission.
            meta:
              type: object
              additionalProperties: {}
              description: Caller-supplied metadata echoed from submission.
            status:
              type: string
              enum:
                - ok
            result:
              $ref: '#/components/schemas/BatchScrapeResponse'
            credits_used:
              type: integer
              minimum: 0
              description: >-
                Credits charged for this page, including OCR. Cached outputs use
                the same pricing as POST /web/scrape.
            ocr_pages:
              type: integer
              minimum: 0
              description: PDF pages recovered by OCR. Omitted when OCR did not run.
          required:
            - url
            - status
            - result
            - credits_used
        - type: object
          properties:
            url:
              type: string
              example: https://example.com/products/anvil
              description: URL as submitted, or as discovered by the crawl.
            itemId:
              type: string
              example: sku-1
              description: Your `itemId` from submission.
            meta:
              type: object
              additionalProperties: {}
              description: Caller-supplied metadata echoed from submission.
            status:
              type: string
              enum:
                - error
              description: The page could not be scraped.
            error_code:
              type: string
              example: NOT_FOUND
              description: Why the page failed.
            message:
              type: string
              example: Page returned 404
              description: Human-readable failure detail.
            result:
              $ref: '#/components/schemas/BatchScrapeResponse'
              description: >-
                Per-format failures when scraping returned a structured
                response. Omitted for errors that prevent scraping.
            credits_used:
              type: integer
              minimum: 0
              description: >-
                Credits charged for this page, including OCR. Cached outputs use
                the same pricing as POST /web/scrape.
            ocr_pages:
              type: integer
              minimum: 0
              description: PDF pages recovered by OCR. Omitted when OCR did not run.
          required:
            - url
            - status
            - error_code
            - message
          title: Failed page
          description: A page the batch could not fetch.
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
    BatchScrapeResponse:
      $ref: '#/components/schemas/ScrapeResponse'
      title: Scrape result
      description: >-
        The same response as POST /web/scrape, including per-format success,
        failure, and partial results.
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
    NotFound:
      description: Not found
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