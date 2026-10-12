#!/bin/sh
# Pipe a sample envelope through every hook command in hooks.json.
#  1. SYSTEMPROMPT_FARM_RUN_ID unset: every command exits 0, prints nothing.
#  2. Set, with an unreachable URL: commands exit 0; PreToolUse falls back to allow.
# POSIX sh; needs python3 only to extract the commands. macOS and Linux.
set -u
cd "$(dirname "$0")/.." || exit 1
HOOKS=plugins/dynapps-odoo-delivery/hooks/hooks.json
ENV='{"session_id":"smoke","hook_event_name":"PreToolUse","tool_name":"Read","tool_input":{"file_path":"README.md"}}'
TMP=$(mktemp -d 2>/dev/null || mktemp -d -t hooksmoke); trap 'rm -rf "$TMP"' EXIT
python3 -c 'import json,sys
for ev,groups in json.load(open(sys.argv[1]))["hooks"].items():
    for g in groups:
        for i,h in enumerate(g["hooks"]):
            open(sys.argv[2]+"/"+ev+"."+str(i),"w").write(h["command"])' "$HOOKS" "$TMP" || exit 1
fail=0
for f in "$TMP"/*.*; do
  ev=$(basename "$f"); ev=${ev%.*}
  out=$(printf %s "$ENV" | env -u SYSTEMPROMPT_FARM_RUN_ID -u SYSTEMPROMPT_URL -u SYSTEMPROMPT_TOKEN sh "$f" 2>&1); rc=$?
  if [ $rc -ne 0 ] || [ -n "$out" ]; then echo "FAIL inert $ev rc=$rc out=$out"; fail=1; else echo "ok   inert $ev"; fi
  out=$(printf %s "$ENV" | SYSTEMPROMPT_FARM_RUN_ID=smoke-run SYSTEMPROMPT_URL=http://127.0.0.1:9 SYSTEMPROMPT_TOKEN=dummy sh "$f" 2>&1); rc=$?
  if [ $rc -ne 0 ]; then echo "FAIL farm  $ev rc=$rc out=$out"; fail=1; continue; fi
  if [ "$ev" = PreToolUse ]; then
    case "$out" in *'"permissionDecision":"allow"'*) echo "ok   farm  $ev (allow fallback)";; *) echo "FAIL farm $ev out=$out"; fail=1;; esac
  else echo "ok   farm  $ev"; fi
done
out=$(printf %s "$ENV" | SYSTEMPROMPT_FARM_RUN_ID=smoke-run env -u SYSTEMPROMPT_URL sh "$TMP/SessionStart.0" 2>&1); rc=$?
[ $rc -ne 0 ] && echo "ok   farm  SessionStart fails fast without URL" || { echo "FAIL SessionStart accepted a missing URL"; fail=1; }
exit $fail
