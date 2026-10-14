---
name: odoo_gdpr_erasure
title: Odoo GDPR Erasure
description: "Use for a GDPR right-to-erasure request against an Odoo contact — 'erase this customer's data', 'process the Art. 17 request' — producing an inventory, anonymisation, retention of posted invoices and an ERASURE_REPORT.md."
tags: [odoo, crm, governance, mcp]
category: development
display_category: "Odoo — Operations"
---

# Odoo GDPR Erasure

This skill runs against a live Odoo through the governed `odoo` MCP server
(`mcp__odoo__*` tools). Every call is audited and attributed; destructive
and erasure tools need a `reason` and may be refused by governance.

1. `partner_search` for the partner tagged `demo-gdpr`; confirm with `partner_get`.
2. Run `gdpr_erase_inventory` for it. Cross-check with `crm_lead_search`,
   `note_list`, `invoice_list` and `attachment_list`.
3. Classify every record:
   - **Erase/anonymise**: contact PII (name, email, phone, address), leads,
     chatter content, draft invoices.
   - **Retain (legal obligation, Art. 17(3)(b))**: posted invoices and
     accounting entries. Never modify, cancel or delete a posted invoice.
4. Call `partner_anonymise` with a `reason` citing the request. If it is
   refused, record the refusal verbatim and stop changing data.
5. Write ERASURE_REPORT.md: request summary; inventory table
   `| model | id | state | action | legal basis |`; what was anonymised; what was
   retained and why; any refusals; residual risk. Refer to the subject by
   partner id only; never copy their email, phone or address into the report.

Rules: work only on records carrying `demo-gdpr`; if a tool
returns a record without it, stop touching that record and note it. Never
put API keys, tokens or passwords in any file. Do not narrate tool use.
