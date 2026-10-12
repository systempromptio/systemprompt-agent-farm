from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    maintenance_ids = fields.One2many("dynapps.fleet.maintenance", "vehicle_id")
    maintenance_cost_total = fields.Monetary(
        compute="_compute_maintenance_cost_total",
        store=True,
        currency_field="currency_id",
    )
    next_maintenance_date = fields.Date(compute="_compute_next_maintenance_date")

    @api.depends("maintenance_ids")
    def _compute_maintenance_cost_total(self):
        for vehicle in self:
            vehicle.maintenance_cost_total = sum(
                vehicle.maintenance_ids.filtered(lambda m: m.state == "done").mapped(
                    "cost"
                )
            )

    @api.depends("maintenance_ids.scheduled_date", "maintenance_ids.state")
    def _compute_next_maintenance_date(self):
        for vehicle in self:
            pending = vehicle.maintenance_ids.filtered(lambda m: m.state != "done")
            vehicle.next_maintenance_date = min(
                pending.mapped("scheduled_date"), default=False
            )
