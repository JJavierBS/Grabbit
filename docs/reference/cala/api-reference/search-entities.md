# Search Entities

>  Find entities by name with fuzzy matching when you know (or partially know) an entity's name.

 Optionally filter by entity type. Returns an array of matching entities, each with an `id`, `name`, `entity_type`, and a `description` (when available) — use the `id` to pass to ***Retrieve Entity*** for full profiles.


Examples:

 `GET /v1/entities?name=OpenAI`

 `GET /v1/entities?name=Tim+Cook&entity_types=Person`

 `GET /v1/entities?name=Berlin&entity_types=GPE&entity_types=Location&limit=5`


Use this when you know the name and want the entity ID or basic info. Use `entity_lookup` when you have an identifier (LEI, CIK, …) instead of a name. Use `retrieve_entity` with the returned ID for full details. Use `knowledge_query` when you want a structured, tabular answer, or `knowledge_search` for a succinct natural-language answer. 



## OpenAPI

````yaml GET /v1/entities
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
  /v1/entities:
    get:
      tags:
        - API v1
        - Entities
      summary: Search Entities
      description: >-
        Find real-world entities by name with fuzzy matching — spans many
        domains and keeps growing:

        business (companies, investors, funding rounds, M&A, industries,
        products), people, legal (laws,

        regulations, sanctions), geography (countries, places), finance/macro
        (financial metrics, macro

        indicators, FX rates), healthcare (hospitals, healthcare establishments
        and metrics), and more — treat

        this list as illustrative, not exhaustive. Use for "look up X" /
        "who/what is X" / "X's profile,

        properties, or relationships" when you know (or partially know) the
        name. Optionally filter by entity type.


        Returns an array of matching entities with IDs that feed
        `entity_retrieval` (entity data) and

        `entity_introspection` (available fields).



        Examples:


        `{"name": "OpenAI"}`


        `{"name": "Elon Musk", "entity_types": ["Person"]}`


        `{"name": "Berlin", "entity_types": ["GPE"]}`


        `{"name": "GDPR", "entity_types": ["Law"]}`



        Use this when: You know the name and want the entity ID or a quick
        profile. Use `knowledge_query`

        instead for attribute-based filtering without a name.
      operationId: entity_search
      parameters:
        - name: name
          in: query
          required: true
          schema:
            type: string
            minLength: 1
            maxLength: 100
            description: Entity name to search for
            examples:
              - Fracttal
            title: Name
          description: Entity name to search for
        - name: entity_types
          in: query
          required: false
          schema:
            type: array
            items:
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
              type: string
            description: Filter by entity types
            default: []
            title: Entity Types
          description: Filter by entity types
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            maximum: 100
            minimum: 1
            description: Maximum number of results
            default: 20
            title: Limit
          description: Maximum number of results
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EntitySearchResponse'
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
    EntitySearchResponse:
      properties:
        entities:
          items:
            $ref: '#/components/schemas/Entity'
          type: array
          title: Entities
          description: >-
            List of entities matching the search query, ordered by relevance
            (most relevant first).
      type: object
      required:
        - entities
      title: EntitySearchResponse
      description: Response containing a list of entities matching the search query.
      example:
        entities:
          - description: An American multinational technology company.
            entity_type: Company
            id: e5bb591a-d308-4aa5-9672-96046d366cde
            name: OpenAI
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
    Entity:
      properties:
        id:
          type: string
          format: uuid
          title: Id
          description: The ID of the entity
          examples:
            - e5bb591a-d308-4aa5-9672-96046d366cde
        name:
          type: string
          title: Name
          description: The name of the entity
          examples:
            - OpenAI
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
        description:
          anyOf:
            - type: string
            - type: 'null'
          title: Description
          description: A short description of the entity
          examples:
            - An American multinational technology company.
      type: object
      required:
        - id
        - name
        - entity_type
      title: Entity
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