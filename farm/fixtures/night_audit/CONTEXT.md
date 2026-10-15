# Night audit workspace

Unattended monthly accounting audit of Dynapps (Odoo `master`, company 1).
Odoo is reached only through the `dynapps-odoo` MCP read tools; nothing in Odoo
is ever changed from this run. The run writes `out/dashboard.md`,
`informe_auditoria_Dynapps_<YYYY>_<MM>.md` and `DELIVERY.md` here, and publishes
a summary to DynBrain (`dynbrain` MCP) for the morning follow-up.
