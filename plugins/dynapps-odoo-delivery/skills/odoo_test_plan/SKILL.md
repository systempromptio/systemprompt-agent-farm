---
name: odoo_test_plan
title: Odoo Test Plan and Tests
description: "Use when an Odoo addon needs automated tests — 'write tests for this module', 'what should we test before release', 'cover the state transitions' — and the result must be a TEST_PLAN.md plus TransactionCase test files under tests/."
tags: [odoo, testing, transactioncase, quality, delivery]
category: development
display_category: "Odoo — Delivery"
---

# Odoo Test Plan and Tests

You read one Odoo addon, derive what must be proven, write `TEST_PLAN.md`, and then write the
`tests/` package that proves it with `TransactionCase`. The plan and the tests match one to one:
every plan row names the test method that covers it.

## Use when

- "write tests for this module", "add coverage before the release", "test the workflow"
- Do not use to review code; that is `odoo_module_review`.

## Procedure

1. Read the models. For each model with a `state` selection, draw the transition table: every
   button method (`action_*`) that writes `state`, its source states and its target state.
2. List the compute fields, constraints (`@api.constrains`, `_sql_constraints`) and onchange
   methods. Each one gets at least one positive and one negative case.
3. List the access lines in `security/ir.model.access.csv`. Each group gets a test that a user
   in that group can or cannot create/write/unlink, using `new_test_user` and `with_user`.
4. Write `TEST_PLAN.md`, then the tests using the patterns in `references/odoo-test-patterns.md`.
5. Register each test module in `tests/__init__.py`.

## Output: TEST_PLAN.md

```markdown
# Test plan: <module> (<series>)

## State transitions
| From | Action | To | Test |
|------|--------|----|------|
| draft | action_confirm | confirmed | test_confirm_from_draft |
| done | action_confirm | UserError | test_confirm_from_done_refused |

## Computes and constraints
| Field / constraint | Case | Expected | Test |

## Access
| Group | Operation | Expected | Test |

## Run
`odoo-bin -d <db> -i <module> --test-tags /<module> --stop-after-init`
```

## Output: tests/

- `tests/__init__.py` importing each test module.
- `tests/test_<model>_workflow.py`, `tests/test_<model>_access.py`, one class per concern.
- Classes are decorated `@tagged("post_install", "-at_install", "<module>")`.
- Records are created in `setUpClass` with `cls.env = cls.env(context=dict(cls.env.context,
  tracking_disable=True))`.
- Every illegal transition asserts the exception with `self.assertRaises(UserError)` or
  `ValidationError`, never a bare `Exception`.

## Done when

`TEST_PLAN.md` exists, every transition, compute, constraint and access line has a row, and
every row's test method exists in `tests/`.
