# Search companies

> Find companies by name or description. Use `fast` for quick results or `ultra` for a more thorough search that checks each result. Pages with no matches are free.

2 CreditsUltra: 10 CreditsAll plans

See the [guide](https://docs.context.dev/companies/search.md) for examples and usage.


## OpenAPI

````yaml POST /company/search
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
  /company/search:
    post:
      tags:
        - Company
      summary: Search companies
      description: Find companies with a natural-language query.
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
                  maxLength: 5000
                  description: >-
                    Describe the companies to find. Up to 500 characters in
                    `fast` mode and 5000 in `ultra` mode.
                  example: Solar startups in California that raised a Series B
                mode:
                  type: string
                  enum:
                    - fast
                    - ultra
                  default: fast
                  description: >-
                    `fast` returns results in about two seconds; `ultra`
                    searches more thoroughly and checks every result against
                    each criterion in the query. `ultra` can take up to 20
                    seconds, so allow for that in your client timeout.
                filters:
                  $ref: '#/components/schemas/CompanySearchFilters'
                cursor:
                  type: string
                  maxLength: 64
                  description: >-
                    Use next_cursor with the same query, mode and filters to
                    fetch the next page.
                zdr:
                  type: string
                  enum:
                    - enabled
                    - disabled
                  description: >-
                    `enabled` turns on zero data retention. Returns 403
                    `ZDR_NOT_ENABLED` unless your organization has ZDR.
                tags:
                  $ref: '#/components/schemas/RequestTags'
              required:
                - query
              additionalProperties: false
              example:
                query: Solar startups in California that raised a Series B
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
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        name:
                          type: string
                          description: Company name.
                        domain:
                          type: string
                          description: The company's website domain.
                        socials:
                          type: object
                          properties:
                            linkedin:
                              type:
                                - string
                                - 'null'
                              description: >-
                                The company's LinkedIn page URL; null when
                                unknown.
                            x:
                              type:
                                - string
                                - 'null'
                              description: >-
                                The company's X (Twitter) profile URL; null when
                                unknown.
                            instagram:
                              type:
                                - string
                                - 'null'
                              description: >-
                                The company's Instagram profile URL; null when
                                unknown.
                            facebook:
                              type:
                                - string
                                - 'null'
                              description: >-
                                The company's Facebook page URL; null when
                                unknown.
                            youtube:
                              type:
                                - string
                                - 'null'
                              description: >-
                                The company's YouTube channel URL; null when
                                unknown.
                            github:
                              type:
                                - string
                                - 'null'
                              description: >-
                                The company's GitHub organization URL; null when
                                unknown.
                            crunchbase:
                              type:
                                - string
                                - 'null'
                              description: >-
                                The company's Crunchbase profile URL; null when
                                unknown.
                            wellfound:
                              type:
                                - string
                                - 'null'
                              description: >-
                                The company's Wellfound profile URL; null when
                                unknown.
                          description: The company's social profiles.
                        description:
                          type:
                            - string
                            - 'null'
                          description: What the company does.
                        organization_type:
                          type:
                            - string
                            - 'null'
                          description: >-
                            Company type, such as public_company or
                            privately_held.
                        operating_status:
                          type:
                            - string
                            - 'null'
                          description: >-
                            Operating status, such as active, acquired or
                            closed.
                        stock_symbols:
                          type: array
                          items:
                            type: string
                          description: Known stock listings and ticker symbols.
                        revenue:
                          type: object
                          properties:
                            min_usd:
                              type:
                                - integer
                                - 'null'
                              description: Lower estimate of annual revenue in US dollars.
                            max_usd:
                              type:
                                - integer
                                - 'null'
                              description: Upper estimate of annual revenue in US dollars.
                          description: Estimated annual revenue in US dollars.
                        industries:
                          type: array
                          items:
                            type: string
                          description: Industries the company operates in.
                        founded_year:
                          type:
                            - integer
                            - 'null'
                          description: Year the company was founded.
                        headquarters:
                          type: object
                          properties:
                            country_code:
                              type:
                                - string
                                - 'null'
                              description: ISO 3166-1 alpha-2 country code.
                            region:
                              type:
                                - string
                                - 'null'
                              description: State or region.
                            city:
                              type:
                                - string
                                - 'null'
                              description: City.
                            street_address:
                              type:
                                - string
                                - 'null'
                              description: Street address.
                            postal_code:
                              type:
                                - string
                                - 'null'
                              description: Postal code.
                          description: Where the company is headquartered.
                        employees:
                          type: object
                          properties:
                            count:
                              type:
                                - integer
                                - 'null'
                              description: Employee count, when known.
                            min:
                              type:
                                - integer
                                - 'null'
                              description: Lower bound of the headcount range.
                            max:
                              type:
                                - integer
                                - 'null'
                              description: >-
                                Upper headcount bound; null for open-ended
                                ranges.
                          description: How many people the company employs.
                        funding:
                          type: object
                          properties:
                            total_usd:
                              type:
                                - integer
                                - 'null'
                              description: Total disclosed funding in US dollars.
                            round_count:
                              type: integer
                              description: Number of known funding rounds.
                            latest_round:
                              type:
                                - object
                                - 'null'
                              properties:
                                type:
                                  type: string
                                  description: Round type, such as seed or series_b.
                                date:
                                  type: string
                                  description: Announcement date (YYYY-MM-DD).
                                amount_usd:
                                  type:
                                    - integer
                                    - 'null'
                                  description: Round size in US dollars, when disclosed.
                              required:
                                - type
                                - date
                              description: >-
                                The most recent known funding round; null when
                                none is known.
                            stage:
                              type:
                                - string
                                - 'null'
                              description: Current funding stage, when known.
                            rounds:
                              type: array
                              items:
                                type: object
                                properties:
                                  type:
                                    type: string
                                    description: Round type, such as seed or series_b.
                                  date:
                                    type: string
                                    description: Announcement date (YYYY-MM-DD).
                                  amount_usd:
                                    type:
                                      - integer
                                      - 'null'
                                    description: Round size in US dollars, when disclosed.
                                  phase:
                                    type:
                                      - string
                                      - 'null'
                                    enum:
                                      - initial
                                      - extension
                                      - null
                                    description: >-
                                      Initial financing or an extension, when
                                      known.
                                required:
                                  - type
                                  - date
                              description: >-
                                Known historical rounds; unavailable amounts are
                                null.
                          required:
                            - round_count
                            - rounds
                          description: Known funding history.
                      required:
                        - name
                        - domain
                        - socials
                        - stock_symbols
                        - revenue
                        - industries
                        - headquarters
                        - employees
                        - funding
                      example:
                        name: Solstice
                        domain: solstice.example
                        socials:
                          linkedin: https://www.linkedin.com/company/solstice-example
                          x: https://x.com/solstice_example
                          instagram: null
                          facebook: null
                          youtube: null
                          github: null
                          crunchbase: >-
                            https://www.crunchbase.com/organization/solstice-example
                          wellfound: null
                        description: >-
                          Software for designing and managing solar
                          installations.
                        organization_type: privately_held
                        operating_status: active
                        stock_symbols: []
                        revenue:
                          min_usd: null
                          max_usd: null
                        industries:
                          - Renewable Energy
                        founded_year: 2018
                        headquarters:
                          country_code: US
                          region: California
                          city: San Francisco
                          street_address: null
                          postal_code: null
                        employees:
                          count: null
                          min: 51
                          max: 200
                        funding:
                          stage: series_b
                          total_usd: 40000000
                          round_count: 3
                          latest_round:
                            type: series_b
                            date: '2026-03-02'
                            amount_usd: 25000000
                          rounds:
                            - type: series_b
                              date: '2026-03-02'
                              amount_usd: 25000000
                              phase: initial
                    maxItems: 10
                    description: >-
                      Up to 10 matching companies, most relevant first by
                      default.
                  next_cursor:
                    type:
                      - string
                      - 'null'
                    description: >-
                      Pass as cursor to fetch the next page; null when there are
                      no more results.
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - results
                  - request_id
              example:
                results:
                  - name: Solstice
                    domain: solstice.example
                    socials:
                      linkedin: https://www.linkedin.com/company/solstice-example
                      x: https://x.com/solstice_example
                      instagram: null
                      facebook: null
                      youtube: null
                      github: null
                      crunchbase: https://www.crunchbase.com/organization/solstice-example
                      wellfound: null
                    description: Software for designing and managing solar installations.
                    organization_type: privately_held
                    operating_status: active
                    stock_symbols: []
                    revenue:
                      min_usd: null
                      max_usd: null
                    industries:
                      - Renewable Energy
                    founded_year: 2018
                    headquarters:
                      country_code: US
                      region: California
                      city: San Francisco
                      street_address: null
                      postal_code: null
                    employees:
                      count: null
                      min: 51
                      max: 200
                    funding:
                      stage: series_b
                      total_usd: 40000000
                      round_count: 3
                      latest_round:
                        type: series_b
                        date: '2026-03-02'
                        amount_usd: 25000000
                      rounds:
                        - type: series_b
                          date: '2026-03-02'
                          amount_usd: 25000000
                          phase: initial
                next_cursor: null
                request_id: 3f1c2a6e-8b4d-4c1e-9f0a-2d7b5e6c8a91
                key_metadata:
                  credits_consumed: 2
                  credits_remaining: 998
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
                      - INPUT_VALIDATION_ERROR
                    description: Machine-readable error code.
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
    CompanySearchFilters:
      type: object
      properties:
        countries:
          type: array
          items:
            type: string
            pattern: ^[A-Z]{2}$
          description: Headquarters countries as two-letter codes, such as US or GB.
        employees_min:
          type: integer
          minimum: 0
          description: Minimum headcount; includes overlapping employee ranges.
        employees_max:
          type: integer
          minimum: 0
          description: Maximum headcount; includes overlapping employee ranges.
      additionalProperties: false
      description: Additional constraints every result must match.
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