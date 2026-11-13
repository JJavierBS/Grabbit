# Retrieve Entity

> Retrieve an entity by its UUID.

Returns detailed information including legal name, industry, founders, executives, headquarters, employee count, and more.

Pass the entity UUID in the URL path (e.g. `POST /entities/{entity_id}`). Optionally send a JSON body to specify which properties and relationships to return; if omitted, default properties are returned.

Use the ***Entity Introspection*** endpoint to see which properties and relationships can be queried for an entity.

Examples (path + optional body):

`POST /entities/c6772802-bdbc-4778-91e9-cd3d27d008d5`

Optional body: `{"properties": ["name", "aliases", "registered_address", "employee_count"], "relationships": {"outgoing": {"IS_ULTIMATE_PARENT": {"limit": 5}}, "incoming": {"IS_CEO_OF": {}}}}`

Use this when you already have an entity UUID (from `entity_search`, `entity_lookup`, `knowledge_search`, or `knowledge_query` results) and need the complete profile. Use `entity_search` first if you only have a name, or `entity_lookup` if you have an identifier (LEI, CIK, …).




## OpenAPI

````yaml POST /v1/entities/{entity_id}
openapi: 3.1.0
info:
  title: Cala AI
  summary: Verified, reliable knowledge one API call away
  description: >

    ### Knowledge Search


    Let's you search for verified knowledge to empower your AI Agent with the
    **right context**.


    ### Knowledge Entities


    Get information about entities, **structured** and reliable.
  version: Beta 1.0
servers:
  - url: https://api.cala.ai
security: []
paths:
  /v1/entities/{entity_id}:
    post:
      tags:
        - API v1
        - Entities
      summary: Entities
      description: >-
        Get typed entity data by its UUID — company, person, place, law,
        financial instrument, and

        more (the schema spans many domains, illustrative not exhaustive) — in
        two modes:



        - **Coarse (no body):** returns only the default property set. No
        relationships, no numerical
          observations. Use only when a rough profile is enough.

        - **Projection (body):** name exact `properties`, `relationships`, and
        `numerical_observations` to
          get back. The only way to get relationships or time-series data, and the most token-efficient
          read. Available fields vary by entity type and must be *queryable* for that specific entity — run
          `entity_introspection` first to discover them; projecting blind wastes round-trips and may hit
          empty or non-queryable edges.


        Pass the entity UUID in the URL path (e.g. `POST
        /entities/{entity_id}`). Optionally send a JSON body

        to specify which properties and relationships to return; if omitted,
        default properties are returned.


        Examples (path + optional body):


        `POST /entities/c6772802-bdbc-4778-91e9-cd3d27d008d5`


        Optional body: `{"properties": ["name", "aliases", "registered_address",
        "employee_count"], "relationships": {"outgoing": {"IS_ULTIMATE_PARENT":
        {"limit": 5}}, "incoming": {"IS_CEO_OF": {}}}}`



        Use this when: You already have an entity UUID (from `entity_search`,
        `entity_lookup`, `knowledge_search`, or

        `knowledge_query` results) and need entity data. Use `entity_search`
        first if you only have a name,

        `entity_lookup` if you have an Ontology identifier (LEI, CIK, …), and
        `entity_introspection` first if you need

        a projection.
      operationId: retrieve_entity
      parameters:
        - name: entity_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
            description: >-
              The entity's UUID: the `id` of a result from `entity_search` or
              `entity_lookup`, or of an entity in a `knowledge_search` or
              `knowledge_query` response. Never a name, a number, or a
              placeholder.
            examples:
              - c6772802-bdbc-4778-91e9-cd3d27d008d5
            title: Entity Id
          description: >-
            The entity's UUID: the `id` of a result from `entity_search` or
            `entity_lookup`, or of an entity in a `knowledge_search` or
            `knowledge_query` response. Never a name, a number, or a
            placeholder.
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EntityQuery'
              description: >-
                Optional query to specify which properties and relationships to
                return for the entity. If it is not provided, default properties
                will be returned.
              examples:
                - properties:
                    - name
                    - aliases
                    - registered_address
                    - employee_count
                  relationships:
                    outgoing:
                      IS_REGISTERED_IN:
                        limit: 2
                        offset: 0
                    incoming:
                      IS_BOARD_MEMBER_OF:
                        limit: 2
                        offset: 2
                  numerical_observations:
                    FinancialMetric:
                      - 1d3eae40-0ba8-5baf-9907-6a4823b067bb
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GetEntityResponse'
        '422':
          description: Validation Error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '429':
          description: Too many requests (rate limit exceeded)
          content:
            application/json:
              example:
                error: rate_limit_exceeded
                message: Rate limit exceeded. Too many requests.
      security:
        - APIKeyHeader: []
components:
  schemas:
    EntityQuery:
      properties:
        properties:
          items:
            type: string
          type: array
          title: Properties
          description: List of entity property names to query
          default: []
          examples:
            - - name
              - aliases
              - registered_address
              - employee_count
        relationships:
          $ref: '#/components/schemas/EntityQueryRelationships'
          description: Relationship queries
        numerical_observations:
          additionalProperties:
            items:
              type: string
              format: uuid
            type: array
          type: object
          title: Numerical Observations
          description: >-
            Numerical observations to query, keyed by observation type name (for
            example, FinancialMetric), with lists of observation UUIDs as values
          examples:
            - FinancialMetric:
                - 1d3eae40-0ba8-5baf-9907-6a4823b067bb
      type: object
      title: EntityQuery
      example:
        numerical_observations:
          FinancialMetric:
            - 1d3eae40-0ba8-5baf-9907-6a4823b067bb
        properties:
          - name
          - aliases
          - registered_address
          - employee_count
        relationships:
          incoming:
            IS_BOARD_MEMBER_OF:
              limit: 2
              offset: 2
          outgoing:
            IS_REGISTERED_IN:
              limit: 2
              offset: 0
    GetEntityResponse:
      properties:
        id:
          type: string
          format: uuid
          title: Id
          description: The ID of the entity
        name:
          type: string
          title: Name
          description: The name of the entity
        entity_type:
          type: string
          enum:
            - Entity
            - Animal
            - Award
            - Organization
            - Company
            - EducationalInstitution
            - ResearchInstitution
            - GovernmentalInstitution
            - CulturalInstitution
            - NonprofitOrganization
            - IntergovernmentalOrganization
            - HealthcareEstablishment
            - Hospital
            - HealthcareNetwork
            - HealthcareMetric
            - Person
            - Event
            - GPE
            - Country
            - CountrySubdivision
            - DependentTerritory
            - Municipality
            - Continent
            - Currency
            - Industry
            - DomainName
            - FinancialMetric
            - CuratedFinancialMetric
            - Group
            - CorporateEvent
            - PrivateCompanyFundingRound
            - FundingRound
            - FundingRoundTranche
            - LoanFacilityComponent
            - Facility
            - Location
            - Organism
            - Plant
            - Fungus
            - Bacterium
            - Archaeon
            - Virus
            - Protist
            - Chromosome
            - Product
            - Medicine
            - ChemicalSubstance
            - SmallMolecule
            - Protein
            - ProteinComplex
            - Antibody
            - ProteinIsoform
            - Gene
            - Transcript
            - Oligonucleotide
            - Drug
            - SmallMoleculeDrug
            - AntibodyDrug
            - ProteinDrug
            - OligonucleotideDrug
            - ChemicalSubstanceDrug
            - CellTherapy
            - GeneTherapy
            - MechanismOfAction
            - Disease
            - Anatomy
            - Pathway
            - ClinicalTrial
            - ClinicalTrialArm
            - ClinicalIntervention
            - ClinicalOutcome
            - Sanction
            - WorkOfArt
            - Document
            - Patent
            - ResearchPaper
            - Law
            - Language
            - Exchange
            - Future
            - Commodity
            - PositioningMetric
            - MacroIndicatorPublication
            - MacroIndicator
            - ForeignExchangeRate
            - CountryRegion
            - AbstractFinancialMetric
          title: Entity Type
          description: The type of the entity
        description:
          anyOf:
            - type: string
            - type: 'null'
          title: Description
          description: A short description of the entity
        properties:
          additionalProperties: true
          type: object
          title: Properties
          description: >-
            List of property names available for this entity (e.g. id, name,
            currency).
          examples:
            - aliases:
                sources: []
                value:
                  - Apple Computer, Inc.
                  - Apple
                  - AAPL
                  - Apple Inc.
                  - Apple (AAPL)
                  - Apple Computer Inc.
                  - Apple Computer Company
                  - 'NASDAQ: AAPL'
                  - 'Apple — AAPL (NASDAQ: AAPL)'
                  - 'Apple (NASDAQ: AAPL)'
              employee_count:
                sources:
                  - date: '2026-04-15'
                    document: https://www.stockanalysis.com/stocks/aapl/employees/
                    name: Apple (AAPL) Number of Employees 1994-2025
                value: 166000
              name:
                sources:
                  - date: '2026-02-26'
                    document:
                      endpoint: >-
                        https://efts.sec.gov/LATEST/search-index?q=%22APPLE+INC%22
                      params: {}
                      response_hash: >-
                        3f0354a291ad77088d55bd2577294a85d5ba3c1b9ae0aa5a58c53bb24ed49111
                    name: SEC
                value: APPLE INC
              registered_address:
                sources:
                  - date: '2026-01-01'
                    document: >-
                      https://www.creditsafe.com/business-index/en-gb/company/apple-inc-us22139727
                    name: Apple Inc Credit Report
                  - date: '2025-07-25'
                    document: >-
                      https://www.bbb.org/us/ca/cupertino/profile/home-electronics/apple-inc-1216-198239
                    name: About
                  - date: '2026-04-16'
                    document: >-
                      https://labormarketinfo.edd.ca.gov/aspdotnet/databrowsing/empDetails.aspx?menuchoice=emp&geogArea=0604000085&empId=008264145
                    name: labormarketinfo.edd.ca.gov
                value: One Apple Park Way, Cupertino, CA 95014, USA
        relationships:
          $ref: '#/components/schemas/EntityRelationships'
          description: >-
            Outgoing and incoming relationship types. This field is empty unless
            relationships.incoming and/or relationships.outgoing are provided in
            the request.
        numerical_observations:
          items: {}
          type: array
          title: Numerical Observations
          description: Numerical observations keyed by observation type.
          examples:
            - - data:
                  - origin:
                      name: 10-Q
                      published_time: '2026-01-30T00:00:00Z'
                      source: SEC
                      url: >-
                        https://www.sec.gov/Archives/edgar/data/0000320193-26-000006/0000320193-26-000006-index.html
                    time: '2025-12-27T00:00:00Z'
                    value: 45317000000
                  - origin:
                      name: 10-K
                      published_time: '2025-10-31T00:00:00Z'
                      source: SEC
                      url: >-
                        https://www.sec.gov/Archives/edgar/data/0000320193-25-000079/0000320193-25-000079-index.html
                    time: '2025-09-27T00:00:00Z'
                    value: 35934000000
                  - origin:
                      name: 10-Q
                      published_time: '2026-01-30T00:00:00Z'
                      source: SEC
                      url: >-
                        https://www.sec.gov/Archives/edgar/data/0000320193-26-000006/0000320193-26-000006-index.html
                    time: '2025-09-27T00:00:00Z'
                    value: 35934000000
                id: 1d3eae40-0ba8-5baf-9907-6a4823b067bb
                name: Cash and Cash Equivalents, at Carrying Value
                properties:
                  unit: USD
                  aliases: []
                  taxonomy: us-gaap
                  cadence: i
                type: FinancialMetric
      type: object
      required:
        - id
        - name
        - entity_type
        - properties
        - relationships
      title: GetEntityResponse
      description: Response containing full entity profile
      example:
        description: >-
          Computer company founded in 1977 with headquarters in Cupertino,
          California
        entity_type: Company
        id: c6772802-bdbc-4778-91e9-cd3d27d008d5
        name: APPLE INC
        numerical_observations:
          - data:
              - origin:
                  name: 10-Q
                  published_time: '2026-01-30T00:00:00Z'
                  source: SEC
                  url: >-
                    https://www.sec.gov/Archives/edgar/data/0000320193-26-000006/0000320193-26-000006-index.html
                time: '2025-12-27T00:00:00Z'
                value: 45317000000
              - origin:
                  name: 10-K
                  published_time: '2025-10-31T00:00:00Z'
                  source: SEC
                  url: >-
                    https://www.sec.gov/Archives/edgar/data/0000320193-25-000079/0000320193-25-000079-index.html
                time: '2025-09-27T00:00:00Z'
                value: 35934000000
              - origin:
                  name: 10-Q
                  published_time: '2026-01-30T00:00:00Z'
                  source: SEC
                  url: >-
                    https://www.sec.gov/Archives/edgar/data/0000320193-26-000006/0000320193-26-000006-index.html
                time: '2025-09-27T00:00:00Z'
                value: 35934000000
            id: 1d3eae40-0ba8-5baf-9907-6a4823b067bb
            name: Cash and Cash Equivalents, at Carrying Value
            properties:
              unit: USD
              aliases: []
              taxonomy: us-gaap
              cadence: i
            type: FinancialMetric
        properties:
          name:
            sources:
              - date: '2026-02-26'
                document:
                  endpoint: https://efts.sec.gov/LATEST/search-index?q=%22APPLE+INC%22
                  params: {}
                  response_hash: >-
                    3f0354a291ad77088d55bd2577294a85d5ba3c1b9ae0aa5a58c53bb24ed49111
                name: SEC
            value: APPLE INC
          aliases:
            sources: []
            value:
              - Apple Computer, Inc.
              - Apple
              - AAPL
              - Apple Inc.
              - Apple (AAPL)
              - Apple Computer Inc.
              - Apple Computer Company
              - 'NASDAQ: AAPL'
              - 'Apple — AAPL (NASDAQ: AAPL)'
              - 'Apple (NASDAQ: AAPL)'
          registered_address:
            sources:
              - date: '2026-01-01'
                document: >-
                  https://www.creditsafe.com/business-index/en-gb/company/apple-inc-us22139727
                name: Apple Inc Credit Report
              - date: '2025-07-25'
                document: >-
                  https://www.bbb.org/us/ca/cupertino/profile/home-electronics/apple-inc-1216-198239
                name: About
              - date: '2026-04-16'
                document: >-
                  https://labormarketinfo.edd.ca.gov/aspdotnet/databrowsing/empDetails.aspx?menuchoice=emp&geogArea=0604000085&empId=008264145
                name: labormarketinfo.edd.ca.gov
            value: One Apple Park Way, Cupertino, CA 95014, USA
          employee_count:
            sources:
              - date: '2026-04-15'
                document: https://www.stockanalysis.com/stocks/aapl/employees/
                name: Apple (AAPL) Number of Employees 1994-2025
            value: 166000
        relationships:
          incoming:
            IS_BOARD_MEMBER_OF:
              - entity_type: Person
                id: 1118056e-3ddc-4856-8855-9f6179924d25
                name: William Campbell
                properties:
                  valid_until: '2015-03-13'
                  sources:
                    - date: '2014-03-05'
                      document: >-
                        https://www.sec.gov/Archives/edgar/data/320193/000119312514084697/d684095d8k.htm
                      name: SEC
                    - date: '2015-03-13'
                      document: >-
                        https://www.sec.gov/Archives/edgar/data/320193/000110465915019336/a15-5624_18k.htm
                      name: SEC
                  id: b4ab6a95-9b90-4c70-bcde-343f34df25ca
                  valid_since: '2014-02-28'
              - entity_type: Person
                id: 39326f52-abf3-44f9-a552-ef183daa68f0
                name: James A. Bell
                properties:
                  valid_until: '2024-02-28'
                  sources:
                    - date: '2015-10-02'
                      document: >-
                        https://www.sec.gov/Archives/edgar/data/320193/000119312515336615/d10101d8k.htm
                      name: SEC
                    - date: '2016-03-01'
                      document: >-
                        https://www.sec.gov/Archives/edgar/data/320193/000119312516488223/d150918d8k.htm
                      name: SEC
                    - date: '2017-03-01'
                      document: >-
                        https://www.sec.gov/Archives/edgar/data/320193/000119312517064019/d342218d8k.htm
                      name: SEC
                    - date: '2018-02-14'
                      document: >-
                        https://www.sec.gov/Archives/edgar/data/320193/000119312518045761/d374908d8k.htm
                      name: SEC
                    - date: '2019-03-04'
                      document: >-
                        https://www.sec.gov/Archives/edgar/data/320193/000032019319000032/copyofreference8-kform8xkq.htm
                      name: SEC
                    - date: '2020-02-27'
                      document: >-
                        https://www.sec.gov/Archives/edgar/data/320193/000119312520050884/d865740d8k.htm
                      name: SEC
                  id: 93adb3c1-049f-4dc4-a363-7b368f69d76f
                  valid_since: '2015-10-01'
          outgoing:
            IS_REGISTERED_IN:
              - entity_type: Country
                id: 37a1f0f5-f5ef-4b63-b3d8-14f5636be703
                name: United States
                properties:
                  sources:
                    - date: '2026-04-15'
                      document: >-
                        https://indianexpress.com/article/trending/top-10-listing/top-10-tech-companies-in-the-world-by-market-cap-2025-9977264
                      name: indianexpress.com
                  id: bb76eabf-d089-5a3a-a4a3-2ab2b38a2cac
    ErrorResponse:
      properties:
        response_type:
          type: string
          const: ERROR
          title: Response Type
          default: ERROR
        error:
          $ref: '#/components/schemas/Error'
      type: object
      required:
        - error
      title: ErrorResponse
    EntityQueryRelationships:
      properties:
        outgoing:
          additionalProperties: true
          type: object
          title: Outgoing
          description: Outgoing relationship
          default: {}
          examples:
            - IS_REGISTERED_IN:
                limit: 2
                offset: 0
        incoming:
          additionalProperties: true
          type: object
          title: Incoming
          description: Incoming relationship
          default: {}
          examples:
            - IS_BOARD_MEMBER_OF:
                limit: 2
                offset: 2
      type: object
      title: EntityQueryRelationships
    EntityRelationships:
      properties:
        outgoing:
          additionalProperties: true
          type: object
          title: Outgoing
          description: Outgoing relationship type names.
          examples:
            - IS_REGISTERED_IN:
                - entity_type: Country
                  id: 37a1f0f5-f5ef-4b63-b3d8-14f5636be703
                  name: United States
                  properties:
                    sources:
                      - date: '2026-04-15'
                        document: >-
                          https://indianexpress.com/article/trending/top-10-listing/top-10-tech-companies-in-the-world-by-market-cap-2025-9977264
                        name: indianexpress.com
                    id: bb76eabf-d089-5a3a-a4a3-2ab2b38a2cac
        incoming:
          additionalProperties: true
          type: object
          title: Incoming
          description: Incoming relationship type names.
          examples:
            - IS_BOARD_MEMBER_OF:
                - entity_type: Person
                  id: 1118056e-3ddc-4856-8855-9f6179924d25
                  name: William Campbell
                  properties:
                    valid_until: '2015-03-13'
                    sources:
                      - date: '2014-03-05'
                        document: >-
                          https://www.sec.gov/Archives/edgar/data/320193/000119312514084697/d684095d8k.htm
                        name: SEC
                      - date: '2015-03-13'
                        document: >-
                          https://www.sec.gov/Archives/edgar/data/320193/000110465915019336/a15-5624_18k.htm
                        name: SEC
                    id: b4ab6a95-9b90-4c70-bcde-343f34df25ca
                    valid_since: '2014-02-28'
                - entity_type: Person
                  id: 39326f52-abf3-44f9-a552-ef183daa68f0
                  name: James A. Bell
                  properties:
                    valid_until: '2024-02-28'
                    sources:
                      - date: '2015-10-02'
                        document: >-
                          https://www.sec.gov/Archives/edgar/data/320193/000119312515336615/d10101d8k.htm
                        name: SEC
                      - date: '2016-03-01'
                        document: >-
                          https://www.sec.gov/Archives/edgar/data/320193/000119312516488223/d150918d8k.htm
                        name: SEC
                      - date: '2017-03-01'
                        document: >-
                          https://www.sec.gov/Archives/edgar/data/320193/000119312517064019/d342218d8k.htm
                        name: SEC
                      - date: '2018-02-14'
                        document: >-
                          https://www.sec.gov/Archives/edgar/data/320193/000119312518045761/d374908d8k.htm
                        name: SEC
                      - date: '2019-03-04'
                        document: >-
                          https://www.sec.gov/Archives/edgar/data/320193/000032019319000032/copyofreference8-kform8xkq.htm
                        name: SEC
                      - date: '2020-02-27'
                        document: >-
                          https://www.sec.gov/Archives/edgar/data/320193/000119312520050884/d865740d8k.htm
                        name: SEC
                    id: 93adb3c1-049f-4dc4-a363-7b368f69d76f
                    valid_since: '2015-10-01'
      type: object
      title: EntityRelationships
      description: Outgoing and incoming relationship types for an entity.
    Error:
      properties:
        error_type:
          $ref: '#/components/schemas/ErrorType'
        message:
          type: string
          title: Message
      type: object
      required:
        - error_type
        - message
      title: Error
    ErrorType:
      type: string
      enum:
        - internal_server_error
        - service_unavailable_error
        - format_error
        - session_not_found_error
        - entity_not_found_error
        - request_not_found_error
        - bad_gateway_error
        - search_query_error
      title: ErrorType
  securitySchemes:
    APIKeyHeader:
      type: apiKey
      in: header
      name: X-API-KEY

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.