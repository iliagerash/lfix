# LLM Fixture

Catches deprecated model IDs, broken structured-output schemas, and fragile MCP tools before they reach production.

A local-first CLI — **ESLint + pytest for LLM integrations**. Your application code may not change, but your AI dependencies can. `lfix` checks the parts of an AI app that traditional CI does not understand.

**Status:** early development. The CLI installs and reports a version today. Scanner, MCP linter, and schema tests are the next milestones.

## Install

Python 3.11 or newer. Install with **pipx** so `lfix` is on your PATH and works from any folder:

```bash
pipx install git+https://github.com/iliagerash/lfix.git
lfix --version
```

From a local clone (editable: the command tracks this checkout):

```bash
cd lfix
pipx install --editable .
```

After that, `cd` into any project and run `lfix scan`. You do not need to stay in this repo.
If the shell cannot find `lfix`, run `pipx ensurepath` and open a new terminal.

Without pipx, `python3 -m pip install --user git+https://github.com/iliagerash/lfix.git` also works if `$(python3 -m site --user-base)/bin` is on your PATH.

No account. No API keys. No telemetry.

## What it will check

| Command | What it does | Keys required |
|---|---|---|
| `lfix scan ./src` | Deprecated model IDs, risky aliases (`latest`), SDK rot, missing schema/prompt coverage | No |
| `lfix mcp lint ./tools.json` | MCP tool overlap, schema quality, naming, token cost | No |
| `lfix schema test …` | Structured-output compatibility across models | Your provider keys, locally |
| `lfix ci` | Run fixtures from `lfix.yml`; non-zero exit when thresholds fail | No (unless a schema fixture is configured) |

`lfix scan` and `lfix mcp lint` run fully locally. They do not send source code, manifests, schemas, prompts, file names, or findings anywhere.

## Example (intended)

```text
AI Codebase Scan — 47 files, 12 model calls, 8 schema files

HIGH    src/ai/resume-parser.ts:14
        Deprecated model: claude-sonnet-4-20250514
        EOL: 2026-08-01. Successor: claude-sonnet-4-6.

MEDIUM  src/ai/classifier.ts:8
        Model alias "latest" tracks provider updates silently.
        Pin to a versioned model ID for reproducible behavior.
```

## Config

Commit `lfix.yml` and run the same checks locally or in CI:

```yaml
project: hiring-assistant
fail_on: high

fixtures:
  - name: codebase_scan
    type: scan
    paths: [./src, ./prompts, ./schemas]
  - name: mcp_tools
    type: mcp
    config: ./mcp-server/tools.json
```

```yaml
# .github/workflows/lfix.yml (coming)
- run: lfix ci
```

## This is not

LLM observability, a production proxy, a prompt CMS, a model router, or a generic eval framework. No tracing, session replay, RAG scoring, or red-teaming.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
mypy
```

## License

[MIT](LICENSE)
