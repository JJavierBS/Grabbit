# Search people

> Find people with a natural-language query. Use `fast` for basic criteria or `ultra` for a deeper search that scores each result. Pages with no matches are free.

10 CreditsUltra: 50 CreditsAll plans

See the [guide](https://docs.context.dev/people/search.md) for examples and usage.


## OpenAPI

````yaml POST /people/search
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
  /people/search:
    post:
      tags:
        - People
      summary: Search people
      description: Find people with a natural-language query.
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
                    Describe the people to find. Up to 500 characters in `fast`
                    mode and 5000 in `ultra` mode.
                  example: VPs of sales at solar companies in California
                mode:
                  type: string
                  enum:
                    - fast
                    - ultra
                  default: fast
                  description: >-
                    `fast` matches people on basic criteria (e.g. their role,
                    location or background); `ultra` plans a deeper search,
                    judges each candidate against every criterion in the query.
                    Complex `ultra` searches can take up to 30 seconds to
                    complete, so allow for that in your client timeout.
                filters:
                  $ref: '#/components/schemas/PeopleSearchFilters'
                cursor:
                  type: string
                  maxLength: 65536
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
                query: VPs of sales at solar companies in California
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
                          type:
                            - string
                            - 'null'
                          description: Full name.
                        description:
                          type:
                            - string
                            - 'null'
                          description: What the person does.
                        profiles:
                          type: array
                          items:
                            type: string
                          description: Public professional profile URLs.
                        location:
                          type: object
                          properties:
                            country_code:
                              type:
                                - string
                                - 'null'
                              description: Country as a two-letter code, such as US or GB.
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
                          required:
                            - country_code
                            - region
                            - city
                          description: Where the person lives.
                        role:
                          type: object
                          properties:
                            title:
                              type:
                                - string
                                - 'null'
                              description: Job title.
                            seniority:
                              type:
                                - string
                                - 'null'
                              description: Seniority level.
                            functions:
                              type: array
                              items:
                                type: string
                              description: Areas of responsibility.
                            started_on:
                              type:
                                - string
                                - 'null'
                              description: Role start date (YYYY-MM-DD).
                            company:
                              type:
                                - object
                                - 'null'
                              properties:
                                name:
                                  type:
                                    - string
                                    - 'null'
                                  description: Company name.
                                domain:
                                  type:
                                    - string
                                    - 'null'
                                  description: The company’s website domain.
                              required:
                                - name
                                - domain
                              description: Current employer, when known.
                          required:
                            - title
                            - seniority
                            - functions
                            - started_on
                            - company
                          description: The person’s current role.
                        years_of_experience:
                          type:
                            - integer
                            - 'null'
                          minimum: 0
                          description: Years of professional experience.
                        is_founder:
                          type:
                            - boolean
                            - 'null'
                          description: >-
                            Whether the person is currently a founder or
                            co-founder.
                        skills:
                          type: array
                          items:
                            type: string
                          description: Professional skills.
                        schools:
                          type: array
                          items:
                            type: string
                          description: Schools attended.
                        match:
                          $ref: '#/components/schemas/PeopleSearchMatch'
                      required:
                        - name
                        - description
                        - profiles
                        - location
                        - role
                        - years_of_experience
                        - is_founder
                        - skills
                        - schools
                      description: >-
                        A person matching your search; unavailable details are
                        null or empty lists.
                      example:
                        name: Alex Morgan
                        description: Sales leader helping solar companies grow.
                        profiles:
                          - https://alexmorgan.example
                        location:
                          country_code: US
                          region: California
                          city: San Francisco
                        role:
                          title: VP of Sales
                          seniority: executive
                          functions:
                            - sales
                          started_on: '2023-06-01'
                          company:
                            name: Solstice
                            domain: solstice.example
                        years_of_experience: 12
                        is_founder: false
                        skills:
                          - Enterprise Sales
                          - Sales Leadership
                          - Renewable Energy
                        schools:
                          - University of California, Berkeley
                    maxItems: 10
                    description: Up to 10 matching people, most relevant first.
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
                  - name: Alex Morgan
                    description: Sales leader helping solar companies grow.
                    profiles:
                      - https://alexmorgan.example
                    location:
                      country_code: US
                      region: California
                      city: San Francisco
                    role:
                      title: VP of Sales
                      seniority: executive
                      functions:
                        - sales
                      started_on: '2023-06-01'
                      company:
                        name: Solstice
                        domain: solstice.example
                    years_of_experience: 12
                    is_founder: false
                    skills:
                      - Enterprise Sales
                      - Sales Leadership
                      - Renewable Energy
                    schools:
                      - University of California, Berkeley
                next_cursor: null
                request_id: 3f1c2a6e-8b4d-4c1e-9f0a-2d7b5e6c8a91
                key_metadata:
                  credits_consumed: 10
                  credits_remaining: 990
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
    PeopleSearchFilters:
      type: object
      properties:
        countries:
          type: array
          items:
            type: string
            pattern: ^[A-Z]{2}$
          description: Countries people live in as two-letter codes, such as US or GB.
        years_of_experience_min:
          type: integer
          minimum: 0
          description: Minimum years of professional experience.
        years_of_experience_max:
          type: integer
          minimum: 0
          description: Maximum years of professional experience.
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
    PeopleSearchMatch:
      type: object
      properties:
        confidence:
          type: number
          minimum: 0
          maximum: 1
          description: How well the person matches the query, from 0 to 1.
      required:
        - confidence
      description: How well the person matches the query. Only returned in `ultra` mode.
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