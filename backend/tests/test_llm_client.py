from app.llm import Message, ToolCall, ToolResult
from app.llm.client import _contents


def test_tool_calls_and_results_go_back_to_gemini_as_function_parts():
    contents = _contents(
        [
            Message(role="user", text="Who backs GREÏ?"),
            Message(
                role="model",
                tool_calls=[
                    ToolCall(name="cala_search", args={"name": "GREÏ"}, id="c1", signature=b"sig")
                ],
            ),
            Message(
                role="user",
                text="Round 1 of 4.",
                tool_results=[ToolResult(name="cala_search", id="c1", output="GREÏ [Company]")],
            ),
        ]
    )

    assert [c.role for c in contents] == ["user", "model", "user"]
    assert contents[0].parts[0].text == "Who backs GREÏ?"
    call = contents[1].parts[0]
    # Gemini 3 rejects a replayed function call that lost its thought signature.
    assert (call.function_call.name, call.function_call.id, call.thought_signature) == (
        "cala_search",
        "c1",
        b"sig",
    )
    assert len(contents[1].parts) == 1  # no empty text part beside the call
    response, note = contents[2].parts
    assert response.function_response.response == {"result": "GREÏ [Company]"}
    assert note.text == "Round 1 of 4."


async def test_a_streamed_reply_tells_on_text_the_answer_so_far_and_keeps_its_parts():
    from google.genai import types

    from app.llm.client import GeminiLLM

    def chunk(*parts):
        return types.GenerateContentResponse(
            candidates=[types.Candidate(content=types.Content(role="model", parts=list(parts)))]
        )

    chunks = [
        chunk(types.Part(text="Looking for the fund", thought=True)),
        chunk(types.Part(text="root = Answer([t])\n")),
        chunk(types.Part(text='t = Text("Here.")')),
        chunk(
            types.Part(
                function_call=types.FunctionCall(name="cala_search", args={"name": "A"}),
                thought_signature=b"sig",
            )
        ),
    ]

    async def stream(**_):
        async def gen():
            for c in chunks:
                yield c

        return gen()

    llm = GeminiLLM(api_key="k", model="m", thoughts=True)
    llm._client.aio.models.generate_content_stream = stream
    seen: list[str] = []

    result = await llm.chat(
        system="s", messages=[Message(role="user", text="q")], on_text=seen.append
    )

    assert seen == ["root = Answer([t])\n", 'root = Answer([t])\nt = Text("Here.")']
    assert result.text == 'root = Answer([t])\nt = Text("Here.")'
    assert result.thoughts == "Looking for the fund"
    assert [(c.name, c.signature) for c in result.tool_calls] == [("cala_search", b"sig")]
