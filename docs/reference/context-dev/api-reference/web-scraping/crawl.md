# Crawl a website

> Crawl a website and return page content as Markdown. Use a batch for crawls beyond 500 pages.

1 credit per pageRate limit weight: 10

See the [guide](https://docs.context.dev/crawl/overview) for examples and usage.

> [!TIP]
>
> Need to crawl more than 500 pages? Use [batches](https://docs.context.dev/crawl/async.md).


## OpenAPI

````yaml POST /web/crawl
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
  /web/crawl:
    post:
      tags:
        - Web Scraping
      summary: Crawl a website
      description: >-
        Crawl a website and return page content as Markdown. Use a batch for
        crawls beyond 500 pages.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                url:
                  type: string
                  minLength: 1
                  format: uri
                  description: Start URL, including `http://` or `https://`.
                maxPages:
                  type: integer
                  minimum: 1
                  maximum: 500
                  default: 100
                  description: Maximum pages to crawl.
                maxDepth:
                  type: integer
                  minimum: 0
                  description: >-
                    Maximum link depth from the starting URL (0 = only the
                    starting page)
                urlRegex:
                  type: string
                  maxLength: 256
                  description: >-
                    Regex pattern. Only URLs matching this pattern will be
                    followed and scraped. An automatic prefix scope in the form
                    ^<starting URL> follows a redirect of the starting page.
                  example: ^https?://[^/]+/blog/
                excludeUrlRegex:
                  type: string
                  maxLength: 256
                  description: >-
                    Regex pattern. URLs matching this pattern are never followed
                    or scraped, even when they match urlRegex. The starting URL
                    is always scraped.
                  example: /tag/|/author/
                includeLinks:
                  type: boolean
                  default: true
                  description: >-
                    Preserve hyperlinks in the Markdown output
                    (`html-conversion` only).
                includeImages:
                  type: boolean
                  default: false
                  description: >-
                    Include image references in the Markdown output
                    (`html-conversion` only).
                shortenBase64Images:
                  type: boolean
                  default: true
                  description: >-
                    Truncate base64-encoded image data in the Markdown output
                    (`html-conversion` only).
                useMainContentOnly:
                  type: boolean
                  default: false
                  description: >-
                    Extract only the main content, stripping headers, footers,
                    sidebars, and navigation
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
                    Markdown sources in order of preference: `html-conversion`
                    converts the page HTML, `markdown-direct` uses Markdown the
                    site publishes.
                followSubdomains:
                  type: boolean
                  default: false
                  description: >-
                    When true, follow links on subdomains of the starting URL's
                    domain (e.g. docs.example.com when starting from
                    example.com). www and apex are always treated as equivalent.
                pdf:
                  type: object
                  properties:
                    shouldParse:
                      type: boolean
                      default: true
                      description: >-
                        When true, PDF pages are fetched and parsed. When false,
                        PDF pages are skipped entirely (not included in results
                        and not counted as failures).
                    start:
                      type: integer
                      minimum: 1
                      description: First 1-based PDF page to parse.
                    end:
                      type: integer
                      minimum: 1
                      description: >-
                        Last PDF page to parse (1-based, inclusive). Defaults to
                        the final page. Must be >= start.
                    ocr:
                      type: boolean
                      default: false
                      description: >-
                        Read scanned PDF pages with OCR; preserve pages that
                        already have text.
                  default:
                    shouldParse: true
                    ocr: false
                  additionalProperties: false
                  description: >-
                    PDF handling. `start`/`end` limit parsing to an inclusive,
                    1-based page range.
                includeFrames:
                  type: boolean
                  default: false
                  description: >-
                    When true, the contents of iframes are rendered to Markdown
                    for each crawled page.
                includeSelectors:
                  type:
                    - array
                    - 'null'
                  items:
                    type: string
                    minLength: 1
                    maxLength: 2048
                  maxItems: 50
                  description: >-
                    Keep matching HTML subtrees before converting each page to
                    Markdown.
                excludeSelectors:
                  type:
                    - array
                    - 'null'
                  items:
                    type: string
                    minLength: 1
                    maxLength: 2048
                  maxItems: 50
                  description: >-
                    Remove matching elements after inclusions. Exclusions take
                    precedence.
                maxAgeMs:
                  type:
                    - integer
                    - 'null'
                  minimum: 0
                  maximum: 2592000000
                  default: 86400000
                  description: >-
                    Maximum cache age in milliseconds. Defaults to 1 day; `0`
                    fetches fresh.
                waitForMs:
                  type:
                    - integer
                    - 'null'
                  minimum: 0
                  maximum: 30000
                  default: 3500
                  description: >-
                    Browser wait time in milliseconds after initial page load
                    for each crawled page. Defaults to 3500 (3.5 seconds). Min:
                    0. Max: 30000 (30 seconds).
                settleAnimations:
                  type: boolean
                  default: false
                  description: >-
                    Wait briefly for CSS animations and transitions to settle
                    before reading each page.
                stopAfterMs:
                  type: integer
                  minimum: 10000
                  default: 80000
                  maximum: 110000
                  description: >-
                    Soft crawl deadline in milliseconds. Returns pages collected
                    before the next deadline check.
                timeoutOpts:
                  $ref: '#/components/schemas/PartialTimeout'
                country:
                  $ref: '#/components/schemas/BrowserCountryCode'
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
                - url
            example:
              url: https://example.com
              maxPages: 10
      responses:
        '200':
          description: Successful response
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
                        markdown:
                          type: string
                          description: >-
                            Extracted page content as Markdown (empty string on
                            failure)
                        metadata:
                          allOf:
                            - $ref: '#/components/schemas/PageMetadata'
                            - type: object
                              properties:
                                url:
                                  type: string
                                  description: The crawl URL fetched for this page.
                                title:
                                  type: string
                                  description: >-
                                    Best page title extracted from the page
                                    (empty string if unavailable).
                                crawlDepth:
                                  type: integer
                                  description: >-
                                    Depth relative to the start URL. 0 = start
                                    URL, 1 = one link away.
                                statusCode:
                                  type: integer
                                  description: HTTP status code of the response
                                success:
                                  type: boolean
                                  description: >-
                                    true if the page was fetched and parsed
                                    successfully
                              required:
                                - url
                                - title
                                - crawlDepth
                                - statusCode
                                - success
                      required:
                        - markdown
                        - metadata
                  metadata:
                    type: object
                    properties:
                      numUrls:
                        type: integer
                        description: Total number of URLs crawled
                      maxCrawlDepth:
                        type: integer
                        description: Maximum crawl depth reached during the crawl
                      numSucceeded:
                        type: integer
                        description: Number of pages successfully crawled
                      numFailed:
                        type: integer
                        description: Number of pages that failed to crawl
                      numSkipped:
                        type: integer
                        description: >-
                          Number of URLs skipped (PDFs when
                          pdf.shouldParse=false, URLs not matching urlRegex, or
                          URLs matching excludeUrlRegex)
                    required:
                      - numUrls
                      - maxCrawlDepth
                      - numSucceeded
                      - numFailed
                      - numSkipped
                  cache_metadata:
                    $ref: '#/components/schemas/CacheMetadata'
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - results
                  - metadata
                  - cache_metadata
                  - request_id
        '400':
          description: Bad request - Invalid URL or parameters
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
                      - WEBSITE_ACCESS_ERROR
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
            request. An access policy can also block the website
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
        '404':
          description: Start URL returned a 404
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
                      - NOT_FOUND
                    description: Error code indicating the start URL was not found
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - message
                  - error_code
                  - request_id
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
        '415':
          description: >-
            The start URL has an unsupported content type. Supported documents
            include PDF, Word, Excel, PowerPoint, and CSV.
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
                    description: Error message describing the unsupported content type
                  error_code:
                    type: string
                    enum:
                      - UNSUPPORTED_CONTENT
                    description: Error code indicating an unsupported content type
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - message
                  - error_code
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
    BrowserCountryCode:
      type: string
      enum:
        - ad
        - ae
        - af
        - ag
        - ai
        - al
        - am
        - ao
        - ar
        - at
        - au
        - aw
        - az
        - ba
        - bb
        - bd
        - be
        - bf
        - bg
        - bh
        - bi
        - bj
        - bm
        - bn
        - bo
        - bq
        - br
        - bs
        - bw
        - by
        - bz
        - ca
        - cd
        - cf
        - cg
        - ch
        - ci
        - cl
        - cm
        - cn
        - co
        - cr
        - cv
        - cw
        - cy
        - cz
        - de
        - dj
        - dk
        - dm
        - do
        - dz
        - ec
        - ee
        - eg
        - es
        - et
        - fi
        - fj
        - fr
        - ga
        - gb
        - gd
        - ge
        - gf
        - gg
        - gh
        - gm
        - gn
        - gp
        - gq
        - gr
        - gt
        - gu
        - gw
        - gy
        - hk
        - hn
        - hr
        - ht
        - hu
        - id
        - ie
        - il
        - im
        - in
        - iq
        - ir
        - is
        - it
        - je
        - jm
        - jo
        - jp
        - ke
        - kg
        - kh
        - kn
        - kr
        - kw
        - ky
        - kz
        - la
        - lb
        - lc
        - lk
        - lr
        - ls
        - lt
        - lu
        - lv
        - ly
        - ma
        - mc
        - md
        - me
        - mf
        - mg
        - mk
        - ml
        - mm
        - mn
        - mo
        - mq
        - mr
        - mt
        - mu
        - mv
        - mw
        - mx
        - my
        - mz
        - na
        - nc
        - ne
        - ng
        - ni
        - nl
        - 'no'
        - np
        - nz
        - om
        - pa
        - pe
        - pf
        - pg
        - ph
        - pk
        - pl
        - pr
        - ps
        - pt
        - py
        - qa
        - re
        - ro
        - rs
        - ru
        - rw
        - sa
        - sc
        - sd
        - se
        - sg
        - si
        - sk
        - sl
        - sm
        - sn
        - so
        - sr
        - ss
        - st
        - sv
        - sx
        - sy
        - sz
        - tc
        - td
        - tg
        - th
        - tj
        - tl
        - tm
        - tn
        - tr
        - tt
        - tw
        - tz
        - ua
        - ug
        - us
        - uy
        - uz
        - vc
        - ve
        - vg
        - vi
        - vn
        - ye
        - yt
        - za
        - zm
        - zw
      example: de
      description: Fetch from this country (ISO 3166-1 alpha-2).
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
    PageMetadata:
      type: object
      properties:
        sourceUrl:
          type: string
          description: Original URL requested by the caller.
        finalUrl:
          type: string
          description: >-
            Final URL scraped after redirects or scraper fallback, when known.
            Falls back to sourceUrl when unavailable.
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
            Page headings (h1–h6) in document order, extracted from the
            unfiltered document. Capped at the first 500 headings. Omitted when
            the page has none.
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
      required:
        - sourceUrl
        - finalUrl
      description: Metadata extracted from the scraped page HTML.
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