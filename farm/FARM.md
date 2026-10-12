# Agent Farm format (schema 1)

This is the authoritative spec for everything under `farm/`. The Dynapps
backend parser and `tools/farm-lint.py` are both written from it. Every
mapping below rejects unknown keys: an unrecognised key is an error, never
ignored.

```
farm/
  farm.yaml                 farm manifest
  agents/<agent_id>.md      one agent per file (YAML frontmatter + system prompt body)
  evals/<agent_id>.yaml     eval suite for that agent (optional)
  fixtures/<name>/          workspace seed copied into each run
  fixtures/README.md        ground truth; never copied into a workspace
```

Identifiers (`agent_id`, fixture names) match `^[a-z][a-z0-9_]{2,63}$`.

## farm.yaml

| key | type | required | meaning |
|-----|------|----------|---------|
| `schema` | int | yes | must be `1` |
| `id` | string | yes | farm id, `^[a-z][a-z0-9-]{2,63}$` |
| `marketplace` | string | yes | marketplace id from `.claude-plugin/marketplace.json`; entitlement to it gates every run |
| `defaults` | map | no | fallbacks for agents: `model`, `max_turns`, `max_budget_usd`, `permission_mode` (same types as the agent keys) |
| `agents` | list[string] | yes | agent ids; each must have `agents/<id>.md`, and every agent file must be listed |

## agents/<agent_id>.md

A YAML frontmatter block between `---` lines, then the body. The body is the
agent's **system prompt**, passed verbatim.

| key | type | required | meaning |
|-----|------|----------|---------|
| `name` | string | yes | equals the file stem, `^[a-z][a-z0-9_]{2,63}$` |
| `description` | string | yes | one line, shown in the dashboard |
| `model` | string | no | model id; falls back to `defaults.model` |
| `tools` | list[string] | yes, non-empty | Claude Code tool names (`Read`, `Grep`, `Glob`, `Write`, `Edit`, `MultiEdit`, `Bash`, `WebFetch`, `WebSearch`, `TodoWrite`, `NotebookEdit`, `Task`, `Skill`). Becomes `--allowedTools` and the allowlist oracle for `no_tool_outside_allowlist`. `Skill` is always allowed implicitly. |
| `plugin` | string | yes | plugin id; `plugins/<plugin>/` must exist in this kit |
| `skills` | list[string] | no | skill ids; each `plugins/<plugin>/skills/<id>/` must exist |
| `entry_prompt` | string | yes | the user prompt for a run. Placeholders: `{{fixture_path}}` (absolute workspace root) and `{{case.prompt}}` (the eval case or API caller's prompt; empty string when none) |
| `fixture` | string | yes | default fixture name under `fixtures/` |
| `max_turns` | int > 0 | no | falls back to `defaults.max_turns` |
| `max_budget_usd` | number > 0 | no | falls back to `defaults.max_budget_usd` |
| `permission_mode` | enum | no | `default`, `acceptEdits`, `plan`, `bypassPermissions`; falls back to `defaults.permission_mode` |
| `output` | map | no | `{path, format}`: `path` relative to the workspace, `format` is `markdown` or `json` |

## evals/<agent_id>.yaml

| key | type | required | meaning |
|-----|------|----------|---------|
| `schema` | int | yes | `1` |
| `agent` | string | yes | agent id; must exist |
| `cases` | list | yes, non-empty | see below |

Case keys:

| key | type | required | meaning |
|-----|------|----------|---------|
| `id` | string | yes | `^[a-z0-9_]+$`, unique in the file |
| `prompt` | string | no | substituted for `{{case.prompt}}` |
| `fixture` | string | no | overrides the agent's fixture; must exist |
| `timeout_secs` | int > 0 | no | wall-clock limit for the run (default 900) |
| `assertions` | list | yes | closed set below; evaluated after the run |
| `judge_rubric` | string | no | LLM judge instructions; the judge sees the rubric, the prompt and the output file, nothing else |
| `judge_threshold` | int 0–100 | no | pass mark for the judge score, default 70; only meaningful with `judge_rubric` |

Assertions (each is a map with `type` plus the listed keys; nothing else):

| type | keys | passes when |
|------|------|-------------|
| `file_exists` | `path` | the workspace file exists after the run |
| `output_contains` | `path?`, `text` | the file (default: the agent's `output.path`, else the final result text) contains `text` literally |
| `regex` | `path?`, `pattern` | the same target matches the pattern (Rust `regex` syntax, case-sensitive unless `(?i)`) |
| `no_tool_outside_allowlist` | — | every `tool_use` in the run used a tool in the agent's `tools` (or `Skill`) |
| `max_turns` | `value` (int) | the run's `num_turns` ≤ value |
| `max_cost_usd` | `value` (number) | the run's cost ≤ value |
| `skill_invoked` | `skill` | a `Skill` tool_use named that skill (bare id or `plugin:skill`, dash or underscore spelling) |

A case passes when every assertion passes and, if a rubric is set, the judge
score ≥ threshold.

All `path` values are relative, contain no `..`, and are not absolute.

## fixtures/

- Each subdirectory is a fixture; it is copied verbatim into the run
  workspace, which becomes the run's cwd and `{{fixture_path}}`.
- `fixtures/README.md` is never copied.
- No symlinks anywhere under `farm/`, no path component `..`.
- Keep fixtures small (the sync caps the farm at 256 files / 8 MiB).
