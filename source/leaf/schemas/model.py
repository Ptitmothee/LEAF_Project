"""Data schema representing AI model specifications and telemetry capabilities."""

from dataclasses import asdict, dataclass, field

from leaf.typing import JsonDict, ModelSpecID


@dataclass
class ModelSpec:
    """Specification of an AI model used for code generation.

    Attributes:
        model_id: Unique benchmark identifier (e.g. 'openai:gpt-4o-2024-08-06', 'ollama:qwen2.5-coder-7b').
        provider: Organization or runtime provider ('openai', 'anthropic', 'google', 'ollama', 'mock').
        display_name: Human-friendly name for reporting.
        api_model_name: Exact string sent in API or local runtime queries.
        is_local: True if running on local hardware (permitting machine power measurement),
            False if cloud API.
        release_date: Official public release date (YYYY-MM-DD).
        knowledge_cutoff: Declared knowledge cutoff date if documented.
        pricing_input_per_million: Billed price in USD per 1M input tokens as of benchmark date.
        pricing_output_per_million: Billed price in USD per 1M output tokens as of benchmark date.
        supports_reasoning_tokens: True if provider telemetry separates reasoning/thinking tokens.
        metadata: Provider-specific auxiliary configuration.
    """

    model_id: ModelSpecID
    provider: str
    display_name: str
    api_model_name: str
    is_local: bool = False
    release_date: str | None = None
    knowledge_cutoff: str | None = None
    pricing_input_per_million: float | None = None
    pricing_output_per_million: float | None = None
    supports_reasoning_tokens: bool = False
    metadata: JsonDict = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        """Serialize model specification to dictionary."""
        return {
            "schema_version": "1.0.0",
            **asdict(self),
        }

    @classmethod
    def from_dict(cls, data: JsonDict) -> ModelSpec:
        """Instantiate model specification from dictionary."""
        return cls(
            model_id=str(data["model_id"]),
            provider=str(data["provider"]),
            display_name=str(data["display_name"]),
            api_model_name=str(data["api_model_name"]),
            is_local=bool(data.get("is_local", False)),
            release_date=data.get("release_date"),
            knowledge_cutoff=data.get("knowledge_cutoff"),
            pricing_input_per_million=float(data["pricing_input_per_million"]) if data.get("pricing_input_per_million") is not None else None,
            pricing_output_per_million=float(data["pricing_output_per_million"]) if data.get("pricing_output_per_million") is not None else None,
            supports_reasoning_tokens=bool(data.get("supports_reasoning_tokens", False)),
            metadata=dict(data.get("metadata", {})),
        )
