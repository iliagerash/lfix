from llmfixture.metadata import load_metadata
from llmfixture.metadata.loader import ModelStatus


def test_unknown_id_is_not_an_error() -> None:
    metadata = load_metadata()
    assert metadata.get_model("not-a-real-model-id") is None
    assert metadata.is_retired("not-a-real-model-id") is False


def test_deprecated_id_round_trips() -> None:
    metadata = load_metadata()
    record = metadata.get_model("claude-sonnet-4-20250514")
    assert record is not None
    assert record.provider == "anthropic"
    assert record.status is ModelStatus.eol
    assert record.eol == "2026-06-15"
    assert record.successor == "claude-sonnet-4-6"
    assert metadata.is_retired("claude-sonnet-4-20250514") is True


def test_current_id_is_not_retired() -> None:
    metadata = load_metadata()
    record = metadata.get_model("claude-sonnet-4-6")
    assert record is not None
    assert record.status is ModelStatus.current
    assert metadata.is_retired("claude-sonnet-4-6") is False
    assert metadata.is_risky_alias("claude-sonnet-4-6") is False


def test_snapshot_version_is_present() -> None:
    metadata = load_metadata()
    assert metadata.version == "2026.08.3"
    assert metadata.snapshot.generated_at == "2026-08-21"


def test_risky_aliases() -> None:
    metadata = load_metadata()
    assert metadata.is_risky_alias("latest") is True
    assert metadata.is_risky_alias("gpt-4o") is True
    assert metadata.is_risky_alias("some-model-latest") is True
    assert metadata.is_risky_alias("gpt-5.6-sol") is False


def test_openai_dated_snapshot() -> None:
    metadata = load_metadata()
    record = metadata.get_model("gpt-5-2025-08-07")
    assert record is not None
    assert record.status is ModelStatus.deprecated
    assert record.successor == "gpt-5.6-sol"


def test_sdk_table_is_nonempty() -> None:
    metadata = load_metadata()
    assert metadata.sdks
    assert metadata.sdks[0].symbol == "ChatCompletion.create"


def test_high_rows_follow_protocol() -> None:
    metadata = load_metadata()
    seen: set[str] = set()
    for key in metadata.models:
        record = metadata.get_model(key)
        assert record is not None
        if record.id in seen:
            continue
        seen.add(record.id)
        if record.status is ModelStatus.current:
            continue
        assert record.source
        assert record.successor
        if record.status is ModelStatus.eol:
            assert record.eol


def test_open_weights_survive_api_retirement() -> None:
    metadata = load_metadata()
    api = metadata.get_model("open-mistral-7b")
    weights = metadata.get_model("mistralai/Mistral-7B-Instruct-v0.3")
    assert api is not None and api.status is ModelStatus.eol
    assert weights is not None and weights.status is ModelStatus.current
    assert metadata.is_retired("open-mistral-7b") is True
    assert metadata.is_retired("mistralai/Mistral-7B-Instruct-v0.3") is False


def test_oss_current_ids() -> None:
    metadata = load_metadata()
    assert metadata.get_model("openai/gpt-oss-120b") is not None
    assert metadata.get_model("gpt-oss-120b") is not None
    assert metadata.is_retired("meta-llama/Llama-4-Scout-17B-16E-Instruct") is False
    assert metadata.is_risky_alias("llama3") is True
    assert metadata.is_risky_alias("Llama-4-Scout-17B-16E-Instruct") is False


def test_mistral_small_4_api_id() -> None:
    metadata = load_metadata()
    record = metadata.get_model("mistral-small-2603")
    assert record is not None
    assert record.status is ModelStatus.current
    assert record.source == "https://docs.mistral.ai/models/mistral-small-4-0-26-03"
    assert metadata.get_model("ministral-8b-2512") is not None
    assert metadata.get_model("ministral-3-8b") is None
