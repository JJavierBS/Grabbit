# Entity Introspection

>  Get the field schema for an entity by its UUID.

 Returns the available properties, relationships, and numerical observations you can use when querying the entity with ***Retrieve Entity***.


Examples:

 `GET /entities/c6772802-bdbc-4778-91e9-cd3d27d008d5/introspection`

 `GET /entities/e5bb591a-d308-4aa5-9672-96046d366cde/introspection`


Use this when you have an entity UUID and need to discover which attributes and relationships exist before querying. Use `retrieve_entity` for the full profile, `entity_search` first if you only have a name, or `entity_lookup` if you have an identifier (LEI, CIK, …). 



## OpenAPI

````yaml GET /v1/entities/{entity_id}/introspection
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
  /v1/entities/{entity_id}/introspection:
    get:
      tags:
        - API v1
        - Entities
      summary: Entity Introspection
      description: >-
        Get the field schema for a real-world entity by its UUID — the schema
        spans many domains,

        illustrative not exhaustive. Use to look up / find out what an entity is
        queryable for before

        pulling its profile. Returns the available properties, relationships,
        and numerical observations

        you can request from `entity_retrieval`.



        Examples:


        `GET /entities/c6772802-bdbc-4778-91e9-cd3d27d008d5/introspection`


        `GET /entities/e5bb591a-d308-4aa5-9672-96046d366cde/introspection`



        Use this when: You have an entity UUID and need to discover which
        attributes and relationships exist before

        querying. Use `entity_retrieval` to fetch data, `entity_search` first if
        you only have a name, or

        `entity_lookup` if you have an Ontology identifier (LEI, CIK, …).
      operationId: entity_introspection
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
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/IntrospectionResponse'
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
    IntrospectionResponse:
      properties:
        properties:
          items:
            type: string
          type: array
          title: Properties
          description: >-
            List of property names available for this entity (e.g. id, name,
            currency).
          examples:
            - - cik
              - headquarters_address
              - lei
              - registered_address
              - founding_date
              - esg_policy
              - legal_name
              - employee_count
              - bics
              - name
              - aliases
              - id
        relationships:
          $ref: '#/components/schemas/IntrospectionEntityRelationships'
          description: Outgoing and incoming relationship types.
        numerical_observations:
          additionalProperties: true
          type: object
          title: Numerical Observations
          description: List of numerical observation names available for this entity.
          examples:
            - FinancialMetric:
                - cadence: i
                  description: >-
                    Amount of currency on hand as well as demand deposits with
                    banks or financial institutions. Includes other kinds of
                    accounts that have the general characteristics of demand
                    deposits. Also includes short-term, highly liquid
                    investments that are both readily convertible to known
                    amounts of cash and so near their maturity that they present
                    insignificant risk of changes in value because of changes in
                    interest rates. Excludes cash and cash equivalents within
                    disposal group and discontinued operation.
                  id: 1d3eae40-0ba8-5baf-9907-6a4823b067bb
                  name: Cash and Cash Equivalents, at Carrying Value
                  taxonomy: us-gaap
                  unit: USD
      type: object
      required:
        - properties
        - relationships
        - numerical_observations
      title: IntrospectionResponse
      description: Response containing the introspection of an entity.
      example:
        numerical_observations:
          FinancialMetric:
            - cadence: i
              description: >-
                Amount of currency on hand as well as demand deposits with banks
                or financial institutions. Includes other kinds of accounts that
                have the general characteristics of demand deposits. Also
                includes short-term, highly liquid investments that are both
                readily convertible to known amounts of cash and so near their
                maturity that they present insignificant risk of changes in
                value because of changes in interest rates. Excludes cash and
                cash equivalents within disposal group and discontinued
                operation.
              id: 1d3eae40-0ba8-5baf-9907-6a4823b067bb
              name: Cash and Cash Equivalents, at Carrying Value
              taxonomy: us-gaap
              unit: USD
        properties:
          - cik
          - headquarters_address
          - lei
          - registered_address
          - founding_date
          - esg_policy
          - legal_name
          - employee_count
          - bics
          - name
          - aliases
          - id
        relationships:
          incoming:
            - IS_CFO_OF
            - IS_SUBSIDIARY_OF
            - IS_BOARD_MEMBER_OF
            - IS_BENEFICIARY_OWNER_OF
            - IS_CEO_OF
          outgoing:
            - IS_ULTIMATE_PARENT_OF
            - IS_REGISTERED_IN
            - OPERATES_IN_INDUSTRY
            - IS_DIRECT_PARENT_OF
            - IS_BENEFICIARY_OWNER_OF
            - HAS_HEADQUARTERS_IN
            - PARTICIPATES_IN_CORPORATE_EVENT
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
    IntrospectionEntityRelationships:
      properties:
        outgoing:
          items:
            type: string
          type: array
          title: Outgoing
          description: Outgoing relationship type names.
          examples:
            - - IS_ULTIMATE_PARENT_OF
              - IS_REGISTERED_IN
              - OPERATES_IN_INDUSTRY
              - IS_DIRECT_PARENT_OF
              - IS_BENEFICIARY_OWNER_OF
              - HAS_HEADQUARTERS_IN
              - PARTICIPATES_IN_CORPORATE_EVENT
        incoming:
          items:
            type: string
          type: array
          title: Incoming
          description: Incoming relationship type names.
          examples:
            - - IS_CFO_OF
              - IS_SUBSIDIARY_OF
              - IS_BOARD_MEMBER_OF
              - IS_BENEFICIARY_OWNER_OF
              - IS_CEO_OF
      type: object
      title: IntrospectionEntityRelationships
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