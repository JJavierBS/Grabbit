# Auto-complete Brand

> Find up to 10 brands by name or domain, ordered by popularity. Use the returned domain to retrieve a full brand profile.

1 creditFree on Pro, Growth, and Scale

See the [guide](https://docs.context.dev/brand/search.md) for examples and usage.


## OpenAPI

````yaml GET /brand/search
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
  /brand/search:
    get:
      tags:
        - Brand Intelligence
      summary: Auto-complete Brand
      description: >-
        Find up to 10 brands by name or domain, ordered by popularity.
        Optionally filter by country and primary language; both filters must
        match when provided together. Results include description, country, and
        language when available. Use the returned domain to retrieve a full
        brand profile.
      parameters:
        - schema:
            type: string
            minLength: 1
            maxLength: 100
            description: >-
              Search term, matched against the fields selected by queryBy (e.g.
              'stripe', 'stripe.com', 'stri').
          required: true
          description: >-
            Search term, matched against the fields selected by queryBy (e.g.
            'stripe', 'stripe.com', 'stri').
          name: query
          in: query
        - schema:
            type: string
            enum:
              - AD
              - AE
              - AF
              - AG
              - AI
              - AL
              - AM
              - AO
              - AQ
              - AR
              - AS
              - AT
              - AU
              - AW
              - AX
              - AZ
              - BA
              - BB
              - BD
              - BE
              - BF
              - BG
              - BH
              - BI
              - BJ
              - BL
              - BM
              - BN
              - BO
              - BQ
              - BR
              - BS
              - BT
              - BV
              - BW
              - BY
              - BZ
              - CA
              - CC
              - CD
              - CF
              - CG
              - CH
              - CI
              - CK
              - CL
              - CM
              - CN
              - CO
              - CR
              - CU
              - CV
              - CW
              - CX
              - CY
              - CZ
              - DE
              - DJ
              - DK
              - DM
              - DO
              - DZ
              - EC
              - EE
              - EG
              - EH
              - ER
              - ES
              - ET
              - FI
              - FJ
              - FK
              - FM
              - FO
              - FR
              - GA
              - GB
              - GD
              - GE
              - GF
              - GG
              - GH
              - GI
              - GL
              - GM
              - GN
              - GP
              - GQ
              - GR
              - GS
              - GT
              - GU
              - GW
              - GY
              - HK
              - HM
              - HN
              - HR
              - HT
              - HU
              - ID
              - IE
              - IL
              - IM
              - IN
              - IO
              - IQ
              - IR
              - IS
              - IT
              - JE
              - JM
              - JO
              - JP
              - KE
              - KG
              - KH
              - KI
              - KM
              - KN
              - KP
              - KR
              - KW
              - KY
              - KZ
              - LA
              - LB
              - LC
              - LI
              - LK
              - LR
              - LS
              - LT
              - LU
              - LV
              - LY
              - MA
              - MC
              - MD
              - ME
              - MF
              - MG
              - MH
              - MK
              - ML
              - MM
              - MN
              - MO
              - MP
              - MQ
              - MR
              - MS
              - MT
              - MU
              - MV
              - MW
              - MX
              - MY
              - MZ
              - NA
              - NC
              - NE
              - NF
              - NG
              - NI
              - NL
              - 'NO'
              - NP
              - NR
              - NU
              - NZ
              - OM
              - PA
              - PE
              - PF
              - PG
              - PH
              - PK
              - PL
              - PM
              - PN
              - PR
              - PS
              - PT
              - PW
              - PY
              - QA
              - RE
              - RO
              - RS
              - RU
              - RW
              - SA
              - SB
              - SC
              - SD
              - SE
              - SG
              - SH
              - SI
              - SJ
              - SK
              - SL
              - SM
              - SN
              - SO
              - SR
              - SS
              - ST
              - SV
              - SX
              - SY
              - SZ
              - TC
              - TD
              - TF
              - TG
              - TH
              - TJ
              - TK
              - TL
              - TM
              - TN
              - TO
              - TR
              - TT
              - TV
              - TW
              - TZ
              - UA
              - UG
              - UM
              - US
              - UY
              - UZ
              - VA
              - VC
              - VE
              - VG
              - VI
              - VN
              - VU
              - WF
              - WS
              - YE
              - YT
              - ZA
              - ZM
              - ZW
            description: >-
              Only return brands in this country, as an uppercase ISO 3166-1
              alpha-2 code such as US or GB.
            example: US
          required: false
          description: >-
            Only return brands in this country, as an uppercase ISO 3166-1
            alpha-2 code such as US or GB.
          name: country
          in: query
        - schema:
            type: string
            enum:
              - afrikaans
              - albanian
              - amharic
              - arabic
              - armenian
              - assamese
              - aymara
              - azeri
              - basque
              - belarusian
              - bengali
              - bosnian
              - bulgarian
              - burmese
              - cantonese
              - catalan
              - cebuano
              - chinese
              - corsican
              - croatian
              - czech
              - danish
              - dutch
              - english
              - esperanto
              - estonian
              - farsi
              - fijian
              - finnish
              - french
              - galician
              - georgian
              - german
              - greek
              - guarani
              - gujarati
              - haitian-creole
              - hausa
              - hawaiian
              - hebrew
              - hindi
              - hmong
              - hungarian
              - icelandic
              - igbo
              - indonesian
              - irish
              - italian
              - japanese
              - javanese
              - kannada
              - kazakh
              - khmer
              - kinyarwanda
              - korean
              - kurdish
              - kyrgyz
              - lao
              - latin
              - latvian
              - lingala
              - lithuanian
              - luxembourgish
              - macedonian
              - malagasy
              - malay
              - malayalam
              - maltese
              - maori
              - marathi
              - mongolian
              - nepali
              - norwegian
              - odia
              - oromo
              - pashto
              - pidgin
              - polish
              - portuguese
              - punjabi
              - quechua
              - romanian
              - russian
              - samoan
              - scottish-gaelic
              - serbian
              - sesotho
              - shona
              - sindhi
              - sinhala
              - slovak
              - slovene
              - somali
              - spanish
              - sundanese
              - swahili
              - swedish
              - tagalog
              - tajik
              - tamil
              - tatar
              - telugu
              - thai
              - tibetan
              - tigrinya
              - tongan
              - tswana
              - turkish
              - turkmen
              - ukrainian
              - urdu
              - uyghur
              - uzbek
              - vietnamese
              - welsh
              - wolof
              - xhosa
              - yiddish
              - yoruba
              - zulu
            description: >-
              Only return brands with this primary language, such as english or
              french.
          required: false
          description: >-
            Only return brands with this primary language, such as english or
            french.
          name: language
          in: query
        - schema:
            type: boolean
            default: true
            description: >-
              Whether the search term matches by prefix, so partial words match
              as they are typed (e.g. 'stri' matches Stripe). Set to false to
              match whole words only.
          required: false
          description: >-
            Whether the search term matches by prefix, so partial words match as
            they are typed (e.g. 'stri' matches Stripe). Set to false to match
            whole words only.
          name: autocomplete
          in: query
        - schema:
            type: array
            items:
              type: string
              enum:
                - name
                - domain
            minItems: 1
            default:
              - name
              - domain
            description: >-
              Fields to match the search term against, as a comma-separated list
              or repeated parameter: 'name', 'domain', or both. Defaults to
              both.
          required: false
          description: >-
            Fields to match the search term against, as a comma-separated list
            or repeated parameter: 'name', 'domain', or both. Defaults to both.
          name: queryBy
          in: query
        - schema:
            type: integer
            minimum: 0
            maximum: 2
            default: 0
            description: >-
              Maximum number of typos tolerated when matching, from 0 to 2.
              Defaults to 0 (no typo tolerance).
          required: false
          description: >-
            Maximum number of typos tolerated when matching, from 0 to 2.
            Defaults to 0 (no typo tolerance).
          name: typoTolerance
          in: query
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
                        domain:
                          type: string
                          description: The brand's domain.
                          example: stripe.com
                        name:
                          type: string
                          description: The brand's name. Empty string when unknown.
                          example: Stripe
                        description:
                          type: string
                          description: The brand's description, when available.
                          example: Stripe designs athletic footwear and apparel.
                        country:
                          type: string
                          enum:
                            - AD
                            - AE
                            - AF
                            - AG
                            - AI
                            - AL
                            - AM
                            - AO
                            - AQ
                            - AR
                            - AS
                            - AT
                            - AU
                            - AW
                            - AX
                            - AZ
                            - BA
                            - BB
                            - BD
                            - BE
                            - BF
                            - BG
                            - BH
                            - BI
                            - BJ
                            - BL
                            - BM
                            - BN
                            - BO
                            - BQ
                            - BR
                            - BS
                            - BT
                            - BV
                            - BW
                            - BY
                            - BZ
                            - CA
                            - CC
                            - CD
                            - CF
                            - CG
                            - CH
                            - CI
                            - CK
                            - CL
                            - CM
                            - CN
                            - CO
                            - CR
                            - CU
                            - CV
                            - CW
                            - CX
                            - CY
                            - CZ
                            - DE
                            - DJ
                            - DK
                            - DM
                            - DO
                            - DZ
                            - EC
                            - EE
                            - EG
                            - EH
                            - ER
                            - ES
                            - ET
                            - FI
                            - FJ
                            - FK
                            - FM
                            - FO
                            - FR
                            - GA
                            - GB
                            - GD
                            - GE
                            - GF
                            - GG
                            - GH
                            - GI
                            - GL
                            - GM
                            - GN
                            - GP
                            - GQ
                            - GR
                            - GS
                            - GT
                            - GU
                            - GW
                            - GY
                            - HK
                            - HM
                            - HN
                            - HR
                            - HT
                            - HU
                            - ID
                            - IE
                            - IL
                            - IM
                            - IN
                            - IO
                            - IQ
                            - IR
                            - IS
                            - IT
                            - JE
                            - JM
                            - JO
                            - JP
                            - KE
                            - KG
                            - KH
                            - KI
                            - KM
                            - KN
                            - KP
                            - KR
                            - KW
                            - KY
                            - KZ
                            - LA
                            - LB
                            - LC
                            - LI
                            - LK
                            - LR
                            - LS
                            - LT
                            - LU
                            - LV
                            - LY
                            - MA
                            - MC
                            - MD
                            - ME
                            - MF
                            - MG
                            - MH
                            - MK
                            - ML
                            - MM
                            - MN
                            - MO
                            - MP
                            - MQ
                            - MR
                            - MS
                            - MT
                            - MU
                            - MV
                            - MW
                            - MX
                            - MY
                            - MZ
                            - NA
                            - NC
                            - NE
                            - NF
                            - NG
                            - NI
                            - NL
                            - 'NO'
                            - NP
                            - NR
                            - NU
                            - NZ
                            - OM
                            - PA
                            - PE
                            - PF
                            - PG
                            - PH
                            - PK
                            - PL
                            - PM
                            - PN
                            - PR
                            - PS
                            - PT
                            - PW
                            - PY
                            - QA
                            - RE
                            - RO
                            - RS
                            - RU
                            - RW
                            - SA
                            - SB
                            - SC
                            - SD
                            - SE
                            - SG
                            - SH
                            - SI
                            - SJ
                            - SK
                            - SL
                            - SM
                            - SN
                            - SO
                            - SR
                            - SS
                            - ST
                            - SV
                            - SX
                            - SY
                            - SZ
                            - TC
                            - TD
                            - TF
                            - TG
                            - TH
                            - TJ
                            - TK
                            - TL
                            - TM
                            - TN
                            - TO
                            - TR
                            - TT
                            - TV
                            - TW
                            - TZ
                            - UA
                            - UG
                            - UM
                            - US
                            - UY
                            - UZ
                            - VA
                            - VC
                            - VE
                            - VG
                            - VI
                            - VN
                            - VU
                            - WF
                            - WS
                            - YE
                            - YT
                            - ZA
                            - ZM
                            - ZW
                          description: >-
                            The brand's country, when available, as an uppercase
                            ISO 3166-1 alpha-2 code.
                          example: US
                        language:
                          type: string
                          enum:
                            - afrikaans
                            - albanian
                            - amharic
                            - arabic
                            - armenian
                            - assamese
                            - aymara
                            - azeri
                            - basque
                            - belarusian
                            - bengali
                            - bosnian
                            - bulgarian
                            - burmese
                            - cantonese
                            - catalan
                            - cebuano
                            - chinese
                            - corsican
                            - croatian
                            - czech
                            - danish
                            - dutch
                            - english
                            - esperanto
                            - estonian
                            - farsi
                            - fijian
                            - finnish
                            - french
                            - galician
                            - georgian
                            - german
                            - greek
                            - guarani
                            - gujarati
                            - haitian-creole
                            - hausa
                            - hawaiian
                            - hebrew
                            - hindi
                            - hmong
                            - hungarian
                            - icelandic
                            - igbo
                            - indonesian
                            - irish
                            - italian
                            - japanese
                            - javanese
                            - kannada
                            - kazakh
                            - khmer
                            - kinyarwanda
                            - korean
                            - kurdish
                            - kyrgyz
                            - lao
                            - latin
                            - latvian
                            - lingala
                            - lithuanian
                            - luxembourgish
                            - macedonian
                            - malagasy
                            - malay
                            - malayalam
                            - maltese
                            - maori
                            - marathi
                            - mongolian
                            - nepali
                            - norwegian
                            - odia
                            - oromo
                            - pashto
                            - pidgin
                            - polish
                            - portuguese
                            - punjabi
                            - quechua
                            - romanian
                            - russian
                            - samoan
                            - scottish-gaelic
                            - serbian
                            - sesotho
                            - shona
                            - sindhi
                            - sinhala
                            - slovak
                            - slovene
                            - somali
                            - spanish
                            - sundanese
                            - swahili
                            - swedish
                            - tagalog
                            - tajik
                            - tamil
                            - tatar
                            - telugu
                            - thai
                            - tibetan
                            - tigrinya
                            - tongan
                            - tswana
                            - turkish
                            - turkmen
                            - ukrainian
                            - urdu
                            - uyghur
                            - uzbek
                            - vietnamese
                            - welsh
                            - wolof
                            - xhosa
                            - yiddish
                            - yoruba
                            - zulu
                          description: The brand's primary language, when available.
                          example: english
                        logo:
                          type: string
                          description: >-
                            Logo link URL that serves the brand's logo,
                            generated per request for the calling organization.
                          example: >-
                            https://logos.context.dev/?publicClientId=brandLL_1a2b3c&domain=stripe.com
                      required:
                        - domain
                        - name
                        - logo
                    maxItems: 10
                    description: >-
                      Up to 10 matching brands, name matches first, then domain
                      matches, most popular first within each group. Empty when
                      nothing matches.
                  key_metadata:
                    $ref: '#/components/schemas/KeyMetadata'
                  request_id:
                    $ref: '#/components/schemas/RequestId'
                required:
                  - results
                  - request_id
        '400':
          description: Bad Request - Invalid or missing search query
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
  parameters:
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
  schemas:
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