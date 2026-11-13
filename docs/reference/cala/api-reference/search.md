# Search

>  Get a succinct, token-optimized answer in natural-language markdown, with explainability, source citations, and matching entities.

 Accepts either a Cala QL expression or a natural-language question as input — both produce the same response shape.


Examples:

 `{"input": "What are the biggest AI startups in Europe by funding?"}`

 `{"input": "Who founded Stripe and what is their background?"}`

 `{"input": "What regulations affect fintech companies in the EU?"}`


Use this when you want a natural-language answer with sources and explainability. Use `knowledge_query` when you want structured, tabular rows instead. Use `entity_search` if you just need to find an entity by name. 



## OpenAPI

````yaml POST /v1/knowledge/search
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
  /v1/knowledge/search:
    post:
      tags:
        - API v1
        - Knowledge
      summary: Search
      description: >-
        Search verified knowledge and get back a sourced, prose answer. Best
        when you have a question and

        want a researched narrative with citations — not a list of entities.


        Returns markdown content with explainability, source citations, and
        matching entities.



        Input can be natural language or Dot-Notation Syntax — both work the
        same here, only the output

        shape differs from `knowledge_query`.



        Dot-Notation Syntax lets you express filters and structure directly:


        - `.` navigates entity/topic → attribute → nested facet (e.g.
        `companies.industry`)


        - `=` `!=` `>` `<` `>=` `<=` filter a facet


        - `AND` / `OR` combine multiple values of the *same* field (e.g.
        `investors=A AND B`,
          `series=A OR B`); chain different fields with `.`

        - `order_by=field ASC|DESC` and `limit=N` steer which results surface,
        not just their order


        - `return(f1, f2, ...)` focuses the answer on specific fields (a strict
        field projection on
          `knowledge_query`)

        - Clauses can appear in any order


        - Numeric fields may come back as approximate strings (e.g. "over 100M",
        "~206,753") —
          synthesize, don't treat as exact


        Examples:


        `{"input": "Who founded Anthropic and what is their background?"}`


        `{"input": "people.role=CEO.company.industry=renewable_energy"}`


        `{"input": "What regulations affect fintech companies in the EU?"}`



        Use this when: You want a sourced, prose answer to a question.

        NOT for: A structured list of matching entities — use `knowledge_query`
        instead (same input,

        different output). NOT for: Looking up one specific entity by name — use
        `entity_search`.
      operationId: knowledge_search
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SearchRequest'
        required: true
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Answer'
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
    SearchRequest:
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
            - Who founded Anthropic and what is their background?
        explainability:
          type: boolean
          title: Explainability
          description: Whether to generate explainability for the answer.
          default: true
          examples:
            - true
        return_entities:
          type: boolean
          title: Return Entities
          description: Whether to return the entities identified in the answer.
          default: true
          examples:
            - true
      type: object
      required:
        - input
      title: SearchRequest
      example:
        input: Who founded Anthropic and what is their background?
    Answer:
      properties:
        content:
          type: string
          title: Content
          description: A succinct answer to the user's input in Markdown format.
          examples:
            - >-
              **Altano Energy (Spain)** — Madrid-based, developing renewable
              energy projects across Spain. Altano secured €60M Series C in 2025
              from M&G Investments and Pioneer Point Partners.
        explainability:
          anyOf:
            - items:
                $ref: '#/components/schemas/ReasoningSteps'
              type: array
            - type: 'null'
          title: Explainability
          description: A list of reasoning steps to get to that answer.
        context:
          items:
            $ref: '#/components/schemas/KnowBit'
          type: array
          title: Context
          description: A list of facts that support the answer.
        entities:
          anyOf:
            - items:
                $ref: '#/components/schemas/EntityMention'
              type: array
            - type: 'null'
          title: Entities
          description: Entities identified in the answer.
      type: object
      required:
        - content
        - explainability
        - context
        - entities
      title: Answer
      description: >-
        The answer to the user's input with the reasoning steps and the context
        that support the answer.
      example:
        content: >-
          **Altano Energy (Spain)** — Madrid-based, developing renewable energy
          projects across Spain. Altano secured €60M Series C in 2025 from M&G
          Investments and Pioneer Point Partners.
        context:
          - content: >-
              Altano Energy - €60m (Series C, Jul 2025). Develops and operates
              renewable energy projects across Spain...
            id: 732e1954-9538-4fbc-a565-db2f8c07ad4e
        entities:
          - entity_type: Company
            id: 0abe9580-5abb-46df-9506-5dc784520b69
            mentions:
              - Altano Energy
              - Altano
            name: Altano Energy
        explainability:
          - content: >-
              Altano Energy secured a €60 million Series C round in July 2025
              from Pioneer Point Partners and M&G Investments.
            references:
              - f22a1a96-6234-48d7-95c2-8b049f00fdab
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
    ReasoningSteps:
      properties:
        content:
          type: string
          title: Content
          description: The content of the reasoning step.
          examples:
            - >-
              Altano Energy secured a €60 million Series C round in July 2025
              from Pioneer Point Partners and M&G Investments.
        references:
          items:
            type: string
            format: uuid
          type: array
          title: References
          description: >-
            The UUIDs of the KnowBits referenced in the reasoning step. Must
            match 'id' fields in context array.
          examples:
            - - f22a1a96-6234-48d7-95c2-8b049f00fdab
      type: object
      required:
        - content
        - references
      title: ReasoningSteps
      description: A step in the reasoning process.
    KnowBit:
      properties:
        id:
          type: string
          format: uuid
          title: Id
          description: The id of the KnowBit.
          examples:
            - 732e1954-9538-4fbc-a565-db2f8c07ad4e
        content:
          type: string
          title: Content
          description: The information contained in the KnowBit.
          examples:
            - >-
              Altano Energy - €60m (Series C, Jul 2025). Develops and operates
              renewable energy projects across Spain...
        origins:
          items:
            $ref: '#/components/schemas/Origin'
          type: array
          title: Origins
          description: The origins from which the KnowBit was extracted.
      type: object
      required:
        - id
        - content
        - origins
      title: KnowBit
      description: >-
        A KnowBit is like a fact, a piece of information that supports the
        answer.
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
    Origin:
      properties:
        source:
          $ref: '#/components/schemas/Source'
        document:
          $ref: '#/components/schemas/Document'
        breadcrumb:
          items:
            type: string
          type: array
          title: Breadcrumb
          description: Breadcrumb field (always empty for compatibility)
          examples:
            - - ''
      type: object
      required:
        - source
        - document
        - breadcrumb
      title: Origin
      description: The sources and documents from which the KnowBit was extracted.
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
    Source:
      properties:
        name:
          type: string
          title: Name
          description: The name or title of the source.
          examples:
            - Impact Loop
        url:
          type: string
          minLength: 1
          format: uri
          title: URL
          description: The URL of the source.
          examples:
            - https://www.impactloop.com/
      type: object
      required:
        - name
        - url
      title: Source
      description: >-
        Organization that provides, creates, or publishes the document, like a
        web site, a book, a report, etc.
    Document:
      properties:
        name:
          type: string
          title: Name
          description: The name or title of the document.
          examples:
            - Europe's top 25 climate tech funding rounds this year
        url:
          type: string
          minLength: 1
          format: uri
          title: URL
          description: The URL of the document.
          examples:
            - >-
              https://www.impactloop.com/artikel/europe-s-25-largest-climate-tech-fundraises-funding-2025-and-the-investors-behind-them
      type: object
      required:
        - name
        - url
      title: Document
      description: Specific text, report, article, or file that contains the information.
  securitySchemes:
    APIKeyHeader:
      type: apiKey
      in: header
      name: X-API-KEY

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.