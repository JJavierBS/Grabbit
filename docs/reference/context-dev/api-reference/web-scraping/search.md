# Search the web

> Search the web and optionally return page content or relevant passages with each result.

From 1 credit per 10 results

See the [guide](https://docs.context.dev/search/overview) for examples and usage.


## OpenAPI

````yaml POST /web/search
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
  /web/search:
    post:
      tags:
        - Web Scraping
      summary: Search the web
      description: >-
        Search the web and optionally return page content or relevant passages
        with each result.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                  minLength: 1
                  maxLength: 500
                  description: >-
                    Search query. Accepts natural language as well as
                    Google-style search operators such as `site:`, `-site:`,
                    `inurl:`, `intitle:`, quoted phrases, and `OR`.
                numResults:
                  type: integer
                  minimum: 1
                  maximum: 100
                  default: 10
                  description: >-
                    Number of results to request and return (1–100). Defaults to
                    10.
                includeDomains:
                  type: array
                  items:
                    type: string
                    minLength: 3
                  maxItems: 100
                  description: >-
                    Allowlist — only return results from these domains. Up to
                    100 domains. Example: ["arxiv.org", "github.com"].
                excludeDomains:
                  type: array
                  items:
                    type: string
                    minLength: 3
                  maxItems: 100
                  description: >-
                    Blocklist — drop results from these domains. Up to 100
                    domains. Example: ["pinterest.com", "reddit.com"].
                freshness:
                  type: string
                  enum:
                    - last_24_hours
                    - last_week
                    - last_month
                    - last_year
                  description: Restrict results to content published within this window.
                country:
                  type: string
                  enum:
                    - af
                    - al
                    - dz
                    - as
                    - ad
                    - ao
                    - ai
                    - aq
                    - ag
                    - ar
                    - am
                    - aw
                    - au
                    - at
                    - az
                    - bs
                    - bh
                    - bd
                    - bb
                    - by
                    - be
                    - bz
                    - bj
                    - bm
                    - bt
                    - bo
                    - ba
                    - bw
                    - bv
                    - br
                    - io
                    - bn
                    - bg
                    - bf
                    - bi
                    - kh
                    - cm
                    - ca
                    - cv
                    - ky
                    - cf
                    - td
                    - cl
                    - cn
                    - cx
                    - cc
                    - co
                    - km
                    - cg
                    - cd
                    - ck
                    - cr
                    - ci
                    - hr
                    - cu
                    - cy
                    - cz
                    - dk
                    - dj
                    - dm
                    - do
                    - ec
                    - eg
                    - sv
                    - gq
                    - er
                    - ee
                    - et
                    - fk
                    - fo
                    - fj
                    - fi
                    - fr
                    - gf
                    - pf
                    - tf
                    - ga
                    - gm
                    - ge
                    - de
                    - gh
                    - gi
                    - gr
                    - gl
                    - gd
                    - gp
                    - gu
                    - gt
                    - gn
                    - gw
                    - gy
                    - ht
                    - hm
                    - va
                    - hn
                    - hk
                    - hu
                    - is
                    - in
                    - id
                    - ir
                    - iq
                    - ie
                    - il
                    - it
                    - jm
                    - jp
                    - jo
                    - kz
                    - ke
                    - ki
                    - kp
                    - kr
                    - kw
                    - kg
                    - la
                    - lv
                    - lb
                    - ls
                    - lr
                    - ly
                    - li
                    - lt
                    - lu
                    - mo
                    - mk
                    - mg
                    - mw
                    - my
                    - mv
                    - ml
                    - mt
                    - mh
                    - mq
                    - mr
                    - mu
                    - yt
                    - mx
                    - fm
                    - md
                    - mc
                    - mn
                    - ms
                    - ma
                    - mz
                    - mm
                    - na
                    - nr
                    - np
                    - nl
                    - an
                    - nc
                    - nz
                    - ni
                    - ne
                    - ng
                    - nu
                    - nf
                    - mp
                    - 'no'
                    - om
                    - pk
                    - pw
                    - ps
                    - pa
                    - pg
                    - py
                    - pe
                    - ph
                    - pn
                    - pl
                    - pt
                    - pr
                    - qa
                    - re
                    - ro
                    - ru
                    - rw
                    - sh
                    - kn
                    - lc
                    - pm
                    - vc
                    - ws
                    - sm
                    - st
                    - sa
                    - sn
                    - rs
                    - sc
                    - sl
                    - sg
                    - sk
                    - si
                    - sb
                    - so
                    - za
                    - gs
                    - es
                    - lk
                    - sd
                    - sr
                    - sj
                    - sz
                    - se
                    - ch
                    - sy
                    - tw
                    - tj
                    - tz
                    - th
                    - tl
                    - tg
                    - tk
                    - to
                    - tt
                    - tn
                    - tr
                    - tm
                    - tc
                    - tv
                    - ug
                    - ua
                    - ae
                    - gb
                    - us
                    - um
                    - uy
                    - uz
                    - vu
                    - ve
                    - vn
                    - vg
                    - vi
                    - wf
                    - eh
                    - ye
                    - zm
                    - zw
                  description: >-
                    Two-letter ISO 3166-1 alpha-2 country code to localize
                    results to a specific country (maps to Google's `gl`
                    parameter). Example: "us", "gb", "de".
                languages:
                  anyOf:
                    - type: string
                      enum:
                        - all
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
                  default: all
                  description: >-
                    Languages to return results in, as BCP 47 language codes
                    such as `en` or `de`, or "all" for any language. Defaults to
                    "all". Example: ["en", "de"].
                queryFanout:
                  type: boolean
                  description: Currently has no effect.
                markdownOptions:
                  type:
                    - object
                    - 'null'
                  properties:
                    enabled:
                      type: boolean
                      default: false
                      description: >-
                        Scrape each result to Markdown. Adds 1 credit per result
                        with Markdown.
                    includeLinks:
                      type: boolean
                      default: true
                      description: Keep hyperlinks in the Markdown.
                    includeImages:
                      type: boolean
                      default: false
                      description: Emit image references in the Markdown.
                    shortenBase64Images:
                      type: boolean
                      default: true
                      description: >-
                        Truncate inline base64 image payloads to keep responses
                        small.
                    useMainContentOnly:
                      type: boolean
                      default: false
                      description: >-
                        Strip nav, header, footer, and sidebar — keep only the
                        primary article content.
                    pdf:
                      type: object
                      properties:
                        shouldParse:
                          type: boolean
                          default: true
                          description: >-
                            Parse PDF URLs. When false, PDF results are skipped
                            with WEBSITE_ACCESS_ERROR.
                        start:
                          type: integer
                          minimum: 1
                          description: First 1-based PDF page to parse.
                        end:
                          type: integer
                          minimum: 1
                          description: >-
                            Last PDF page to parse (1-based, inclusive).
                            Defaults to the final page. Must be >= start.
                      default:
                        shouldParse: true
                      additionalProperties: false
                      description: >-
                        PDF handling. `start`/`end` limit parsing to an
                        inclusive, 1-based page range.
                    includeFrames:
                      type: boolean
                      default: false
                      description: Render iframe contents into the Markdown.
                    maxAgeMs:
                      type:
                        - integer
                        - 'null'
                      minimum: 0
                      maximum: 31536000000
                      description: >-
                        Maximum cache age in milliseconds for result page
                        content. Defaults to 180 days (15552000000 ms) when
                        Markdown is requested, or 365 days (31536000000 ms) when
                        only highlights are requested. Explicit values override
                        either default. Maximum: 365 days. Set to 0 to force a
                        fresh scrape.
                    waitForMs:
                      type:
                        - integer
                        - 'null'
                      minimum: 0
                      maximum: 30000
                      description: >-
                        Extra wait after page load before rendering, in ms
                        (0–30000). Useful for JS-heavy pages.
                    timeoutOpts:
                      $ref: '#/components/schemas/ScrapeTimeout'
                  additionalProperties: false
                  description: >-
                    Inline Markdown scraping for each result. Set `enabled:
                    true` to activate.
                highlightsOptions:
                  type:
                    - object
                    - 'null'
                  properties:
                    enabled:
                      type: boolean
                      default: false
                      description: >-
                        Return relevant passages for each result. Adds 1 credit
                        per 10 results.
                    maxCharacters:
                      type: integer
                      minimum: 100
                      maximum: 20000
                      default: 4000
                      description: Maximum combined length of passages per result.
                  additionalProperties: false
                  description: >-
                    Passages from each result page that are relevant to the
                    query. Pages are read with the `markdownOptions` settings.
                descriptionMaxCharacters:
                  type:
                    - integer
                    - 'null'
                  minimum: 0
                  default: null
                  description: >-
                    Maximum length of each result's `description`, in
                    characters.
                timeoutOpts:
                  $ref: '#/components/schemas/PartialTimeout'
                zdr:
                  type: string
                  enum:
                    - enabled
                    - disabled
                  default: disabled
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
                tags:
                  $ref: '#/components/schemas/RequestTags'
              required:
                - query
              additionalProperties: false
            example:
              query: Stripe API authentication
              numResults: 10
      responses:
        '200':
          description: Search succeeded. Results are ordered by relevance.
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
                type: object
                properties:
                  partial:
                    type: boolean
                    description: >-
                      True when timeoutOpts.behavior=return-partial returned the
                      usable results collected before the deadline. Partial
                      collections are not cached as complete results.
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        url:
                          type: string
                          description: Canonical result URL.
                        title:
                          type: string
                          description: Page title.
                        description:
                          type: string
                          description: >-
                            Snippet excerpt from the page. Empty string when the
                            search provider does not supply a snippet.
                        relevance:
                          type: string
                          enum:
                            - high
                            - medium
                            - low
                          description: Relevance to the original query.
                        markdown:
                          type: object
                          properties:
                            finalDOMState:
                              type: string
                              enum:
                                - loaded
                                - still-loading
                              description: >-
                                `loaded`, or `still-loading` when capture ended
                                before the page finished loading.
                            markdown:
                              type:
                                - string
                                - 'null'
                              description: >-
                                GFM Markdown of the page. Null unless
                                markdownOptions.enabled is true and scraping
                                succeeded.
                            code:
                              type: string
                              enum:
                                - SUCCESS
                                - NOT_REQUESTED
                                - TIMEOUT
                                - CONTENT_TOO_LARGE
                                - WEBSITE_ACCESS_ERROR
                                - WEBSITE_BLOCKED
                                - ERROR
                              description: >-
                                Per-result scrape outcome. Inspect this before
                                reading `markdown`.
                          required:
                            - markdown
                            - code
                          additionalProperties: false
                          description: Markdown scrape status and content for this result.
                        highlights:
                          type: object
                          properties:
                            highlights:
                              type:
                                - array
                                - 'null'
                              items:
                                type: string
                              description: >-
                                Passages relevant to the query, in page order.
                                Null unless highlightsOptions.enabled is true
                                and the page was read.
                            code:
                              type: string
                              enum:
                                - SUCCESS
                                - NOT_REQUESTED
                                - TIMEOUT
                                - CONTENT_TOO_LARGE
                                - WEBSITE_ACCESS_ERROR
                                - WEBSITE_BLOCKED
                                - ERROR
                              description: >-
                                Per-result highlights outcome. Inspect this
                                before reading `highlights`.
                          required:
                            - highlights
                            - code
                          additionalProperties: false
                          description: Highlights status and passages for this result.
                      required:
                        - url
                        - title
                        - description
                        - relevance
                        - markdown
                        - highlights
                  query:
                    type: string
                    description: >-
                      Echo of the original query (useful when fanout was
                      enabled).
                  cache_metadata:
                    $ref: '#/components/schemas/CacheMetadata'
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - results
                  - query
                  - cache_metadata
                  - request_id
        '400':
          description: Bad request - Invalid parameters
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
                  message:
                    type: string
                    description: Error message describing the issue
                  error_code:
                    type: string
                    enum:
                      - INPUT_VALIDATION_ERROR
                    description: Machine-readable error code.
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - message
                  - error_code
                  - request_id
        '401':
          description: Missing, invalid, or disabled API key.
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
        '408':
          description: Request timeout
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
                  message:
                    type: string
                    description: Timeout error message
                  error_code:
                    type: string
                    enum:
                      - REQUEST_TIMEOUT
                    description: Error code indicating request timeout
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - request_id
        '429':
          $ref: '#/components/responses/RateLimited'
        '500':
          description: Internal server error
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
                  message:
                    type: string
                    description: Human-readable error message.
                  error_code:
                    type: string
                    enum:
                      - INTERNAL_ERROR
                    description: Error code indicating internal server error
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - request_id
      security:
        - bearerAuth: []
components:
  schemas:
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