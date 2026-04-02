from __future__ import annotations

from typing import Any, Dict


MODEL_ID = "google/flan-t5-small"


def get_ai_insights(plan_payload: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI insights using Hugging Face Inference API.

    This helper is intentionally defensive:
    - If AI insights are disabled in settings, it returns a message noting that.
    - If no API token is configured, it returns a message explaining how to set one.
    - If the huggingface_hub package is missing, it returns an install hint.

    The actual text generation uses the hosted Inference API via
    huggingface_hub.InferenceClient and the google/flan-t5-small model.
    """

    enabled = bool(settings.get("enable_ai_insights", True))
    if not enabled:
        return {
            "enabled": False,
            "text": None,
            "error": "AI insights are disabled in settings.",
        }

    token = settings.get("hf_api_token") or ""
    if not token.strip():
        return {
            "enabled": False,
            "text": None,
            "error": "Hugging Face API token is not configured. Go to Settings and add your token.",
        }

    try:
        from huggingface_hub import InferenceClient
    except Exception as exc:  # pragma: no cover - environment dependent
        return {
            "enabled": False,
            "text": None,
            "error": (
                "huggingface_hub is not installed. Install it with 'pip install huggingface_hub' "
                f"and restart the app. ({exc})"
            ),
        }

    client = InferenceClient(MODEL_ID, token=token.strip())

    # The prompt will be refined in later parts once the full plan
    # structure is available. For now we accept a generic payload
    # and rely on the caller to prepare a concise description.
    prompt = plan_payload.get("prompt") or "Summarise the current plan."  # type: ignore[assignment]

    try:
        completion = client.text_generation(
            prompt,
            max_new_tokens=400,
            temperature=0.3,
        )
    except Exception as exc:  # pragma: no cover - network/remote errors
        return {
            "enabled": True,
            "text": None,
            "error": f"Error while calling Hugging Face Inference API: {exc}",
        }

    return {
        "enabled": True,
        "text": completion,
        "error": None,
    }
