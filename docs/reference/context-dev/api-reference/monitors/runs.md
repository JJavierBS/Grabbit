# List monitor runs

> List a monitor’s runs, newest first.

0 credits

Requires [`monitors:read` permission](https://docs.context.dev/account/api-keys). See the [guide](https://docs.context.dev/monitors/runs-and-changes.md) for examples and usage.


## OpenAPI

````yaml GET /monitors/{monitor_id}/runs
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
  /monitors/{monitor_id}/runs:
    get:
      tags:
        - Monitors
      summary: List monitor runs
      description: List a monitor’s runs, newest first.
      operationId: listMonitorRuns
      parameters:
        - schema:
            type: string
            description: ID of the monitor.
            example: mon_123
          required: true
          description: ID of the monitor.
          name: monitor_id
          in: path
        - schema:
            allOf:
              - $ref: '#/components/schemas/MonitorsRunStatus'
              - description: Filter runs by lifecycle status.
          required: false
          description: Filter runs by lifecycle status.
          name: status
          in: query
        - schema:
            type: integer
            minimum: 1
            maximum: 100
            description: >-
              Maximum number of items to return per page (1-100). Defaults to
              25.
          required: false
          description: Maximum number of items to return per page (1-100). Defaults to 25.
          name: limit
          in: query
        - schema:
            type: string
            description: Opaque pagination cursor from a previous response.
          required: false
          description: Opaque pagination cursor from a previous response.
          name: cursor
          in: query
      responses:
        '200':
          description: A paginated list of runs for the monitor
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
                $ref: '#/components/schemas/MonitorsListRunsResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/MonitorsUnauthorized'
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
          $ref: '#/components/responses/MonitorsNotFound'
        '429':
          $ref: '#/components/responses/RateLimited'
      security:
        - bearerAuth: []
components:
  schemas:
    MonitorsRunStatus:
      type: string
      enum:
        - queued
        - running
        - completed
        - failed
        - skipped
      description: >-
        Lifecycle status of a run. `skipped` runs never executed — see
        `skip_reason` (insufficient credits, monitor paused, or superseded by a
        concurrent run).
    MonitorsListRunsResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/MonitorsRun'
        has_more:
          type: boolean
        next_cursor:
          type:
            - string
            - 'null'
        key_metadata:
          $ref: '#/components/schemas/KeyMetadata'
        request_id:
          $ref: '#/components/schemas/RequestId'
      required:
        - data
        - has_more
        - next_cursor
        - request_id
      additionalProperties: false
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
    MonitorsRun:
      type: object
      properties:
        webhook_delivery_ids:
          type: array
          items:
            type: string
          description: Webhook delivery IDs for this run.
        id:
          type: string
          example: run_123
        monitor_id:
          type: string
          example: mon_123
        status:
          $ref: '#/components/schemas/MonitorsRunStatus'
        run_type:
          type: string
          enum:
            - baseline
            - scheduled
          description: A baseline run follows creation or a target or detection change.
        target_type:
          $ref: '#/components/schemas/MonitorsTargetType'
        change_detection_type:
          $ref: '#/components/schemas/MonitorsChangeDetectionType'
        started_at:
          type:
            - string
            - 'null'
          format: date-time
        completed_at:
          type:
            - string
            - 'null'
          format: date-time
        change_detected:
          type: boolean
          example: true
        change_id:
          type:
            - string
            - 'null'
          example: chg_123
        baseline_created:
          type: boolean
          description: >-
            True when this run established the monitor's initial baseline;
            baseline runs perform no change detection.
        credits_charged:
          type: integer
          minimum: 0
          description: Credits charged for this run (0 for skipped/failed runs).
          example: 1
        skip_reason:
          type:
            - string
            - 'null'
          enum:
            - insufficient_credits
            - monitor_paused
            - superseded
            - null
          description: Why a skipped run never executed; null unless status is `skipped`.
        error:
          $ref: '#/components/schemas/MonitorsNullableRunError'
        webhook_delivery:
          $ref: '#/components/schemas/MonitorsWebhookDelivery'
          deprecated: true
          description: Deprecated. Use `webhook_deliveries` for all attempts.
        webhook_deliveries:
          type: array
          items:
            $ref: '#/components/schemas/MonitorsWebhookDelivery'
          description: >-
            All webhook deliveries attempted by this run — one per subscribed
            event that fired. Omitted when no webhook was attempted, including
            runs created before event selection was added.
      required:
        - id
        - monitor_id
        - status
        - run_type
        - target_type
        - change_detection_type
        - change_detected
        - baseline_created
        - credits_charged
      additionalProperties: false
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
    MonitorsTargetType:
      type: string
      enum:
        - page
        - sitemap
        - extract
        - search
    MonitorsChangeDetectionType:
      type: string
      enum:
        - exact
        - semantic
    MonitorsNullableRunError:
      anyOf:
        - allOf:
            - $ref: '#/components/schemas/MonitorsRunError'
        - type: 'null'
    MonitorsWebhookDelivery:
      type: object
      properties:
        delivery_id:
          type: string
          description: Delivery ID for status checks and retries, when available.
        event_id:
          type: string
          description: Identifier sent in the X-Context-Id header.
          example: evt_123
        event:
          type: string
          enum:
            - change.detected
            - run.completed
          description: >-
            The event this delivery carried. Deliveries recorded before event
            selection existed report change.detected.
        status:
          type: string
          enum:
            - delivered
            - rejected
            - failed
            - skipped_unsafe_url
          description: >-
            Outcome of the delivery attempt. Any 2xx response counts as
            delivered.
        http_status:
          type:
            - integer
            - 'null'
          minimum: 100
          maximum: 599
          description: >-
            The endpoint's final HTTP response status, or null when no response
            was received.
          example: 200
        attempted_at:
          type: string
          format: date-time
        error:
          $ref: '#/components/schemas/MonitorsNullableRunError'
      required:
        - event_id
        - event
        - status
        - http_status
        - attempted_at
        - error
      additionalProperties: false
      x-stainless-model: monitors.webhook_delivery
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
    MonitorsNotFound:
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