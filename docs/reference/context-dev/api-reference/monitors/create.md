# Create a monitor

> Watch a page, URL inventory, or extracted website data on a schedule. A run starts immediately to capture the baseline.

1, 2, or 10 credits per run

Requires [`monitors:write` permission](https://docs.context.dev/account/api-keys). See the [guide](https://docs.context.dev/monitors/overview) for examples and usage.


## OpenAPI

````yaml POST /monitors
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
  /monitors:
    post:
      tags:
        - Monitors
      summary: Create a monitor
      description: >-
        Watch a page, URL inventory, or extracted website data on a schedule. A
        run starts immediately to capture the baseline.
      operationId: createMonitor
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MonitorsCreateMonitorRequest'
            examples:
              page_exact:
                summary: Exact page monitor
                value:
                  mode: web
                  name: Acme pricing page
                  target:
                    type: page
                    url: https://acme.com/pricing
                  change_detection:
                    type: exact
                  schedule:
                    type: interval
                    frequency: 6
                    unit: hours
                  webhook:
                    url: https://example.com/webhook
              sitemap_exact:
                summary: Exact sitemap monitor
                value:
                  mode: web
                  name: Acme sitemap
                  target:
                    type: sitemap
                    url: https://acme.com/sitemap.xml
                  change_detection:
                    type: exact
                  schedule:
                    type: interval
                    frequency: 1
                    unit: days
                  webhook:
                    url: https://example.com/webhook
              extract_semantic:
                summary: Semantic extract monitor
                value:
                  mode: web
                  name: Acme website positioning
                  target:
                    type: extract
                    url: https://acme.com
                    instructions: >-
                      Extract the product positioning, pricing, packaging, and
                      headline feature claims.
                    max_pages: 10
                  change_detection:
                    type: semantic
                  schedule:
                    type: interval
                    frequency: 1
                    unit: days
                  webhook:
                    url: https://example.com/webhook
      responses:
        '201':
          description: Monitor created
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
                $ref: '#/components/schemas/MonitorsCreateMonitorResponse'
        '400':
          $ref: '#/components/responses/MonitorsBadRequest'
        '401':
          $ref: '#/components/responses/MonitorsUnauthorized'
        '403':
          $ref: '#/components/responses/MonitorsLimitExceeded'
        '429':
          $ref: '#/components/responses/RateLimited'
      security:
        - bearerAuth: []
components:
  schemas:
    MonitorsCreateMonitorRequest:
      type: object
      properties:
        mode:
          $ref: '#/components/schemas/MonitorsMode'
        name:
          type: string
          minLength: 1
          maxLength: 200
          description: Display name for the monitor.
          example: Acme pricing monitor
        tags:
          type: array
          items:
            type: string
            minLength: 1
            maxLength: 50
          maxItems: 20
          uniqueItems: true
          description: Labels for filtering monitors, their changes, and their usage.
          example:
            - pricing
            - competitor
        target:
          $ref: '#/components/schemas/MonitorsTarget'
        change_detection:
          $ref: '#/components/schemas/MonitorsChangeDetection'
        schedule:
          $ref: '#/components/schemas/MonitorsSchedule'
        webhook:
          $ref: '#/components/schemas/MonitorsNullableWebhookConfig'
        policies:
          type: array
          items:
            type: string
          description: Access policy IDs to apply to every run.
          example:
            - pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e
      required:
        - name
        - target
      additionalProperties: false
      title: Create monitor request
      description: >-
        Monitor target, detection method, and schedule. Omitted schedules run
        daily.
    MonitorsCreateMonitorResponse:
      type: object
      properties:
        mode:
          $ref: '#/components/schemas/MonitorsMode'
        id:
          type: string
          example: mon_123
        name:
          type: string
          example: Acme pricing monitor
        target:
          $ref: '#/components/schemas/MonitorsTarget'
        change_detection:
          $ref: '#/components/schemas/MonitorsChangeDetection'
        schedule:
          $ref: '#/components/schemas/MonitorsSchedule'
        webhook:
          $ref: '#/components/schemas/MonitorsNullableWebhookConfig'
        status:
          $ref: '#/components/schemas/MonitorsMonitorStatus'
        last_run_at:
          type:
            - string
            - 'null'
          format: date-time
        last_change_at:
          type:
            - string
            - 'null'
          format: date-time
        next_run_at:
          type:
            - string
            - 'null'
          format: date-time
          description: When the next scheduled run is due; null while paused.
        last_error:
          anyOf:
            - allOf:
                - $ref: '#/components/schemas/MonitorsRunError'
            - type: 'null'
          description: >-
            Error from the most recent failed run; null when the last run
            succeeded.
        webhook_failure:
          anyOf:
            - $ref: '#/components/schemas/MonitorsWebhookFailure'
            - type: 'null'
          description: >-
            Present while webhook deliveries are failing consecutively; null
            when deliveries are healthy or no webhook is configured. Cleared on
            the next successful delivery and when the webhook URL changes.
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
        tags:
          type: array
          items:
            type: string
            minLength: 1
            maxLength: 50
          maxItems: 20
          uniqueItems: true
          description: Labels for filtering monitors, their changes, and their usage.
          example:
            - pricing
            - competitor
        baseline:
          oneOf:
            - $ref: '#/components/schemas/MonitorsPageBaseline'
            - $ref: '#/components/schemas/MonitorsSitemapBaseline'
            - $ref: '#/components/schemas/MonitorsExtractBaseline'
            - $ref: '#/components/schemas/MonitorsSearchBaseline'
            - type: 'null'
          description: >-
            Comparison baseline, included on Retrieve. Null until capture
            completes or after target changes.
        initial_run_id:
          type:
            - string
            - 'null'
          description: >-
            ID of the baseline run queued at creation; null if it will start on
            the next scheduled tick.
          example: run_123
        policies:
          type: array
          items:
            type: string
          description: Access policy IDs applied to every run.
          example:
            - pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e
        key_metadata:
          $ref: '#/components/schemas/KeyMetadata'
        request_id:
          $ref: '#/components/schemas/RequestId'
      required:
        - mode
        - id
        - name
        - target
        - change_detection
        - status
        - created_at
        - updated_at
        - initial_run_id
        - request_id
      additionalProperties: false
      title: Create monitor response
    MonitorsMode:
      type: string
      enum:
        - web
      description: Always `web`. Optional.
      title: Monitor mode
    MonitorsTarget:
      oneOf:
        - $ref: '#/components/schemas/MonitorsPageTarget'
        - $ref: '#/components/schemas/MonitorsSitemapTarget'
        - allOf:
            - $ref: '#/components/schemas/MonitorsExtractTarget'
            - description: >-
                Track relevant pages selected by `schema` and `instructions`;
                refresh the page set periodically.
        - $ref: '#/components/schemas/MonitorsSearchTarget'
      discriminator:
        propertyName: type
        mapping:
          page: '#/components/schemas/MonitorsPageTarget'
          sitemap: '#/components/schemas/MonitorsSitemapTarget'
          extract: '#/components/schemas/MonitorsExtractTarget'
          search: '#/components/schemas/MonitorsSearchTarget'
      description: >-
        What to watch: a page, a sitemap, data extracted from a site, or web
        search results.
    MonitorsChangeDetection:
      oneOf:
        - $ref: '#/components/schemas/MonitorsExactChangeDetection'
        - $ref: '#/components/schemas/MonitorsSemanticChangeDetection'
      discriminator:
        propertyName: type
        mapping:
          exact: '#/components/schemas/MonitorsExactChangeDetection'
          semantic: '#/components/schemas/MonitorsSemanticChangeDetection'
      description: >-
        How changes are judged. Defaults to `semantic` for extract and search
        targets and page targets with `instructions`, otherwise `exact`.
    MonitorsSchedule:
      oneOf:
        - $ref: '#/components/schemas/MonitorsIntervalSchedule'
      discriminator:
        propertyName: type
        mapping:
          interval: '#/components/schemas/MonitorsIntervalSchedule'
      description: How often the monitor runs. Defaults to once a day.
    MonitorsNullableWebhookConfig:
      description: >-
        Webhook destination and delivery settings. Null means no webhook is
        configured.
      anyOf:
        - allOf:
            - $ref: '#/components/schemas/MonitorsWebhookConfig'
        - type: 'null'
    MonitorsMonitorStatus:
      type: string
      enum:
        - active
        - paused
        - failed
      description: >-
        Current state. Failed monitors keep running; paused monitors must be
        resumed with `status: "active"`.
    MonitorsRunError:
      type: object
      properties:
        code:
          type: string
          example: fetch_failed
        message:
          type: string
          example: The target URL could not be fetched.
      required:
        - code
        - message
      additionalProperties: false
    MonitorsWebhookFailure:
      type: object
      properties:
        consecutive_failures:
          type: integer
          minimum: 1
          description: Number of consecutive delivery attempts that did not succeed.
          example: 3
        last_status:
          type: string
          enum:
            - rejected
            - failed
            - skipped_unsafe_url
          description: >-
            Outcome of the most recent failed delivery. rejected means a non-2xx
            response; failed means no HTTP response was received;
            skipped_unsafe_url means the URL failed the public-endpoint safety
            check.
        last_message:
          type: string
          description: Human-readable description of the most recent failure.
          example: Webhook endpoint returned HTTP 429.
        last_failed_at:
          type: string
          format: date-time
      required:
        - consecutive_failures
        - last_status
        - last_message
        - last_failed_at
      additionalProperties: false
    MonitorsPageBaseline:
      type: object
      properties:
        text:
          type: string
          description: The page's visible text as last observed.
          example: |-
            Acme Pricing
            Starter $9/mo…
        captured_at:
          type: string
          format: date-time
          description: When this baseline was last captured or replaced.
      required:
        - text
        - captured_at
      additionalProperties: false
      title: Page baseline
      description: >-
        Current baseline of a `page` monitor: the visible page text as last
        observed.
    MonitorsSitemapBaseline:
      type: object
      properties:
        urls:
          type: array
          items:
            type: string
          description: The sitemap URLs as last observed (sorted, normalized).
          example:
            - https://acme.com/blog/launch
            - https://acme.com/pricing
        url_count:
          type: integer
          description: Number of URLs in the baseline.
          example: 2
        captured_at:
          type: string
          format: date-time
          description: When this baseline was last captured or replaced.
      required:
        - urls
        - url_count
        - captured_at
      additionalProperties: false
      title: Sitemap baseline
      description: >-
        Current baseline of a `sitemap` monitor: the normalized URL set as last
        observed.
    MonitorsExtractBaseline:
      type: object
      properties:
        data:
          description: >-
            Latest structured snapshot matching the extraction schema, refreshed
            at most daily; `null` before capture.
          example:
            plans:
              - name: Starter
                price: $9/mo
        urls_analyzed:
          type: array
          items:
            type: string
          description: The page URLs the monitor tracks and analyzes for changes.
          example:
            - https://acme.com/pricing
        captured_at:
          type: string
          format: date-time
          description: When this baseline was last captured or replaced.
      required:
        - data
        - urls_analyzed
        - captured_at
      additionalProperties: false
      title: Extract baseline
      description: >-
        Current baseline of an `extract` monitor: the pages it tracks and the
        structured data as last extracted.
    MonitorsSearchBaseline:
      type: object
      properties:
        results:
          type: array
          items:
            type: object
            properties:
              url:
                type: string
                format: uri
              title:
                type: string
              description:
                type: string
                description: Result snippet.
              published_at:
                type:
                  - string
                  - 'null'
                format: date-time
                description: When the result was published, when known.
            required:
              - url
              - title
              - description
              - published_at
            additionalProperties: false
          description: Search results as last observed.
        captured_at:
          type: string
          format: date-time
          description: When this baseline was last captured or replaced.
      required:
        - results
        - captured_at
      additionalProperties: false
      title: Search baseline
      description: >-
        Current baseline of a `search` monitor: the search results as last
        observed.
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
    MonitorsPageTarget:
      type: object
      properties:
        type:
          type: string
          enum:
            - page
          description: Use `page` to watch one web page.
        url:
          type: string
          format: uri
          description: Public HTTP(S) page URL to monitor.
          example: https://acme.com/pricing
        instructions:
          type: string
          minLength: 1
          maxLength: 2000
          description: >-
            Plain-language goal describing which page changes matter. When
            provided without change_detection, semantic detection is inferred.
          example: >-
            Report pricing or plan availability changes. Ignore counters,
            timestamps, testimonials, and navigation.
        normalize_whitespace:
          type: boolean
          default: true
          description: Normalize whitespace before comparing or analyzing text.
        include_selectors:
          type: array
          items:
            type: string
            minLength: 1
            maxLength: 2048
          maxItems: 50
          description: >-
            Monitor these CSS-selected regions. Empty or omitted uses main
            content. Changes create a new baseline.
          example:
            - '#attraction-details'
        exclude_selectors:
          type: array
          items:
            type: string
            minLength: 1
            maxLength: 2048
          maxItems: 50
          description: >-
            Remove matching regions after inclusions. Changes create a new
            baseline.
          example:
            - .carousel
            - '[id^="TA_"]'
        actions:
          type:
            - array
            - 'null'
          items:
            $ref: '#/components/schemas/WebScrapeAction'
          maxItems: 5
          description: >-
            Optional browser actions executed in array order after the page
            loads, before content is captured, on every run. Requires a paid
            plan. Maximum: 5 actions. Changes create a new baseline.
      required:
        - type
        - url
      additionalProperties: false
      description: >-
        Watch a single web page. Exact detection reports visible-text diffs;
        semantic detection judges confirmed stable diffs against `instructions`.
      title: Page target
    MonitorsSitemapTarget:
      type: object
      properties:
        type:
          type: string
          enum:
            - sitemap
          description: Use `sitemap` to watch a site for added or removed URLs.
        url:
          type: string
          format: uri
          description: Sitemap URL to monitor.
          example: https://acme.com/sitemap.xml
        include:
          type: array
          items:
            type: string
            minLength: 1
            maxLength: 200
          maxItems: 50
          description: URL path patterns to include (max 50).
          example:
            - /blog/*
            - /pricing*
        exclude:
          type: array
          items:
            type: string
            minLength: 1
            maxLength: 200
          maxItems: 50
          description: URL path patterns to exclude (max 50).
          example:
            - /legal/*
            - /privacy
        max_urls:
          type: integer
          minimum: 1
          maximum: 10000
          default: 5000
          description: Maximum number of sitemap URLs to track (capped at 10,000).
      required:
        - type
        - url
      additionalProperties: false
      description: Watch a site’s URL inventory for confirmed additions and removals.
      title: Sitemap target
    MonitorsExtractTarget:
      type: object
      properties:
        type:
          type: string
          enum:
            - extract
          description: Use `extract` to watch structured data across selected pages.
        url:
          type: string
          format: uri
          description: Root URL to extract structured data from.
          example: https://acme.com
        schema:
          type: object
          additionalProperties: {}
          description: >-
            JSON Schema for page selection and the baseline snapshot. Changes
            return diffs and evidence.
          example:
            type: object
            properties:
              plans:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    price:
                      type: string
        instructions:
          type: string
          minLength: 1
          maxLength: 2000
          description: >-
            Natural-language instructions guiding which pages and facts to track
            and which changes to report.
          example: >-
            Extract every pricing plan with its monthly price and included
            limits.
        max_pages:
          type: integer
          minimum: 1
          maximum: 50
          default: 10
          description: Maximum number of pages to track.
        max_depth:
          type: integer
          minimum: 0
          maximum: 10
          description: >-
            Optional maximum link depth from the starting URL (0 = only the
            starting page).
        follow_subdomains:
          type: boolean
          default: false
          description: Allow page discovery on subdomains of the target site.
      required:
        - type
        - url
        - instructions
      additionalProperties: false
      title: Extract target
    MonitorsSearchTarget:
      type: object
      properties:
        type:
          type: string
          enum:
            - search
          description: Use `search` to watch the whole web for new results about a topic.
        query:
          type: string
          minLength: 1
          maxLength: 500
          description: >-
            Web search query to run on every check. Supports operators such as
            `site:`, `-site:`, and quoted phrases.
          example: Acme Corp acquisition
        instructions:
          type: string
          minLength: 1
          maxLength: 2000
          description: >-
            Plain-language description of which new results matter. Defaults to
            the query.
          example: >-
            Alert me when Acme announces an acquisition or a new product. Ignore
            opinion pieces.
      required:
        - type
        - query
      additionalProperties: false
      description: >-
        Search the web on every run and report results not seen before, listed
        in the change’s `matched_urls` and `evidence`. Semantic detection
        reports only results describing a new development that matches
        `instructions`; exact detection reports every new result.
      title: Search target
    MonitorsExactChangeDetection:
      type: object
      properties:
        type:
          type: string
          enum:
            - exact
          description: >-
            Use `exact` to compare visible text, sitemap URLs, or search
            results.
      required:
        - type
      additionalProperties: false
      description: >-
        Detect exact changes. For page targets, this means visible text diffs.
        For sitemap targets, this means URL additions and removals. For search
        targets, this means every new result.
      title: Exact
    MonitorsSemanticChangeDetection:
      type: object
      properties:
        type:
          type: string
          enum:
            - semantic
          description: Use `semantic` to judge changes against the target instructions.
        confidence_threshold:
          type: number
          minimum: 0
          maximum: 1
          default: 0.75
          description: >-
            Minimum confidence required to report a meaningful change, from 0 to
            1.
      required:
        - type
      additionalProperties: false
      description: >-
        Detect meaningful content changes using the target’s instructions and
        optional schema.
      title: Semantic
    MonitorsIntervalSchedule:
      type: object
      properties:
        type:
          type: string
          enum:
            - interval
          description: Use `interval` to run on a repeating schedule.
        frequency:
          type: integer
          minimum: 1
          maximum: 525600
          description: >-
            Number of units between runs. The resulting interval (frequency ×
            unit) must be at least 10 minutes and at most 1 year (e.g. minimum
            10 when unit is minutes; maximum 365 when unit is days).
          example: 6
        unit:
          $ref: '#/components/schemas/MonitorsScheduleUnit'
      required:
        - type
        - frequency
        - unit
      additionalProperties: false
      description: >-
        Run the monitor on a fixed interval defined by a frequency and a unit,
        e.g. every 6 hours or every 2 days. The total interval (frequency ×
        unit) must be between 10 minutes and 1 year.
      title: Interval
    MonitorsWebhookConfig:
      type: object
      properties:
        url:
          type: string
          format: uri
          description: >-
            Public HTTP(S) URL that receives events. Slack and GovSlack URLs get
            formatted messages.
          example: https://example.com/webhook
        events:
          type: array
          items:
            type: string
            enum:
              - change.detected
              - run.completed
          minItems: 1
          maxItems: 2
          uniqueItems: true
          description: >-
            Events to deliver. Defaults to `change.detected`; `run.completed`
            also includes unchanged runs.
          example:
            - change.detected
            - run.completed
        retry:
          $ref: '#/components/schemas/WebhookRetry'
        secret:
          type: string
          readOnly: true
          description: >-
            API-generated signing secret. Visible only with full access or
            `monitors:write` permission.
          example: whsec_8f3a…
      required:
        - url
      additionalProperties: false
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
    WebScrapeAction:
      oneOf:
        - $ref: '#/components/schemas/WebScrapeWaitAction'
        - $ref: '#/components/schemas/WebScrapePerformAction'
        - $ref: '#/components/schemas/WebScrapeScrollAction'
      discriminator:
        propertyName: do
        mapping:
          wait: '#/components/schemas/WebScrapeWaitAction'
          perform: '#/components/schemas/WebScrapePerformAction'
          scroll: '#/components/schemas/WebScrapeScrollAction'
      description: >-
        Browser action discriminated by `do`. Each variant exposes only its
        applicable fields.
    MonitorsScheduleUnit:
      type: string
      enum:
        - minutes
        - hours
        - days
      description: Time unit used with `frequency` to set the run interval.
      example: hours
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
    WebScrapeWaitAction:
      type: object
      properties:
        do:
          type: string
          enum:
            - wait
          description: Use `wait` to pause for a fixed duration.
        timeMs:
          type: integer
          minimum: 0
          maximum: 30000
          description: Time to pause in milliseconds before the next action.
      required:
        - do
        - timeMs
      additionalProperties: false
      description: >-
        Pause for a fixed number of milliseconds before continuing to the next
        action.
      title: Wait
    WebScrapePerformAction:
      type: object
      properties:
        do:
          type: string
          enum:
            - perform
          description: Use `perform` for a plain-language browser instruction.
        action:
          type: string
          minLength: 1
          maxLength: 500
          description: One browser instruction, such as clicking a button or entering text.
      required:
        - do
        - action
      additionalProperties: false
      description: Resolve and perform one natural-language browser action.
      title: Perform
    WebScrapeScrollAction:
      type: object
      properties:
        do:
          type: string
          enum:
            - scroll
          description: Use `scroll` to move through the page or a container.
        direction:
          type: string
          enum:
            - up
            - down
            - left
            - right
          description: Direction to scroll. Defaults to down.
        amount:
          anyOf:
            - type: integer
              minimum: 1
              maximum: 100000
            - type: string
              enum:
                - viewport
                - max
          description: >-
            Pixels per scroll, one visible viewport, or the current scroll
            boundary. Defaults to viewport.
        container:
          type: string
          minLength: 1
          maxLength: 2000
          description: >-
            CSS selector for the first matching scroll container. Defaults to
            the page.
        maxScrolls:
          type: integer
          minimum: 1
          maximum: 50
          description: >-
            Maximum scroll iterations. Stops early when scrolling and scrollable
            extent stop changing. Defaults to 1.
      required:
        - do
      additionalProperties: false
      description: >-
        Scroll the page or a selected scrollable container, waiting adaptively
        for content and dimensions to settle after each iteration.
      title: Scroll
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
    MonitorsBadRequest:
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
    MonitorsUnauthorized:
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
    MonitorsLimitExceeded:
      description: >-
        Monitor limit reached (`MONITOR_LIMIT_EXCEEDED`), browser actions need a
        paid plan (`PAID_PLAN_REQUIRED`), or the key lacks `monitors:write`
        (`INSUFFICIENT_PERMISSIONS`).
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