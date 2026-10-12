---
name: odoo_release_notes
title: Odoo Customer Release Notes
description: "Use when a Dynapps Odoo module release is ready for the customer — 'write the release notes', 'summarise what changed since 16.0.1.2.0', 'turn the changelog into notes for the client' — and conventional commits must become a customer-facing RELEASE_NOTES.md."
tags: [odoo, release, changelog, delivery]
category: development
display_category: "Odoo — Delivery"
---

# Odoo Customer Release Notes

You turn a module's `CHANGELOG.md` and its conventional-commit history into `RELEASE_NOTES.md`
that a customer's functional key user can read: what they will see, what they must do, and
what was fixed. Every line traces to a commit; nothing is invented and nothing user-visible
is dropped.

## Use when

- "write the release notes", "what changed for the customer", "notes for version 16.0.1.3.0"
- Do not use to review code; that is `odoo_module_review`.

## Inputs

- The range: last released version or tag, and the head. Default to the newest version in
  `CHANGELOG.md` against the commits listed after it.
- The commit list: `git log --format='%h %s' <from>..<to>` or a provided `commits.txt`.

## Procedure

1. Parse every commit with the rules in `references/commit-mapping.md`. Classify each as
   feature, fix, upgrade action, or internal.
2. Drop internal commits (`chore`, `ci`, `test`, `refactor`, `style`, `docs` without user
   impact) from the customer notes, but count them.
3. Rewrite each kept commit in the customer's language: name the Odoo menu, form or report
   they use, not the model or method. `fix(fleet): avoid N+1 in service count` becomes
   "Vehicle list: the service count column loads faster on large fleets."
4. Any commit with `BREAKING CHANGE:` or `!`, any new `security/` access line, any new
   module dependency, and any data migration becomes an **Action required** item.
5. Write the file.

## Output: RELEASE_NOTES.md

```markdown
# <Module display name> <version> — <YYYY-MM-DD>

## Highlights
- <one to three sentences on the most valuable change>

## New
- <customer-facing line> (<short hash>)

## Fixed
- <customer-facing line> (<short hash>)

## Action required
- <what the key user or administrator must do after upgrade, or "None.">

## Upgrade
Update the module from Apps > <module> > Upgrade, or `-u <technical_name>`.

<N> internal changes not listed.
```

Rules:

- Every bullet ends with its short commit hash in parentheses.
- Present tense, second person where an action is needed, no developer jargon (no "ORM",
  "compute", "recordset").
- Brand the document as delivered by Dynapps only in a footer line if the customer template
  asks for it; never invent marketing copy.

## Done when

`RELEASE_NOTES.md` exists and every non-internal commit in the range appears exactly once.
