# Query

>  Get structured, typed JSON rows plus matching entities from Cala's knowledge base.

 Accepts either a Cala QL expression or a natural-language question as input — both produce the same structured response shape.


Examples:

 `{"input": "startups.location=Spain.funding＞10M.funding＜=50M"}`

 `{"input": "companies.industry=fintech.founded_year＞=2020"}`

 `{"input": "people.role=CEO.company.industry=AI"}`

 `{"input": "What are the biggest AI startups in Europe by funding?"}`


Use this when you want structured, tabular data for programmatic use. Use `knowledge_search` when you want a natural-language answer instead. To look up a known entity by name use `entity_search`. 



## OpenAPI

````yaml POST /v1/knowledge/query
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
  /v1/knowledge/query:
    post:
      tags:
        - API v1
        - Knowledge
      summary: Query
      description: >-
        Search verified knowledge and get back a structured list of matching
        entities. Same input as

        `knowledge_search` — natural language or Dot-Notation Syntax — only the
        output shape differs.


        Returns a structured array of matching results plus entities. The input
        field is called "input" (not "query").



        Dot-Notation Syntax lets you express filters and structure directly:


        - `.` navigates entity/topic → attribute → nested facet (e.g.
        `companies.industry`)


        - `=` `!=` `>` `<` `>=` `<=` filter a facet


        - `AND` / `OR` combine multiple values of the *same* field (e.g.
        `investors=A AND B`,
          `series=A OR B`); chain different fields with `.`

        - `order_by=field ASC|DESC` and `limit=N` steer which results surface,
        not just their order


        - `return(f1, f2, ...)` projects the result to just those fields (always
        keep an identity field
          like `name`)

        - Clauses can appear in any order


        - Numeric fields may come back as approximate strings (e.g. "over 100M",
        "~206,753") —
          synthesize, don't treat as exact


        Examples:


        `{"input": "Which biotech companies were founded after 2020?"}`


        `{"input": "companies.industry=fintech.founded_year>=2020"}`


        `{"input": "people.role=CEO.company.industry=AI"}`



        Use this when: You want a filtered, structured list of entities back.

        NOT for: A researched prose answer with citations — use
        `knowledge_search` instead (same input,

        different output). NOT for: Looking up one specific entity by name — use
        `entity_search`.
      operationId: knowledge_query
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
        required: true
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QueryResponse'
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
    QueryRequest:
      properties:
        input:
          type: string
          title: Input
          description: >-
            Natural language question or Dot-Notation Syntax (e.g.
            "companies.industry=fintech.founded_year>=2020"). Dot-Notation
            Syntax is not a strict grammar — there is no syntax to get wrong. An
            empty or fallback result means no match, not a syntax error.
          examples:
            - companies.industry=fintech.founded_year>=2020
        return_entities:
          type: boolean
          title: Return Entities
          description: Whether to return the entities identified in the query response.
          default: true
          examples:
            - true
      type: object
      required:
        - input
      title: QueryRequest
      example:
        input: companies.industry=fintech.founded_year>=2020
    QueryResponse:
      properties:
        results:
          items:
            additionalProperties: true
            type: object
          type: array
          title: Results
          description: >-
            A list of structured results for the query. Shape and schema will be
            determined by the query.
          examples:
            - - company: Amenitiz
                funding_amount: €38.9M
                round_type: Series B
                sector: Hospitality SaaS
                year: 2025
              - company: H2SITE
                funding_amount: €36M ($37.2M)
                round_type: Series B
                sector: Hydrogen Energy
                year: 2025
              - company: Fracttal
                funding_amount: €29.8M ($35M)
                round_type: Series B
                sector: AI Maintenance
                year: 2026
        entities:
          anyOf:
            - items:
                $ref: '#/components/schemas/EntityMention'
              type: array
            - type: 'null'
          title: Entities
          description: Entities identified in the query response.
      type: object
      required:
        - results
        - entities
      title: QueryResponse
      description: Response in case of a successful structured query.
      example:
        entities:
          - entity_type: Company
            id: e2932ee7-7b57-42b7-8c58-cdfcdf56ceb5
            mentions:
              - Amenitiz
            name: Amenitiz
          - entity_type: Company
            id: e843fc48-8339-4c99-a6e2-e7fb1cc738b1
            mentions:
              - H2SITE
            name: H2SITE
          - entity_type: Company
            id: af3ff4b5-27a9-45d5-8c67-b656cb38e6b8
            mentions:
              - Fracttal
            name: Fracttal
        results:
          - company: Amenitiz
            funding_amount: €38.9M
            round_type: Series B
            sector: Hospitality SaaS
            year: 2025
          - company: H2SITE
            funding_amount: €36M ($37.2M)
            round_type: Series B
            sector: Hydrogen Energy
            year: 2025
          - company: Fracttal
            funding_amount: €29.8M ($35M)
            round_type: Series B
            sector: AI Maintenance
            year: 2026
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
    EntityMention:
      properties:
        id:
          type: string
          format: uuid
          title: Id
          description: The ID of the entity
          examples:
            - 0abe9580-5abb-46df-9506-5dc784520b69
        name:
          type: string
          title: Name
          description: The name of the entity
          examples:
            - Altano Energy
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
          examples:
            - Company
        mentions:
          items:
            type: string
          type: array
          title: Mentions
          description: Mentions of this entity in the response.
          examples:
            - - Altano Energy
              - Altano
      type: object
      required:
        - id
        - name
        - entity_type
        - mentions
      title: EntityMention
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