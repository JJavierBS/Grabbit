# Lookup Entity

>  Resolve one entity by an external identifier.

 Accepts exactly one of these schemes: `lei` (Legal Entity Identifier), `cik` (SEC Central Index Key), `rssd_id` (Federal Reserve RSSD ID), `companies_house_uk_company_number` (UK Companies House number), `siren` (French SIREN).

 Pass exactly one scheme in `id`, or as a top-level shorthand:

 `{"id": {"lei": "95980020140005017502"}}`

 `{"lei": "95980020140005017502"}`

 Returns an entity stub (`id`, `name`, `entity_type`, `description`). Feed the `id` into Retrieve Entity / Entity Introspection for a full profile.

 Use this when you have an external identifier and need the entity UUID. Use `retrieve_entity` when you already have the UUID. 



## OpenAPI

````yaml POST /v1/entities/lookup
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
  /v1/entities/lookup:
    post:
      tags:
        - API v1
        - Entities
      summary: Entity Lookup
      description: >-
        Resolve one Entity by an indexed Ontology identifier (LEI, CIK, SIREN,
        …).



        Pass exactly one scheme in `id`, or as a top-level shorthand:


        `{"id": {"lei": "95980020140005017502"}}`


        `{"lei": "95980020140005017502"}`



        Returns the same stub as `entity_search` (`id`, `name`, `entity_type`,
        `description`). Feed

        the `id` into `entity_retrieval` / `entity_introspection` for a full
        profile.



        Use this when: You have an external identifier and need the Entity id.
        For fuzzy name matching

        use `entity_search`; when you already have the UUID use
        `entity_retrieval`.
      operationId: entity_lookup
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LookupRequest'
        required: true
      responses:
        '200':
          description: Entity stub matching Entity Search
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Entity'
              example:
                id: d1715183-1d00-42c9-81c3-be3da24cdcf2
                name: MANGO MNG S.A.
                entity_type: Company
                description: >-
                  Spanish fashion retailer headquartered in Palau-solità i
                  Plegamans, Barcelona, founded in 1989.
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
    LookupRequest:
      properties:
        id:
          additionalProperties:
            type: string
          type: object
          title: Id
          description: >-
            Exactly one Ontology identifier scheme and its value, e.g. `{"lei":
            "95980020140005017502"}` or `{"cik": "320193"}` (CIK is
            zero-padded). Supported schemes: cik,
            companies_house_uk_company_number, lei, rssd_id, siren.
          examples:
            - lei: '95980020140005017502'
      additionalProperties: false
      type: object
      required:
        - id
      title: LookupRequest
      description: >-
        Resolve one Entity by an Ontology identifier scheme.


        ``id`` is a single-key object ``{ "<scheme>": "<value>" }`` (e.g.
        ``{"lei": "5493…"}``).

        A top-level shorthand ``{"lei": "5493…"}`` is accepted and normalised
        into ``id``.

        Integer values are coerced to strings (e.g. ``{"cik": 320193}``).
      example:
        id:
          lei: '95980020140005017502'
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