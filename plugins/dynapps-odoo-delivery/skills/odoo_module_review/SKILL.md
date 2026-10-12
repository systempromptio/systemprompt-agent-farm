---
name: odoo_module_review
title: Odoo Module Review
description: "Use when an Odoo addon needs a code review before merge or delivery — 'review this module', 'check the addon for ORM problems', 'is this safe to ship' — and the result must be a REVIEW.md of file:line findings with severity and a concrete fix."
tags: [odoo, review, orm, security, delivery]
category: development
display_category: "Odoo — Delivery"
---

# Odoo Module Review

You review one Odoo addon the way a Dynapps senior developer does before a customer delivery: read
every Python, XML and CSV file, check it against the checklist, and write `REVIEW.md` at the
module root. Every finding names a file and a line, a severity, and a fix a developer can apply
without asking a follow-up question. You do not edit the module's code.

## Use when

- "review this module", "check this addon before we merge", "is this safe for production"
- A pull request touches `models/`, `security/`, `views/` or `__manifest__.py`.
- Do not use for a version migration; that is `odoo_migration_plan`.

## Procedure

1. Read `__manifest__.py` first. Note `version` (the first two parts are the Odoo series),
   `depends`, `data` order and `license`. The series decides which view rules apply.
2. List the tree. Every file in `data` must exist, and every XML/CSV file on disk should be in
   `data` or `demo`. An orphan file is a finding.
3. Walk `models/*.py` against the ORM checklist in `references/orm-checklist.md`. Record the
   exact line of each hit.
4. Walk `security/ir.model.access.csv` and any `ir.rule` records against the access checklist in
   `references/orm-checklist.md`.
5. Walk `views/*.xml`. For series 17.0 and later, any `attrs=` or `states=` attribute is a
   blocker: they were removed and the view fails to load.
6. Grade each finding using the severity scale below, then write `REVIEW.md`.

## Severity

| Severity | Meaning |
|----------|---------|
| blocker | Fails to install, breaks data, or bypasses access rights. Must be fixed before merge. |
| major | Correct today but wrong under load, multi-company or a second user. Fix in this PR. |
| minor | Style, naming, maintainability. Fix when touched. |

`sudo()` that leaks records across access rules, SQL injection, and a missing manifest `license`
on a module that ships to the Odoo Apps store are always blockers.

## Output: REVIEW.md

```markdown
# Review: <module technical name> (<series>)

Summary: <one sentence verdict: ship / fix then ship / do not ship>

| # | File:line | Severity | Finding | Fix |
|---|-----------|----------|---------|-----|
| 1 | models/fleet_service.py:42 | blocker | `search()` inside a loop over `self` (N+1) | Read once with `search([('vehicle_id', 'in', self.vehicle_id.ids)])` and group in Python |

## Not checked
<anything you could not verify, e.g. behaviour that needs a running database>
```

Rules for the table:

- One row per occurrence. Two `sudo()` calls on different lines are two rows.
- The finding quotes the offending expression in backticks.
- The fix is code or a precise instruction, never "consider improving".
- Order rows by severity, then file, then line.

## Done when

`REVIEW.md` exists, every checklist item was evaluated, and every row has a file:line that points
at the code it describes.
