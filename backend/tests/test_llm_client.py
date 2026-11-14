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
