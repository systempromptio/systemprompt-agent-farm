# Fixture ground truth

This file is **excluded** from every run workspace.

## night_audit

An empty workspace apart from `CONTEXT.md`. The `accounting_night_audit` agent
reads Dynapps' live Odoo (`master`, company 1) through the hosted `dynapps-odoo`
MCP server as the launching user, strictly read-only, and writes three files
under `out/`: `out/dashboard.md`, `informe_auditoria_Dynapps_<YYYY>_<MM>.md` (11 numbered
sections) and `DELIVERY.md` (the dynbrain publish receipt). There is no planted
ground truth: the data is whatever the previous month holds.
