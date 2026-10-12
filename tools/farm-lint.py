#!/usr/bin/env python3
"""Validate the farm/ directory of an Agent Farm kit against farm/FARM.md.

Usage: farm-lint.py [--root KIT_ROOT] [--strict]

Prints GitHub annotation lines (::error / ::warning file=...,line=...::msg).
Exit status is 1 when errors are found and --strict is set, else 0.
Requires python3 (stdlib) and PyYAML.
"""
import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("::error::farm-lint requires PyYAML (pip install pyyaml)")
    sys.exit(2)

ID_RE = re.compile(r"^[a-z][a-z0-9_]{2,63}$")
FARM_ID_RE = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
CASE_ID_RE = re.compile(r"^[a-z0-9_]+$")
TOOLS = {"Read", "Grep", "Glob", "Write", "Edit", "MultiEdit", "Bash", "WebFetch",
         "WebSearch", "TodoWrite", "NotebookEdit", "Task", "Skill"}
PERMISSION_MODES = {"default", "acceptEdits", "plan", "bypassPermissions"}
OUTPUT_FORMATS = {"markdown", "json"}
PLACEHOLDER_RE = re.compile(r"\{\{\s*([^}]*?)\s*\}\}")
PLACEHOLDERS = {"fixture_path", "case.prompt"}
NON_RUST_REGEX = re.compile(r"\(\?[=!<]|\\[1-9]")

FARM_KEYS = {"schema", "id", "marketplace", "defaults", "agents"}
DEFAULT_KEYS = {"model", "max_turns", "max_budget_usd", "permission_mode"}
AGENT_KEYS = {"name", "description", "model", "tools", "plugin", "skills", "entry_prompt",
              "fixture", "max_turns", "max_budget_usd", "permission_mode", "output"}
AGENT_REQUIRED = {"name", "description", "tools", "plugin", "entry_prompt", "fixture"}
EVAL_KEYS = {"schema", "agent", "cases"}
CASE_KEYS = {"id", "prompt", "fixture", "timeout_secs", "assertions", "judge_rubric",
             "judge_threshold"}
ASSERTIONS = {
    "file_exists": ({"path"}, set()),
    "output_contains": ({"text"}, {"path"}),
    "regex": ({"pattern"}, {"path"}),
    "no_tool_outside_allowlist": (set(), set()),
    "max_turns": ({"value"}, set()),
    "max_cost_usd": ({"value"}, set()),
    "skill_invoked": ({"skill"}, set()),
}


class Lint:
    def __init__(self, root):
        self.root = root
        self.errors = 0
        self.warnings = 0

    def rel(self, path):
        return os.path.relpath(path, self.root)

    def error(self, path, msg, line=1):
        self.errors += 1
        print(f"::error file={self.rel(path)},line={line}::{msg}")

    def warn(self, path, msg, line=1):
        self.warnings += 1
        print(f"::warning file={self.rel(path)},line={line}::{msg}")


def key_line(text, key, offset=0):
    m = re.search(rf"^\s*-?\s*{re.escape(key)}\s*:", text, re.M)
    return text.count("\n", 0, m.start()) + 1 + offset if m else 1 + offset


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def check_rel_path(lint, f, value, what, line):
    if not isinstance(value, str) or not value:
        lint.error(f, f"{what} must be a non-empty string", line)
    elif os.path.isabs(value) or ".." in value.replace("\\", "/").split("/"):
        lint.error(f, f"{what} '{value}' must be relative and contain no '..'", line)


def check_defaults_like(lint, f, data, text, offset=0):
    if "model" in data and (not isinstance(data["model"], str) or not data["model"]):
        lint.error(f, "model must be a non-empty string", key_line(text, "model", offset))
    if "max_turns" in data and (not is_int(data["max_turns"]) or data["max_turns"] <= 0):
        lint.error(f, "max_turns must be a positive integer", key_line(text, "max_turns", offset))
    if "max_budget_usd" in data and (not is_num(data["max_budget_usd"]) or data["max_budget_usd"] <= 0):
        lint.error(f, "max_budget_usd must be a positive number", key_line(text, "max_budget_usd", offset))
    if "permission_mode" in data and data["permission_mode"] not in PERMISSION_MODES:
        lint.error(f, f"permission_mode must be one of {sorted(PERMISSION_MODES)}",
                   key_line(text, "permission_mode", offset))


def load_yaml(lint, path):
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        return yaml.safe_load(text), text
    except yaml.YAMLError as exc:
        line = getattr(getattr(exc, "problem_mark", None), "line", 0) + 1
        lint.error(path, f"invalid YAML: {exc}", line)
    except OSError as exc:
        lint.error(path, f"cannot read: {exc}")
    return None, ""


def check_farm_yaml(lint, farm_dir):
    path = os.path.join(farm_dir, "farm.yaml")
    if not os.path.isfile(path):
        lint.error(path, "farm/farm.yaml is missing")
        return None
    data, text = load_yaml(lint, path)
    if not isinstance(data, dict):
        lint.error(path, "farm.yaml must be a mapping")
        return None
    for k in sorted(set(data) - FARM_KEYS):
        lint.error(path, f"unknown key '{k}'", key_line(text, k))
    for k in sorted(FARM_KEYS - {"defaults"} - set(data)):
        lint.error(path, f"missing required key '{k}'")
    if data.get("schema") != 1:
        lint.error(path, "schema must be 1", key_line(text, "schema"))
    if "id" in data and not (isinstance(data["id"], str) and FARM_ID_RE.match(data["id"])):
        lint.error(path, f"id must match {FARM_ID_RE.pattern}", key_line(text, "id"))
    if "marketplace" in data:
        check_marketplace(lint, path, data["marketplace"], key_line(text, "marketplace"))
    defaults = data.get("defaults") or {}
    if not isinstance(defaults, dict):
        lint.error(path, "defaults must be a mapping", key_line(text, "defaults"))
        defaults = {}
    for k in sorted(set(defaults) - DEFAULT_KEYS):
        lint.error(path, f"unknown defaults key '{k}'", key_line(text, k))
    check_defaults_like(lint, path, defaults, text)
    agents = data.get("agents")
    if not isinstance(agents, list) or not agents or not all(isinstance(a, str) for a in agents):
        lint.error(path, "agents must be a non-empty list of agent ids", key_line(text, "agents"))
        agents = []
    if len(set(agents)) != len(agents):
        lint.error(path, "agents contains duplicate ids", key_line(text, "agents"))
    data["defaults"] = defaults
    data["agents"] = agents
    data["_text"] = text
    return data


def check_marketplace(lint, path, marketplace, line):
    mp = os.path.join(lint.root, ".claude-plugin", "marketplace.json")
    if not isinstance(marketplace, str) or not marketplace:
        lint.error(path, "marketplace must be a non-empty string", line)
        return
    if not os.path.isfile(mp):
        lint.warn(path, ".claude-plugin/marketplace.json not found; marketplace id not checked", line)
        return
    import json
    try:
        with open(mp, encoding="utf-8") as fh:
            name = json.load(fh).get("name")
    except (OSError, ValueError) as exc:
        lint.warn(path, f"cannot read marketplace.json: {exc}", line)
        return
    if name != marketplace:
        lint.error(path, f"marketplace '{marketplace}' does not match marketplace.json name '{name}'", line)


def split_frontmatter(text):
    if not text.startswith("---\n"):
        return None, None, 0
    end = text.find("\n---\n", 4)
    if end == -1:
        if text.rstrip().endswith("\n---"):
            end = text.rstrip().rfind("\n---")
        else:
            return None, None, 0
    return text[4:end + 1], text[end + 5:], 1


def check_agent(lint, farm_dir, agent_id, farm):
    path = os.path.join(farm_dir, "agents", f"{agent_id}.md")
    if not ID_RE.match(agent_id):
        lint.error(os.path.join(farm_dir, "farm.yaml"), f"agent id '{agent_id}' must match {ID_RE.pattern}",
                   key_line(farm["_text"], agent_id))
    if not os.path.isfile(path):
        lint.error(os.path.join(farm_dir, "farm.yaml"), f"agent '{agent_id}' has no agents/{agent_id}.md",
                   key_line(farm["_text"], agent_id))
        return None
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    fm_text, body, offset = split_frontmatter(text)
    if fm_text is None:
        lint.error(path, "missing YAML frontmatter delimited by '---' lines")
        return None
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        line = getattr(getattr(exc, "problem_mark", None), "line", 0) + 2
        lint.error(path, f"invalid frontmatter YAML: {exc}", line)
        return None
    if not isinstance(fm, dict):
        lint.error(path, "frontmatter must be a mapping")
        return None
    kl = lambda k: key_line(fm_text, k, offset)  # noqa: E731
    for k in sorted(set(fm) - AGENT_KEYS):
        lint.error(path, f"unknown key '{k}'", kl(k))
    for k in sorted(AGENT_REQUIRED - set(fm)):
        lint.error(path, f"missing required key '{k}'")
    if fm.get("name") != agent_id:
        lint.error(path, f"name '{fm.get('name')}' must equal the file stem '{agent_id}'", kl("name"))
    if "description" in fm and (not isinstance(fm["description"], str) or not fm["description"].strip()):
        lint.error(path, "description must be a non-empty string", kl("description"))
    tools = fm.get("tools")
    if "tools" in fm:
        if not isinstance(tools, list) or not tools or not all(isinstance(t, str) for t in tools):
            lint.error(path, "tools must be a non-empty list of tool names", kl("tools"))
        else:
            for t in tools:
                if t not in TOOLS and not t.startswith("mcp__"):
                    lint.error(path, f"unknown Claude Code tool '{t}'", kl("tools"))
    check_defaults_like(lint, path, fm, fm_text, offset)
    plugin = fm.get("plugin")
    plugin_dir = os.path.join(lint.root, "plugins", plugin) if isinstance(plugin, str) else None
    if "plugin" in fm and (not plugin_dir or not os.path.isdir(plugin_dir)):
        lint.error(path, f"plugin '{plugin}' not found under plugins/", kl("plugin"))
        plugin_dir = None
    skills = fm.get("skills", [])
    if not isinstance(skills, list) or not all(isinstance(s, str) for s in skills):
        lint.error(path, "skills must be a list of skill ids", kl("skills"))
    elif plugin_dir:
        for s in skills:
            if not os.path.isdir(os.path.join(plugin_dir, "skills", s)):
                lint.error(path, f"skill '{s}' not found under plugins/{plugin}/skills/", kl("skills"))
    ep = fm.get("entry_prompt")
    if "entry_prompt" in fm:
        if not isinstance(ep, str) or not ep.strip():
            lint.error(path, "entry_prompt must be a non-empty string", kl("entry_prompt"))
        else:
            for ph in PLACEHOLDER_RE.findall(ep):
                if ph not in PLACEHOLDERS:
                    lint.error(path, f"unknown placeholder '{{{{{ph}}}}}' (allowed: {sorted(PLACEHOLDERS)})",
                               kl("entry_prompt"))
    fixture = fm.get("fixture")
    if "fixture" in fm and not fixture_exists(farm_dir, fixture):
        lint.error(path, f"fixture '{fixture}' not found under farm/fixtures/", kl("fixture"))
    out = fm.get("output")
    if out is not None:
        if not isinstance(out, dict):
            lint.error(path, "output must be a mapping {path, format}", kl("output"))
        else:
            for k in sorted(set(out) - {"path", "format"}):
                lint.error(path, f"unknown output key '{k}'", kl("output"))
            check_rel_path(lint, path, out.get("path"), "output.path", kl("output"))
            if out.get("format") not in OUTPUT_FORMATS:
                lint.error(path, f"output.format must be one of {sorted(OUTPUT_FORMATS)}", kl("output"))
    if not body or not body.strip():
        lint.error(path, "agent body (system prompt) is empty")
    merged = dict(farm.get("defaults", {}))
    merged.update(fm)
    if "model" not in merged:
        lint.error(path, "no model set and farm.yaml has no defaults.model")
    return merged


def fixture_exists(farm_dir, name):
    return isinstance(name, str) and ID_RE.match(name) is not None and \
        os.path.isdir(os.path.join(farm_dir, "fixtures", name))


def check_eval(lint, farm_dir, path, agents):
    data, text = load_yaml(lint, path)
    if data is None and text == "":
        return
    if not isinstance(data, dict):
        lint.error(path, "eval file must be a mapping")
        return
    for k in sorted(set(data) - EVAL_KEYS):
        lint.error(path, f"unknown key '{k}'", key_line(text, k))
    for k in sorted(EVAL_KEYS - set(data)):
        lint.error(path, f"missing required key '{k}'")
    if data.get("schema") != 1:
        lint.error(path, "schema must be 1", key_line(text, "schema"))
    agent_id = data.get("agent")
    stem = os.path.splitext(os.path.basename(path))[0]
    if agent_id not in agents:
        lint.error(path, f"agent '{agent_id}' is not a farm agent", key_line(text, "agent"))
    elif agent_id != stem:
        lint.error(path, f"eval file name must be <agent_id>.yaml ('{agent_id}.yaml')", key_line(text, "agent"))
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        lint.error(path, "cases must be a non-empty list", key_line(text, "cases"))
        return
    seen = set()
    lines = text.splitlines()
    for idx, case in enumerate(cases):
        cid = case.get("id") if isinstance(case, dict) else None
        line = case_line(lines, cid, idx)
        if not isinstance(case, dict):
            lint.error(path, f"case #{idx + 1} must be a mapping", line)
            continue
        for k in sorted(set(case) - CASE_KEYS):
            lint.error(path, f"case '{cid}': unknown key '{k}'", line)
        if not isinstance(cid, str) or not CASE_ID_RE.match(cid):
            lint.error(path, f"case #{idx + 1}: id must match {CASE_ID_RE.pattern}", line)
        elif cid in seen:
            lint.error(path, f"duplicate case id '{cid}'", line)
        seen.add(cid)
        if "prompt" in case and not isinstance(case["prompt"], str):
            lint.error(path, f"case '{cid}': prompt must be a string", line)
        if "fixture" in case and not fixture_exists(farm_dir, case["fixture"]):
            lint.error(path, f"case '{cid}': fixture '{case['fixture']}' not found", line)
        if "timeout_secs" in case and (not is_int(case["timeout_secs"]) or case["timeout_secs"] <= 0):
            lint.error(path, f"case '{cid}': timeout_secs must be a positive integer", line)
        if "judge_rubric" in case and (not isinstance(case["judge_rubric"], str) or not case["judge_rubric"].strip()):
            lint.error(path, f"case '{cid}': judge_rubric must be a non-empty string", line)
        if "judge_threshold" in case:
            jt = case["judge_threshold"]
            if not is_num(jt) or not 0 <= jt <= 100:
                lint.error(path, f"case '{cid}': judge_threshold must be between 0 and 100", line)
            if "judge_rubric" not in case:
                lint.warn(path, f"case '{cid}': judge_threshold without judge_rubric has no effect", line)
        check_assertions(lint, path, cid, case.get("assertions"), line)


def case_line(lines, cid, idx):
    if isinstance(cid, str):
        for n, l in enumerate(lines, 1):
            if re.match(rf"^\s*-\s*id:\s*['\"]?{re.escape(cid)}['\"]?\s*$", l):
                return n
    count = 0
    for n, l in enumerate(lines, 1):
        if re.match(r"^\s*-\s*id:", l):
            if count == idx:
                return n
            count += 1
    return 1


def check_assertions(lint, path, cid, assertions, line):
    if not isinstance(assertions, list):
        lint.error(path, f"case '{cid}': assertions must be a list", line)
        return
    if not assertions:
        lint.warn(path, f"case '{cid}': no assertions", line)
    for a in assertions:
        if not isinstance(a, dict) or "type" not in a:
            lint.error(path, f"case '{cid}': each assertion is a mapping with 'type'", line)
            continue
        kind = a["type"]
        if kind not in ASSERTIONS:
            lint.error(path, f"case '{cid}': unknown assertion type '{kind}' (allowed: {sorted(ASSERTIONS)})", line)
            continue
        required, optional = ASSERTIONS[kind]
        keys = set(a) - {"type"}
        for k in sorted(keys - required - optional):
            lint.error(path, f"case '{cid}': {kind} has unknown key '{k}'", line)
        for k in sorted(required - keys):
            lint.error(path, f"case '{cid}': {kind} requires '{k}'", line)
        if "path" in a:
            check_rel_path(lint, path, a["path"], f"case '{cid}': {kind}.path", line)
        if kind == "output_contains" and "text" in a and (not isinstance(a["text"], str) or not a["text"]):
            lint.error(path, f"case '{cid}': output_contains.text must be a non-empty string", line)
        if kind == "regex" and "pattern" in a:
            check_pattern(lint, path, cid, a["pattern"], line)
        if kind == "max_turns" and "value" in a and (not is_int(a["value"]) or a["value"] <= 0):
            lint.error(path, f"case '{cid}': max_turns.value must be a positive integer", line)
        if kind == "max_cost_usd" and "value" in a and (not is_num(a["value"]) or a["value"] <= 0):
            lint.error(path, f"case '{cid}': max_cost_usd.value must be a positive number", line)
        if kind == "skill_invoked" and "skill" in a and (not isinstance(a["skill"], str) or not a["skill"]):
            lint.error(path, f"case '{cid}': skill_invoked.skill must be a non-empty string", line)


def check_pattern(lint, path, cid, pattern, line):
    if not isinstance(pattern, str) or not pattern:
        lint.error(path, f"case '{cid}': regex.pattern must be a non-empty string", line)
        return
    if NON_RUST_REGEX.search(pattern):
        lint.error(path, f"case '{cid}': regex uses lookaround or backreferences, unsupported by the Rust regex engine", line)
        return
    try:
        re.compile(pattern)
    except re.error as exc:
        lint.error(path, f"case '{cid}': invalid regex: {exc}", line)


def check_tree(lint, farm_dir):
    for dirpath, dirnames, filenames in os.walk(farm_dir):
        for name in dirnames + filenames:
            full = os.path.join(dirpath, name)
            if os.path.islink(full):
                lint.error(full, "symlinks are not allowed under farm/")
            if name == "..":
                lint.error(full, "path component '..' is not allowed")
    fixtures = os.path.join(farm_dir, "fixtures")
    if os.path.isdir(fixtures):
        for name in sorted(os.listdir(fixtures)):
            full = os.path.join(fixtures, name)
            if os.path.isdir(full):
                if not ID_RE.match(name):
                    lint.error(full, f"fixture name '{name}' must match {ID_RE.pattern}")
                if not any(files for _, _, files in os.walk(full)):
                    lint.error(full, f"fixture '{name}' is empty")
            elif name != "README.md":
                lint.warn(full, "only fixture directories and README.md belong in farm/fixtures/")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="kit repository root (default: .)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any error is reported")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    lint = Lint(root)
    farm_dir = os.path.join(root, "farm")
    if not os.path.isdir(farm_dir):
        lint.error(farm_dir, "farm/ directory not found")
        return finish(lint, args.strict)
    check_tree(lint, farm_dir)
    farm = check_farm_yaml(lint, farm_dir)
    agents = {}
    if farm:
        for agent_id in farm["agents"]:
            merged = check_agent(lint, farm_dir, agent_id, farm)
            if merged is not None:
                agents[agent_id] = merged
        agents_dir = os.path.join(farm_dir, "agents")
        if os.path.isdir(agents_dir):
            for name in sorted(os.listdir(agents_dir)):
                stem, ext = os.path.splitext(name)
                if ext != ".md":
                    lint.error(os.path.join(agents_dir, name), "agents/ holds only <agent_id>.md files")
                elif stem not in farm["agents"]:
                    lint.error(os.path.join(agents_dir, name), f"agent '{stem}' is not listed in farm.yaml agents")
    evals_dir = os.path.join(farm_dir, "evals")
    if os.path.isdir(evals_dir):
        for name in sorted(os.listdir(evals_dir)):
            full = os.path.join(evals_dir, name)
            if not name.endswith(".yaml"):
                lint.error(full, "evals/ holds only <agent_id>.yaml files")
                continue
            check_eval(lint, farm_dir, full, agents)
    return finish(lint, args.strict)


def finish(lint, strict):
    print(f"farm-lint: {lint.errors} error(s), {lint.warnings} warning(s)")
    return 1 if strict and lint.errors else 0


if __name__ == "__main__":
    sys.exit(main())
