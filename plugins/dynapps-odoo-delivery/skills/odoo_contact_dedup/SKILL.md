---
name: odoo_contact_dedup
title: Odoo Contact Deduplication
description: "Use when Odoo contacts or leads are duplicated — 'clean up duplicate contacts', 'merge these partners' — and the result must be a DEDUP_PLAN.md, merge notes, and governed deletes that fall back to archiving when refused."
tags: [odoo, crm, governance, mcp]
category: development
display_category: "Odoo — Operations"
---

# Odoo Contact Deduplication

This skill runs against a live Odoo through the governed `odoo` MCP server
(`mcp__odoo__*` tools). Every call is audited and attributed; destructive
and erasure tools need a `reason` and may be refused by governance.

1. `partner_search` for partners tagged `demo-dedup`, `crm_lead_search` for
   leads tagged `demo-dedup`. Read each candidate with `partner_get` / `crm_lead_get`.
2. Group duplicates by normalised email, then phone (digits only), then name
   (case, punctuation, "Last, First" order and legal-form suffixes like BV, SL,
   S.L. ignored). For each group pick a survivor: the most complete record,
   oldest on a tie.
3. Write DEDUP_PLAN.md before changing anything: one table row per group with
   survivor id, redundant ids, matching evidence, and planned action.
4. For each redundant record:
   - `note_add` a merge note on the survivor naming the redundant id and what
     it held, and on the redundant record pointing at the survivor.
   - Call `partner_delete` / `crm_lead_delete` with a `reason` naming the
     survivor and the evidence.
   - If the call is refused (governance denial, policy, or Odoo constraint),
     archive instead with `partner_update` / `crm_lead_update` setting
     `active: false`, and record the refusal text verbatim.
5. Append an "Outcome" section to DEDUP_PLAN.md: per record — deleted,
   archived (with the refusal), or untouched and why.

Rules: work only on records carrying `demo-dedup`; if a tool
returns a record without it, stop touching that record and note it. Never
put API keys, tokens or passwords in any file. Do not narrate tool use.
Never merge or delete a record that is not tagged `demo-dedup`, even if it
matches a duplicate.
