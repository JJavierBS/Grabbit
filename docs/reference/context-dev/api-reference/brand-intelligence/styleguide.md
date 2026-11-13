# Extract a styleguide

> Extract colors, typography, spacing, and component styles from a website.

10 credits

See the [guide](https://docs.context.dev/brand/styleguide.md) for examples and usage.


## OpenAPI

````yaml GET /web/styleguide
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
  /web/styleguide:
    get:
      tags:
        - Web Extraction
      summary: Extract a styleguide
      description: >-
        Extract colors, typography, spacing, and component styles from a
        website.
      parameters:
        - schema:
            type: string
            minLength: 3
            description: >-
              Domain name to extract styleguide from (e.g., 'example.com',
              'google.com'). The domain will be automatically normalized and
              validated. You must provide either 'domain' or 'directUrl', but
              not both.
          required: false
          description: >-
            Domain name to extract styleguide from (e.g., 'example.com',
            'google.com'). The domain will be automatically normalized and
            validated. You must provide either 'domain' or 'directUrl', but not
            both.
          name: domain
          in: query
        - schema:
            type: string
            format: uri
            description: >-
              Exact URL to inspect. Provide either `domain` or `directUrl`, not
              both.
          required: false
          description: >-
            Exact URL to inspect. Provide either `domain` or `directUrl`, not
            both.
          name: directUrl
          in: query
        - schema:
            type:
              - integer
              - 'null'
            default: 7776000000
            description: >-
              Maximum age of cached brand data in ms. Defaults to 3 months;
              clamped to 0–1 year. `0` refreshes.
          required: false
          description: >-
            Maximum age of cached brand data in ms. Defaults to 3 months;
            clamped to 0–1 year. `0` refreshes.
          name: maxAgeMs
          in: query
        - schema:
            $ref: '#/components/schemas/ScrapeTimeout'
          required: false
          description: Request deadline and what to return when it passes.
          style: deepObject
          explode: true
          name: timeoutOpts
          in: query
        - schema:
            type: string
            enum:
              - light
              - dark
            description: >-
              Optional browser color scheme to emulate for websites that respond
              to prefers-color-scheme. This value is part of the styleguide
              cache key.
          required: false
          description: >-
            Optional browser color scheme to emulate for websites that respond
            to prefers-color-scheme. This value is part of the styleguide cache
            key.
          name: colorScheme
          in: query
        - schema:
            type: string
            enum:
              - enabled
              - disabled
            description: >-
              `enabled` disables request logs and traces and omits request and
              response content from usage logs. Brand data and hosted assets may
              still be stored. Returns 403 `ZDR_NOT_ENABLED` unless your
              organization has ZDR.
          required: false
          description: >-
            `enabled` disables request logs and traces and omits request and
            response content from usage logs. Brand data and hosted assets may
            still be stored. Returns 403 `ZDR_NOT_ENABLED` unless your
            organization has ZDR.
          name: zdr
          in: query
        - $ref: '#/components/parameters/AccessPolicies'
        - $ref: '#/components/parameters/RequestTags'
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
                Present with the value true when zdr=enabled suppressed logs and
                traces. Brand data and hosted assets may still be stored.
              schema:
                type: string
                enum:
                  - 'true'
          content:
            application/json:
              schema:
                type: object
                properties:
                  finalDOMState:
                    type: string
                    enum:
                      - loaded
                      - still-loading
                    description: >-
                      `loaded`, or `still-loading` when capture ended before the
                      page finished loading.
                  status:
                    type: string
                    description: Always `ok` on success.
                  domain:
                    type: string
                    description: The normalized domain that was processed
                  styleguide:
                    type: object
                    properties:
                      mode:
                        type: string
                        enum:
                          - light
                          - dark
                        description: The primary color mode of the website design
                      colors:
                        type: object
                        properties:
                          accent:
                            type: string
                            description: Accent color (hex format)
                          background:
                            type: string
                            description: Background color (hex format)
                          text:
                            type: string
                            description: Text color (hex format)
                        required:
                          - accent
                          - background
                          - text
                        description: Primary colors used on the website
                      typography:
                        type: object
                        properties:
                          headings:
                            type: object
                            properties:
                              h1:
                                type: object
                                properties:
                                  fontFamily:
                                    type: string
                                    description: First font in the stack.
                                  fontFallbacks:
                                    type: array
                                    items:
                                      type: string
                                    description: >-
                                      Full ordered font list from resolved
                                      computed font-family
                                  fontSize:
                                    type: string
                                  fontWeight:
                                    type: number
                                  lineHeight:
                                    type: string
                                  letterSpacing:
                                    type: string
                                required:
                                  - fontFamily
                                  - fontFallbacks
                                  - fontSize
                                  - fontWeight
                                  - lineHeight
                                  - letterSpacing
                              h2:
                                type: object
                                properties:
                                  fontFamily:
                                    type: string
                                    description: First font in the stack.
                                  fontFallbacks:
                                    type: array
                                    items:
                                      type: string
                                    description: >-
                                      Full ordered font list from resolved
                                      computed font-family
                                  fontSize:
                                    type: string
                                  fontWeight:
                                    type: number
                                  lineHeight:
                                    type: string
                                  letterSpacing:
                                    type: string
                                required:
                                  - fontFamily
                                  - fontFallbacks
                                  - fontSize
                                  - fontWeight
                                  - lineHeight
                                  - letterSpacing
                              h3:
                                type: object
                                properties:
                                  fontFamily:
                                    type: string
                                    description: First font in the stack.
                                  fontFallbacks:
                                    type: array
                                    items:
                                      type: string
                                    description: >-
                                      Full ordered font list from resolved
                                      computed font-family
                                  fontSize:
                                    type: string
                                  fontWeight:
                                    type: number
                                  lineHeight:
                                    type: string
                                  letterSpacing:
                                    type: string
                                required:
                                  - fontFamily
                                  - fontFallbacks
                                  - fontSize
                                  - fontWeight
                                  - lineHeight
                                  - letterSpacing
                              h4:
                                type: object
                                properties:
                                  fontFamily:
                                    type: string
                                    description: First font in the stack.
                                  fontFallbacks:
                                    type: array
                                    items:
                                      type: string
                                    description: >-
                                      Full ordered font list from resolved
                                      computed font-family
                                  fontSize:
                                    type: string
                                  fontWeight:
                                    type: number
                                  lineHeight:
                                    type: string
                                  letterSpacing:
                                    type: string
                                required:
                                  - fontFamily
                                  - fontFallbacks
                                  - fontSize
                                  - fontWeight
                                  - lineHeight
                                  - letterSpacing
                            description: Heading styles
                          p:
                            type: object
                            properties:
                              fontFamily:
                                type: string
                                description: First font in the stack.
                              fontFallbacks:
                                type: array
                                items:
                                  type: string
                                description: >-
                                  Full ordered font list from resolved computed
                                  font-family
                              fontSize:
                                type: string
                              fontWeight:
                                type: number
                              lineHeight:
                                type: string
                              letterSpacing:
                                type: string
                            required:
                              - fontFamily
                              - fontFallbacks
                              - fontSize
                              - fontWeight
                              - lineHeight
                              - letterSpacing
                        required:
                          - headings
                        description: Typography styles used on the website
                      elementSpacing:
                        type: object
                        properties:
                          xs:
                            type: string
                          sm:
                            type: string
                          md:
                            type: string
                          lg:
                            type: string
                          xl:
                            type: string
                        required:
                          - xs
                          - sm
                          - md
                          - lg
                          - xl
                        description: Spacing system used on the website
                      shadows:
                        type: object
                        properties:
                          sm:
                            type: string
                          md:
                            type: string
                          lg:
                            type: string
                          xl:
                            type: string
                          inner:
                            type: string
                        required:
                          - sm
                          - md
                          - lg
                          - xl
                          - inner
                        description: Shadow styles used on the website
                      fontLinks:
                        type: object
                        additionalProperties:
                          type: object
                          properties:
                            type:
                              type: string
                              enum:
                                - google
                                - custom
                            files:
                              type: object
                              additionalProperties:
                                type: string
                              description: >-
                                Deprecated upright font lookup keyed by weight
                                string. A variable font can map several standard
                                weight keys to the same URL; faces retains its
                                actual weight range.
                              deprecated: true
                            faces:
                              type: array
                              items:
                                type: object
                                properties:
                                  url:
                                    type: string
                                    description: >-
                                      Preferred font file URL or inline font
                                      data URL.
                                  style:
                                    type: string
                                    description: >-
                                      CSS font-style descriptor: normal, italic,
                                      or oblique, including an optional oblique
                                      angle or angle range (e.g. oblique 10deg
                                      20deg).
                                  weight:
                                    type: string
                                    description: >-
                                      CSS font-weight descriptor. A variable
                                      font file can have a range such as "300
                                      500", covering intermediate weights
                                      without separate files.
                                  width:
                                    type: string
                                    description: CSS font-width or font-stretch descriptor.
                                  unicodeRange:
                                    type: string
                                    description: CSS unicode-range descriptor.
                                required:
                                  - url
                                  - style
                                  - weight
                              description: >-
                                Discovered font faces, including style, weight,
                                and distinct Unicode subsets.
                            category:
                              type: string
                              description: >-
                                Google Fonts category when type is google (e.g.
                                sans-serif, serif, monospace, display,
                                handwriting). Omitted for custom fonts when
                                unknown.
                            displayName:
                              type: string
                              description: >-
                                Human-readable family name. For custom fonts,
                                derived from the fontLinks key; for Google
                                fonts, the canonical Google Fonts family name.
                          required:
                            - type
                          examples:
                            - type: custom
                              files:
                                '300': https://example.com/variable.woff2
                                '400': https://example.com/variable.woff2
                                '500': https://example.com/variable.woff2
                              faces:
                                - url: https://example.com/variable.woff2
                                  style: normal
                                  weight: 300 500
                        description: >-
                          Font assets keyed by family name as it appears in
                          fontFamily/fontFallbacks (non-generic names only).
                          Match font style and weight against faces to select a
                          file URL.
                      components:
                        type: object
                        properties:
                          button:
                            type: object
                            properties:
                              primary:
                                type: object
                                properties:
                                  backgroundColor:
                                    type: string
                                  color:
                                    type: string
                                  borderColor:
                                    type: string
                                    description: >-
                                      Border color as CSS hex (#RRGGBB or
                                      #RRGGBBAA when computed border-color has
                                      alpha)
                                  borderRadius:
                                    type: string
                                  borderWidth:
                                    type: string
                                  borderStyle:
                                    type: string
                                  padding:
                                    type: string
                                  minWidth:
                                    type: string
                                    description: Minimum width (usually px).
                                  minHeight:
                                    type: string
                                    description: >-
                                      Sampled minimum height of the button box
                                      (typically px)
                                  fontSize:
                                    type: string
                                  fontWeight:
                                    type: number
                                  fontFamily:
                                    type: string
                                    description: >-
                                      Primary button typeface (first in
                                      fontFallbacks)
                                  fontFallbacks:
                                    type: array
                                    items:
                                      type: string
                                    description: >-
                                      Full ordered font list from computed
                                      font-family
                                  textDecoration:
                                    type: string
                                  textDecorationColor:
                                    type: string
                                    description: >-
                                      Hex color of the underline when it differs
                                      from the text color
                                  boxShadow:
                                    type: string
                                    description: >-
                                      Computed box-shadow (comma-separated
                                      layers when present)
                                  css:
                                    type: string
                                    description: >-
                                      Ready-to-use CSS declaration block for
                                      this component style
                                required:
                                  - backgroundColor
                                  - color
                                  - borderColor
                                  - borderRadius
                                  - borderWidth
                                  - borderStyle
                                  - padding
                                  - minWidth
                                  - minHeight
                                  - fontSize
                                  - fontWeight
                                  - textDecoration
                                  - boxShadow
                                  - css
                              secondary:
                                type: object
                                properties:
                                  backgroundColor:
                                    type: string
                                  color:
                                    type: string
                                  borderColor:
                                    type: string
                                    description: >-
                                      Border color as CSS hex (#RRGGBB or
                                      #RRGGBBAA when computed border-color has
                                      alpha)
                                  borderRadius:
                                    type: string
                                  borderWidth:
                                    type: string
                                  borderStyle:
                                    type: string
                                  padding:
                                    type: string
                                  minWidth:
                                    type: string
                                    description: Minimum width (usually px).
                                  minHeight:
                                    type: string
                                    description: >-
                                      Sampled minimum height of the button box
                                      (typically px)
                                  fontSize:
                                    type: string
                                  fontWeight:
                                    type: number
                                  fontFamily:
                                    type: string
                                    description: >-
                                      Primary button typeface (first in
                                      fontFallbacks)
                                  fontFallbacks:
                                    type: array
                                    items:
                                      type: string
                                    description: >-
                                      Full ordered font list from computed
                                      font-family
                                  textDecoration:
                                    type: string
                                  textDecorationColor:
                                    type: string
                                    description: >-
                                      Hex color of the underline when it differs
                                      from the text color
                                  boxShadow:
                                    type: string
                                    description: >-
                                      Computed box-shadow (comma-separated
                                      layers when present)
                                  css:
                                    type: string
                                    description: >-
                                      Ready-to-use CSS declaration block for
                                      this component style
                                required:
                                  - backgroundColor
                                  - color
                                  - borderColor
                                  - borderRadius
                                  - borderWidth
                                  - borderStyle
                                  - padding
                                  - minWidth
                                  - minHeight
                                  - fontSize
                                  - fontWeight
                                  - textDecoration
                                  - boxShadow
                                  - css
                              link:
                                type: object
                                properties:
                                  backgroundColor:
                                    type: string
                                  color:
                                    type: string
                                  borderColor:
                                    type: string
                                    description: >-
                                      Border color as CSS hex (#RRGGBB or
                                      #RRGGBBAA when computed border-color has
                                      alpha)
                                  borderRadius:
                                    type: string
                                  borderWidth:
                                    type: string
                                  borderStyle:
                                    type: string
                                  padding:
                                    type: string
                                  minWidth:
                                    type: string
                                    description: Minimum width (usually px).
                                  minHeight:
                                    type: string
                                    description: >-
                                      Sampled minimum height of the button box
                                      (typically px)
                                  fontSize:
                                    type: string
                                  fontWeight:
                                    type: number
                                  fontFamily:
                                    type: string
                                    description: >-
                                      Primary button typeface (first in
                                      fontFallbacks)
                                  fontFallbacks:
                                    type: array
                                    items:
                                      type: string
                                    description: >-
                                      Full ordered font list from computed
                                      font-family
                                  textDecoration:
                                    type: string
                                  textDecorationColor:
                                    type: string
                                    description: >-
                                      Hex color of the underline when it differs
                                      from the text color
                                  boxShadow:
                                    type: string
                                    description: >-
                                      Computed box-shadow (comma-separated
                                      layers when present)
                                  css:
                                    type: string
                                    description: >-
                                      Ready-to-use CSS declaration block for
                                      this component style
                                required:
                                  - backgroundColor
                                  - color
                                  - borderColor
                                  - borderRadius
                                  - borderWidth
                                  - borderStyle
                                  - padding
                                  - minWidth
                                  - minHeight
                                  - fontSize
                                  - fontWeight
                                  - textDecoration
                                  - boxShadow
                                  - css
                            description: Button component styles
                          card:
                            type: object
                            properties:
                              backgroundColor:
                                type: string
                              borderColor:
                                type: string
                                description: >-
                                  Border color as CSS hex (#RRGGBB or #RRGGBBAA
                                  when computed border-color has alpha)
                              borderRadius:
                                type: string
                              borderWidth:
                                type: string
                              borderStyle:
                                type: string
                              padding:
                                type: string
                              boxShadow:
                                type: string
                              textColor:
                                type: string
                              css:
                                type: string
                                description: >-
                                  Ready-to-use CSS declaration block for this
                                  component style
                            required:
                              - backgroundColor
                              - borderColor
                              - borderRadius
                              - borderWidth
                              - borderStyle
                              - padding
                              - boxShadow
                              - textColor
                              - css
                            description: Card component style
                        required:
                          - button
                        description: UI component styles
                    required:
                      - mode
                      - colors
                      - typography
                      - elementSpacing
                      - shadows
                      - fontLinks
                      - components
                    description: Comprehensive styleguide data extracted from the website
                  code:
                    type: integer
                    description: HTTP status code
                  cache_metadata:
                    $ref: '#/components/schemas/CacheMetadata'
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - cache_metadata
                  - request_id
        '400':
          description: Bad Request
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
                Present with the value true when zdr=enabled suppressed logs and
                traces. Brand data and hosted assets may still be stored.
              schema:
                type: string
                enum:
                  - 'true'
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
                      - VALID
                      - NOT_FOUND
                      - FORBIDDEN
                      - USAGE_EXCEEDED
                      - RATE_LIMITED
                      - UNAUTHORIZED
                      - DISABLED
                      - INSUFFICIENT_PERMISSIONS
                      - TIMEOUT_EXCEEDS_MAXIMUM
                      - WEBSITE_ACCESS_ERROR
                      - WEBSITE_BLOCKED
                      - WEBSITE_NOT_FOUND
                      - INPUT_VALIDATION_ERROR
                    description: >-
                      Machine-readable error code, such as `WEBSITE_BLOCKED` or
                      `WEBSITE_NOT_FOUND`.
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - request_id
        '401':
          description: Missing or invalid API key.
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
                  error_code:
                    type: string
                    enum:
                      - INTERNAL_ERROR
                      - VALID
                      - NOT_FOUND
                      - FORBIDDEN
                      - USAGE_EXCEEDED
                      - RATE_LIMITED
                      - UNAUTHORIZED
                      - DISABLED
                      - INSUFFICIENT_PERMISSIONS
                      - TIMEOUT_EXCEEDS_MAXIMUM
                      - WEBSITE_ACCESS_ERROR
                      - INPUT_VALIDATION_ERROR
                    description: Machine-readable error code.
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - request_id
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
          description: An access policy blocks this website (`ACCESS_POLICY_DENIED`).
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
        '408':
          description: Request Timeout
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
  parameters:
    AccessPolicies:
      name: policies
      in: query
      required: false
      style: form
      explode: false
      schema:
        type: array
        items:
          type: string
      description: >-
        Comma-separated access policy IDs to apply. A URL must pass every
        policy.
      example: pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e
    RequestTags:
      name: tags
      in: query
      required: false
      style: form
      explode: false
      schema:
        $ref: '#/components/schemas/RequestTags'
      description: >-
        Comma-separated labels for filtering usage, e.g.
        `production,team-alpha`.
      example: production,team-alpha
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