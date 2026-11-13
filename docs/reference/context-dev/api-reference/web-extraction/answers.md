# Answer questions

> Research the web and return a sourced answer in your JSON shape. Choose `fast` for a short task or `ultra` for deeper research.

10 or 100 credits

See the [guide](https://docs.context.dev/answers/overview) for examples and usage.


## OpenAPI

````yaml POST /web/answers
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
  /web/answers:
    post:
      tags:
        - Answers
      summary: Answer a research task
      description: >-
        Research the web and return a sourced answer in your JSON shape. Choose
        `fast` for a short task or `ultra` for deeper research.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AnswersRequest'
            examples:
              fast:
                summary: Fast
                value:
                  mode: fast
                  task: Find the pricing page URL and plan names for context.dev.
                  json_format:
                    pricing_page_url: ''
                    plans:
                      - name: ''
              ultra:
                summary: Ultra
                value:
                  mode: ultra
                  task: >-
                    Compare the monthly pricing and included credits for the
                    plans on context.dev.
                  json_format:
                    plans:
                      - name: ''
                        monthly_price_usd: 0
                        included_credits: 0
                        pricing_page_url: ''
      responses:
        '200':
          description: The requested JSON shape, plus the sources used
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
            X-Context-ZDR:
              description: >-
                Present with the value true when zero data retention was
                requested and honored.
              schema:
                type: string
                enum:
                  - 'true'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AnswersResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
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
        '408':
          description: The request exceeded timeoutOpts.milliseconds.
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
          description: Request exceeded the applicable rate limit.
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
          description: >-
            Research could not gather usable evidence or produce the requested
            JSON answer.
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
        '504':
          description: The research exceeded its time limit.
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
    AnswersRequest:
      type: object
      properties:
        mode:
          type: string
          enum:
            - fast
            - ultra
          description: >-
            `fast` prioritizes speed, with extra verification for people and
            companies; `ultra` supports deeper research (default).
        task:
          type: string
          minLength: 1
          maxLength: 2000
          description: >-
            Research task. The agent selects company/profile lookups, web
            searches, or page reads. Include domains or URLs to focus the
            research.
        json_format:
          type: object
          additionalProperties: {}
          description: >-
            Example answer object, not JSON Schema. Up to 8 levels, 500 values,
            and 16000 characters; unknowns may be null.
        timeoutOpts:
          $ref: '#/components/schemas/PartialTimeout'
        tags:
          $ref: '#/components/schemas/RequestTags'
        zdr:
          type: string
          enum:
            - enabled
            - disabled
          description: >-
            `enabled` turns on zero data retention. Returns 403
            `ZDR_NOT_ENABLED` unless your organization has ZDR.
        policies:
          type: array
          items:
            type: string
          description: Access policy IDs to apply. A URL must pass every policy.
          example:
            - pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e
      required:
        - task
      additionalProperties: false
    AnswersResponse:
      type: object
      properties:
        partial:
          type: boolean
          description: >-
            True when the request deadline ended research and the answer uses
            the evidence collected so far.
        json_content:
          type: object
          additionalProperties: {}
          description: The answer, in the shape requested by json_format.
        sources:
          type: array
          items:
            type: string
          description: >-
            URLs of the pages and company/profile records read for the answer,
            followed by URLs cited in json_content.
        key_metadata:
          $ref: '#/components/schemas/KeyMetadata'
        request_id:
          $ref: '#/components/schemas/RequestId'
      required:
        - json_content
        - sources
        - request_id
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
    PartialTimeout:
      type: object
      properties:
        milliseconds:
          type: integer
          minimum: 1000
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
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        Send `Authorization: Bearer <API_KEY>`. Keys have full access unless
        restricted to scopes.

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.