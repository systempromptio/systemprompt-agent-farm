from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFleetMaintenance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Dynapps Motors"})
        model = cls.env["fleet.vehicle.model"].create(
            {"name": "Van", "brand_id": brand.id}
        )
        cls.vehicle = cls.env["fleet.vehicle"].create(
            {"model_id": model.id, "license_plate": "1234-DYN"}
        )
        cls.service_type = cls.env["fleet.service.type"].create(
            {"name": "Oil change", "category": "service"}
        )

    def test_create_defaults_to_draft(self):
        order = self.env["dynapps.fleet.maintenance"].create(
            {
                "vehicle_id": self.vehicle.id,
                "service_type_id": self.service_type.id,
                "scheduled_date": "2026-01-15",
            }
        )
        self.assertEqual(order.state, "draft")
        self.assertIn(order, self.vehicle.maintenance_ids)
