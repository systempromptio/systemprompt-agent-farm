# Odoo 17.0 changes that matter for a 16.0 module

## Version matrix

| Component | 16.0 | 17.0 |
|-----------|------|------|
| Python | 3.8 - 3.10 | 3.10 - 3.12 |
| PostgreSQL | 12+ | 12+ (14+ recommended) |
| Manifest version | `16.0.x.y.z` | `17.0.x.y.z` |
| Frontend | legacy widgets + OWL 1/2 | OWL 2 only, legacy widgets removed |

## attrs / states to expressions

16.0 domain syntax becomes a Python expression evaluated on the record:

| 16.0 | 17.0 |
|------|------|
| `attrs="{'invisible': [('state', '!=', 'draft')]}"` | `invisible="state != 'draft'"` |
| `attrs="{'readonly': [('state', 'in', ('done','cancel'))]}"` | `readonly="state in ('done', 'cancel')"` |
| `attrs="{'required': [('type', '=', 'service')]}"` | `required="type == 'service'"` |
| `'|', (a), (b)` | `a or b` |
| `(a), (b)` implicit AND | `a and b` |
| `states="draft,sent"` | `invisible="state not in ('draft', 'sent')"` |

Fields used in an expression must be present in the view (add `invisible="1"` copies if needed).

## Deprecated or changed APIs

- `name_get()` is deprecated: compute `display_name` with `_compute_display_name`.
- `_name_search` signature changed; override `_name_search(name, domain, operator, limit, order)`.
- `fields_view_get` removed: use `get_views` / `_get_view`.
- `flush()` and `invalidate_cache()` removed: `flush_model()`, `flush_recordset()`,
  `invalidate_model()`, `invalidate_recordset()` (already available in 16.0).
- `odoo.tools.SQL` is the preferred wrapper for composed raw SQL.
- Chatter: `<div class="oe_chatter">` becomes `<chatter/>`.
- Tree view `<tree>` still valid in 17.0 (renamed `<list>` in 18.0); do not rename early.

## OpenUpgrade notes

- OCA OpenUpgrade publishes `openupgradelib` helpers: `rename_fields`, `rename_columns`,
  `map_values`, `logged_query`. Use them in `migrations/17.0.1.0.0/pre-migration.py`.
- Core modules are migrated by OpenUpgrade or the Odoo upgrade service; plan only the
  customer's custom modules, but check OpenUpgrade's 17.0 coverage table for each dependency.
- Run the migration on a copy of production data; record row counts before and after.
