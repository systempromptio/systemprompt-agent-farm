# Fixture ground truth

This file is **excluded** from every run workspace. It lists what each fixture
deliberately contains so evals and reviewers can score completeness. Paths are
relative to the fixture root. Line numbers are 1-based.

## dynapps_fleet_maintenance (Odoo 16 module)

| # | File:line | Planted issue | Category |
|---|-----------|---------------|----------|
| 1 | `__manifest__.py:1` | No `license` key in the manifest (Odoo warns and defaults to LGPL-3; OCA/Dynapps policy requires it explicitly). | Packaging |
| 2 | `models/fleet_maintenance.py:49` | `sudo()` inside `_onchange_vehicle_id`: an onchange runs as the editing user and bypasses access rules to leak vehicle data into the form. | Security |
| 3 | `models/fleet_maintenance.py:57` | `search()` inside the `for order in self` loop of `action_schedule`: N+1 queries; should be one grouped search / `read_group` before the loop. | Performance |
| 4 | `models/fleet_maintenance.py:32` | `_compute_line_count` has no `@api.depends` (field declared at line 28): value never recomputes in the cache when `vehicle_id` changes. | Correctness |
| 5 | `models/fleet_maintenance.py:83` / `:85` | `cost_report` builds SQL with `%` string formatting then `self.env.cr.execute(query)`: SQL injection; must pass parameters to `execute`. | Security |
| 6 | `models/fleet_vehicle.py:15` | `store=True` compute `_compute_maintenance_cost_total` depends only on `maintenance_ids` but reads `maintenance_ids.state` and `maintenance_ids.cost`: stored total goes stale. | Correctness |
| 7 | `security/ir.model.access.csv:2` | `base.group_user` (every internal user) gets `perm_unlink=1` on maintenance orders. | Security |
| 8 | `views/fleet_maintenance_views.xml:26,28,43` | `attrs=` domains (and `states=` at line 30) are removed in Odoo 17; migration must rewrite them as `invisible="state != 'draft'"` expressions. | Migration |
| 9 | `tests/test_fleet_maintenance.py` | Only a creation test; no test covers the draft → scheduled → done workflow, the double-schedule guard, or `action_reset_draft`. | Testing |
| 10 | `models/fleet_maintenance.py:69` | `message_post_with_template` is removed in Odoo 17 (use `message_post_with_source`). | Migration |

Secondary, not required for a pass: `cost_report` has no access check; `action_done`
silently ignores non-scheduled orders; `name` default is never sequenced.

## dynapps_fleet_maintenance_git (release-notes input)

`CHANGELOG.md` holds the previous release (16.0.0.9.0). `commits.txt` holds 15
commits for 16.0.1.0.0. Customer-relevant: a1f3c09, b72e4d1, c0d9e88, e5c2f10,
f8b3a22, 2c4f8a1, 4e1c6d2, 6a8d3e9, 7b5f1a0. Internal only (must not appear as
customer features): d4a1b67, 0a7d5e3, 1b6e9f4, 3d9a7b5, 5f2b0c8, 8c0e2b4.
f8b3a22 changes record visibility and should be called out as a behaviour change.
