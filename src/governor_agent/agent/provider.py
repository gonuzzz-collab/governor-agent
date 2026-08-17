"""Explicit model-provider boundary."""

from __future__ import annotations

from strands.models import BedrockModel, Model


def create_bedrock_model(*, model_id: str, region_name: str) -> Model:
    """Create a low-variance Bedrock provider without making a model call."""

    if not model_id.strip() or not region_name.strip():
        raise ValueError("Bedrock model ID and region are required")
    return BedrockModel(
        model_id=model_id,
        region_name=region_name,
        temperature=0.0,
    )
