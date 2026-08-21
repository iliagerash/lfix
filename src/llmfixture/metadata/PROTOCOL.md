# Metadata registry protocol

The files in `data/` are a **versioned editorial catalog**, not a scrape. The CLI never fetches them at runtime. Updates ship with a CLI release (or an explicit user-initiated update command later).

Canonical docs: OpenAI, Anthropic, Gemini, and Mistral deprecation pages; publisher model cards for open weights.

## Snapshot

- Version: `YYYY.MM.N` in `data/snapshot.json`. Bump `N` for any catalog change in the same month.
- `generated_at` is the edit date (`YYYY-MM-DD`).
- `sources` lists the pages used for this snapshot.
- Record every snapshot in `CHANGELOG.md` (what changed and why, not a dump of JSON).

## Record rules

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Exact string that appears in code / API calls |
| `provider` | yes | Must be listed in `data/providers.json` |
| `kind` | yes | `api` (hosted endpoint) or `open_weights` (downloadable weights) |
| `status` | yes | `current`, `deprecated`, or `eol` |
| `source` | yes if `deprecated` or `eol` | URL of the publisher page that states the status |
| `eol` | yes if `status` is `eol` | `YYYY-MM-DD` shutdown/retirement date |
| `successor` | yes if `deprecated` or `eol` | ID we recommend; add that ID as `current` in the same snapshot when it is ours to name |
| `aliases` | no | Other literals that mean this same record (HF id ↔ short name) |

Omit `context_window` / `max_output_tokens` unless the same `source` states them.

**HIGH bar** (`deprecated` / `eol`): prefer false negatives. If the page is vague, do not add a HIGH row.

## Hosted APIs vs open weights

These are different objects. Do not collapse them.

- **API id** (`kind: api`): HIGH only when *that host* publishes deprecation or retirement for *that id*. Example: `open-mistral-7b` retired on Mistral's API.
- **Weights id** (`kind: open_weights`): HIGH only when the *publisher* says the weights are retired or must not be used. Weights still on Hugging Face after an API shutdown stay `current`. Example: `mistralai/Mistral-7B-Instruct-v0.3` remains current after `open-mistral-7b` died.
- **Do not** copy Groq, Bedrock, Together, or Ollama host drop-offs onto Meta/Mistral/Google weight IDs. If we track a host-specific id, it gets that host as `provider` (add the provider first).

Unversioned tags (`llama3`, `mistral`, `latest`) belong in `aliases.json` (medium), not as HIGH.

## How to update

1. Open the publisher deprecation page or model card. Copy the URL.
2. Edit `data/models.json` / `aliases.json` / `sdks.json`. Keep ids unique across `id` and `aliases`.
3. If you need a new publisher, add it to `data/providers.json` first.
4. Bump `data/snapshot.json`.
5. Add a `CHANGELOG.md` section for this snapshot.
6. Run `pytest tests/test_metadata.py`. Do not ship if HIGH rows lack `source` / `successor`, or `eol` rows lack a date.

Cadence: with each CLI release. Emergency HIGH corrections can be a patch snapshot (`YYYY.MM.N+1`) without waiting for a feature release.

## Adding a provider

1. Add the slug to `data/providers.json` (`^[a-z][a-z0-9-]+$`).
2. Add current recommended ids so we do not flag good pins.
3. Add retired ids only from that publisher's own docs.
4. Note the provider in `CHANGELOG.md`.
