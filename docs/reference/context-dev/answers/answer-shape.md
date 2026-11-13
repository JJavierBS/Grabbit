# Answer shape

> Describe the answer using an example JSON object.

`json_format` is an example object with placeholder values. It is not JSON Schema; if you send a JSON Schema object, Answers converts it to an example first. Answers preserves its keys and value types; facts that cannot be established can be `null`.

## Describe a comparison

Send this body to `POST /web/answers`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "mode": "ultra",
  "task": "Compare the documented API authentication methods for Stripe and GitHub.",
  "json_format": {
    "services": [
      {
        "name": "",
        "authentication_methods": [
          ""
        ],
        "docs_url": ""
      }
    ]
  }
}
```

Use strings for text, numbers for numeric facts, booleans for yes/no questions, and an example item to shape an array. An empty array accepts arbitrary JSON items. Without `json_format`, the default is `{"result":""}`.

## Limits

The example can contain up to eight nesting levels, 500 nodes, and 16,000 serialized characters. Every object, array, and value counts as a node, including the root object. The task is limited to 2,000 characters. Keep related facts together and ask for source URLs when you need to attribute individual fields.

Validate the response in your application, including nullable facts. A valid shape does not guarantee every value was found. Review the [sources](https://docs.context.dev/answers/sources-and-deadlines.md) before acting on an answer.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.