# Odoo ORM and access checklist (Dynapps)

## ORM

- **sudo() misuse.** `sudo()` in an `@api.onchange`, a controller, or before a `search`/`read`
  whose result returns to the user bypasses record rules. Allowed only for a narrowly scoped
  write the user may not do directly, with a comment naming why. Prefer `with_user()` or
  `check_access_rights()` + `check_access_rule()`.
- **search in a loop (N+1).** `for rec in self: self.env[...].search([... rec.id ...])` issues
  one query per record. Use one `search` with `'in'`, `read_group`, or a related/one2many field.
- **compute without @api.depends.** A `compute=` method with no `@api.depends` is recomputed on
  every read and never invalidated when its inputs change. Every field read inside the method
  must be listed, dotted paths included (`'line_ids.amount'`).
- **store=True compute with incomplete depends.** A stored compute is only recomputed when a
  listed dependency changes. A missing path leaves stale values in the database.
- **raw SQL without parameters.** `self.env.cr.execute("... %s" % value)` or f-strings are SQL
  injection. Use `cr.execute(query, (value,))` or `psycopg2.sql`/`odoo.tools.SQL` for identifiers.
  Call `flush_model()` before raw reads and `invalidate_model()` after raw writes.
- **write/create in loops.** `rec.write({...})` per record where one `self.write` would do.
- **Missing ensure_one().** A method that reads `self.field` as a scalar on a recordset.

## Access

- **Over-wide ir.model.access.** A line granting `1,1,1,1` to `base.group_user` (all employees)
  or with an empty `group_id` (everyone, including portal) is a blocker unless the model is
  deliberately public.
- Every new model needs at least one access line, or only the superuser can use it.
- `ir.rule` records with `[(1, '=', 1)]` domains on multi-company models.

## Manifest

- `license` key missing: Odoo defaults to LGPL-3 and logs a warning; Dynapps modules declare it
  explicitly (`LGPL-3` or `OPL-1`).
- `version` must be `<series>.x.y.z`, e.g. `16.0.1.0.0`.
- Files in `data` load in order: security before views, views before menus.

## Views (17.0+)

- `attrs="{'invisible': [...]}"` and `states="draft"` are removed. Use
  `invisible="state != 'draft'"`, `readonly="..."`, `required="..."` Python expressions.
