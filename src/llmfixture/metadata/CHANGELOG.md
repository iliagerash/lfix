# Metadata changelog

See `PROTOCOL.md` for how to update this catalog.

## 2026.08.3 (2026-08-21)

- Verified `mistral-small-2603` against Mistral changelog (16 Mar 2026) and the [Small 4 model card](https://docs.mistral.ai/models/mistral-small-4-0-26-03). That is the API id for Mistral Small 4.
- Replaced inferred `ministral-3-8b` with `ministral-8b-2512` (changelog, 2 Dec 2025: Ministral 3 released as `ministral-3b-2512`, `ministral-8b-2512`, `ministral-14b-2512`).

## 2026.08.2 (2026-08-21)

- Documented the update protocol (`PROTOCOL.md`).
- Every `deprecated`/`eol` row now requires `source` and `successor`; `eol` requires a date. Loader enforces this.
- Split `kind`: `api` vs `open_weights`. An API shutdown does not retire downloadable weights.
- Added open-weight current IDs: Llama 4 Scout/Maverick, Llama 3.3, gpt-oss, Gemma 3, DeepSeek-V3, Qwen2.5-72B, Phi-4, Mistral 7B weights.
- Added Mistral API retirements from Mistral docs (`open-mistral-7b`, Mixtral API ids, older `mistral-small-*`). Weights for Mistral 7B stay `current`.
- Unversioned local tags (`llama3`, `mistral`, `gemma`, …) are aliases, not HIGH.

## 2026.08.1 (2026-08-21)

Sources: OpenAI, Anthropic, and Gemini official deprecation pages.

HIGH only when the vendor page lists a shutdown or retirement date.

- Anthropic retired IDs, including `claude-sonnet-4-20250514` → `claude-sonnet-4-6`.
- OpenAI chat/reasoning IDs with announced 2026 shutdowns, plus already-shut aliases.
- Gemini 1.5 and 2.0 Flash IDs listed as shut down. `gemini-2.5-flash` kept **current**.
