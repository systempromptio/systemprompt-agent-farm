---
name: odoo_lead_triage
title: Odoo Lead Triage
description: "Use when CRM leads in Odoo need qualifying — 'triage the new leads', 'score these leads', 'which leads are hot' — and each lead should get a chatter note, priority, temperature tag and follow-up activity, summarised in TRIAGE.md."
tags: [odoo, crm, governance, mcp]
category: development
display_category: "Odoo — Operations"
---

# Odoo Lead Triage

This skill runs against a live Odoo through the governed `odoo` MCP server
(`mcp__odoo__*` tools). Every call is audited and attributed; destructive
and erasure tools need a `reason` and may be refused by governance.

1. `crm_lead_search` for leads tagged `demo-triage`. Read each with `crm_lead_get`.
2. Qualify each lead on budget, authority, need and timeline from its
   description and fields. Score: hot (clear need + timeline + decision maker),
   warm (real need, missing one of those), cold (no engagement or no need).
3. For each lead:
   - `note_add` a qualification note to its chatter: the BANT assessment in 3-5 lines.
   - `crm_lead_update` priority (`3` hot, `2` warm, `0`-`1` cold) and add the
     `hot`/`warm`/`cold` tag (keep `demo-triage`; never remove existing tags).
   - `activity_create` a follow-up: hot in 1 day, warm in 3, cold in 14, with a
     one-line summary of the next step.
4. Write TRIAGE.md: a table `| lead id | name | company | temperature | priority | follow-up date | next step |`,
   then one short paragraph per lead justifying the score.

Rules: work only on records carrying `demo-triage`; if a tool
returns a record without it, stop touching that record and note it. Never
put API keys, tokens or passwords in any file. Do not narrate tool use.
Only read and write tools are available to you; never try to delete anything.
