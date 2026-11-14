from app.api.transcribe import MAX_AUDIO_BYTES


def test_a_recording_comes_back_as_text(client):
    response = client.post(
        "/api/transcribe",
        content=b"\x1aE\xdf\xa3 fake webm",
        headers={"Content-Type": "audio/webm;codecs=opus"},
    )
    assert response.status_code == 200
    assert response.json() == {"text": "Drop consumer health"}


def test_the_codec_parameter_is_dropped_before_gemini(client):
    from app.llm import get_llm

    client.post(
        "/api/transcribe", content=b"ogg", headers={"Content-Type": "audio/ogg; codecs=opus"}
    )
    assert get_llm().calls[-1] == ("transcribe", "audio/ogg")


def test_an_empty_recording_is_rejected(client):
    response = client.post("/api/transcribe", content=b"", headers={"Content-Type": "audio/webm"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "empty_audio"


def test_a_body_that_is_not_audio_is_rejected(client):
    response = client.post("/api/transcribe", json={"text": "hi"})
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_media_type"


def test_a_recording_over_the_limit_is_rejected(client):
    response = client.post(
        "/api/transcribe",
        content=b"\0" * (MAX_AUDIO_BYTES + 1),
        headers={"Content-Type": "audio/webm"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "audio_too_large"


def test_a_gemini_failure_uses_the_error_shape(client, monkeypatch):
    from app.llm import LLMError, get_llm

    async def fail(**_):
        raise LLMError("transcribe: Gemini returned 503")

    monkeypatch.setattr(get_llm(), "transcribe", fail)
    response = client.post("/api/transcribe", content=b"x", headers={"Content-Type": "audio/webm"})
    assert response.status_code == 502
    assert response.json()["error"] == {
        "code": "transcription_failed",
        "message": "Grabbit could not transcribe that. Try again.",
    }


def test_live_transcription_is_unavailable_offline(client):
    response = client.post("/api/transcribe/token")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "live_transcription_unavailable"


def test_the_browser_gets_a_token_and_the_endpoint_that_takes_it(client, monkeypatch):
    from datetime import UTC, datetime

    from app.llm import LiveToken, get_llm

    async def live_token():
        return LiveToken(
            token="auth_tokens/abc",
            model="gemini-live-x",
            expires_at=datetime(2026, 11, 14, tzinfo=UTC),
        )

    monkeypatch.setattr(get_llm(), "live_token", live_token)
    body = client.post("/api/transcribe/token").json()
    assert body["token"] == "auth_tokens/abc" and body["model"] == "gemini-live-x"
    # Plain BidiGenerateContent rejects ephemeral tokens (1008).
    assert body["url"].endswith("GenerativeService.BidiGenerateContentConstrained")
    assert "key=" not in body["url"]
