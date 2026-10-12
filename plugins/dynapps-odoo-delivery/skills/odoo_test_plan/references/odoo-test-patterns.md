# Odoo test patterns (16.0 / 17.0)

```python
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install", "dynapps_fleet_maintenance")
class TestServiceWorkflow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.vehicle = cls.env["fleet.vehicle"].create({...})
        cls.service = cls.env["fleet.maintenance.service"].create({"vehicle_id": cls.vehicle.id})

    def test_confirm_from_draft(self):
        self.service.action_confirm()
        self.assertEqual(self.service.state, "confirmed")

    def test_confirm_from_done_refused(self):
        self.service.state = "done"
        with self.assertRaises(UserError):
            self.service.action_confirm()
```

## Access

```python
user = new_test_user(self.env, login="fleet_user", groups="fleet.fleet_group_user")
with self.assertRaises(AccessError):
    self.service.with_user(user).unlink()
```

## Computes

Change an input, then read the computed field; for `store=True` computes also
`self.env.invalidate_all()` and re-read to prove the stored value was recomputed.

## Tags

- `post_install` + `-at_install` runs after all modules load (needed for cross-module data).
- `--test-tags /module_name` runs one module; `:TestClass.test_method` narrows further.
- `SavepointCase` is merged into `TransactionCase` since 15.0; do not use it.
