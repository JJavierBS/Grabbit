"""Talk: the browser records, Gemini writes down what was said (works in every browser)."""

import logging

from fastapi import APIRouter, Request

from app.api.errors import ApiError
from app.llm import LLMError, get_llm
from app.models import ErrorResponse, LiveTranscription, Transcript

log = logging.getLogger(__name__)

router = APIRouter(prefix="/transcribe", tags=["chat"])

# About ten minutes of Opus at browser bitrates; a Talk turn is a sentence or two.
MAX_AUDIO_BYTES = 10 * 1024 * 1024

_AUDIO_BODY = {
    "requestBody": {
        "required": True,
        "content": {"audio/*": {"schema": {"type": "string", "format": "binary"}}},
    }
}


@router.post("", openapi_extra=_AUDIO_BODY)
async def post_transcribe(request: Request) -> Transcript:
    # MediaRecorder sends e.g. "audio/webm;codecs=opus"; Gemini wants the bare type.
    mime_type = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if not mime_type.startswith("audio/"):
        raise ApiError(415, "unsupported_media_type", "Send the recording as audio.")
    audio = await _read_limited(request)
    if not audio:
        raise ApiError(400, "empty_audio", "The recording is empty. Press Talk and speak.")
    try:
        text = await get_llm().transcribe(audio=audio, mime_type=mime_type)
    except LLMError as exc:
        log.warning("transcribe failed: %s", exc)
        raise ApiError(
            502, "transcription_failed", "Grabbit could not transcribe that. Try again."
        ) from exc
    return Transcript(text=text.strip())


# Browsers authenticate with an ephemeral token, which only this "Constrained" endpoint takes.
LIVE_URL = (
    "wss://generativelanguage.googleapis.com/ws/"
    "google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContentConstrained"
)


@router.post("/token", responses={503: {"model": ErrorResponse}})
async def post_transcribe_token() -> LiveTranscription:
    """Live Talk: the browser streams the mic straight to Gemini with this single-use token."""
    try:
        live = await get_llm().live_token()
    except LLMError as exc:
        log.info("live transcription unavailable: %s", exc)
        raise ApiError(
            503, "live_transcription_unavailable", "Live transcription is not available now."
        ) from exc
    return LiveTranscription(
        url=LIVE_URL, token=live.token, model=live.model, expires_at=live.expires_at
    )


async def _read_limited(request: Request) -> bytes:
    audio = bytearray()
    async for chunk in request.stream():
        audio += chunk
        if len(audio) > MAX_AUDIO_BYTES:
            raise ApiError(413, "audio_too_large", "The recording is too long. Keep it short.")
    return bytes(audio)
