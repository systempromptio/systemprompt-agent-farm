---
name: odoo_migration_plan
title: Odoo 16 to 17 Migration Plan
description: "Use when a Dynapps customer module must move from Odoo 16.0 to 17.0 — 'plan the migration', 'what breaks on 17', 'estimate the upgrade' — and the result must be a MIGRATION_PLAN.md listing every change by file with effort and order."
tags: [odoo, migration, upgrade, openupgrade, delivery]
category: development
display_category: "Odoo — Delivery"
---

# Odoo 16 to 17 Migration Plan

You inventory one or more Odoo 16.0 addons and produce `MIGRATION_PLAN.md`: what must change for
17.0, where, in what order, and how long it takes. You plan; you do not port the code.

## Use when

- "plan the 17 migration", "what breaks when we upgrade", "estimate the upgrade for this module"
- Do not use for a general code review; that is `odoo_module_review`.

## Procedure

1. Read each `__manifest__.py`. Confirm the series is `16.0`. Record `depends`: every dependency
   must exist in 17.0 (core, OCA or Dynapps). A dependency without a 17.0 release is a blocker
   and goes first in the plan.
2. Check the version matrix in `references/odoo-17-changes.md` for Python, PostgreSQL and
   library requirements, and record the target versions.
3. Scan `views/*.xml` for `attrs=` and `states=`. Each occurrence becomes a row with the
   rewritten 17.0 expression, translated with the rules in `references/odoo-17-changes.md`.
4. Scan `models/*.py` for the deprecated APIs listed in the reference (`name_get`,
   `_name_search`, `fields_view_get`, `read_group` lazy behaviour, `flush()`/`invalidate_cache()`).
5. Decide the data path: if stored fields are renamed or removed, plan an OpenUpgrade-style
   `migrations/17.0.1.0.0/pre-migration.py` and `post-migration.py`. Name each column and the
   SQL or ORM step that moves it.
6. Write the plan.

## Output: MIGRATION_PLAN.md

```markdown
# Migration plan: <module> 16.0 -> 17.0

## Verdict
<feasible / feasible with blockers / blocked>, estimated <N> developer-days.

## Version matrix
| Component | 16.0 | 17.0 |

## Blockers
<dependencies without a 17.0 release, data that cannot be migrated automatically>

## Changes
| # | File:line | Change | 17.0 replacement | Effort (h) |

## Data migration
<pre/post migration scripts, one bullet per column or model>

## Order of work
1. ...

## Test strategy
<which flows to re-test; reference odoo_test_plan for TransactionCase coverage>
```

Rules:

- Every `attrs`/`states` occurrence is its own row with the exact replacement expression.
- Effort is in hours per row; the verdict total is their sum rounded up to half-days.
- Bump `version` to `17.0.1.0.0` as the last change row.

## Done when

`MIGRATION_PLAN.md` exists, every view and model file was scanned, and every row names a file:line.
