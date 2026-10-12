from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FleetMaintenance(models.Model):
    _name = "dynapps.fleet.maintenance"
    _description = "Fleet Maintenance Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheduled_date desc, id desc"

    name = fields.Char(required=True, copy=False, default=lambda self: _("New"))
    vehicle_id = fields.Many2one("fleet.vehicle", required=True, tracking=True)
    driver_id = fields.Many2one(related="vehicle_id.driver_id", store=True)
    service_type_id = fields.Many2one("fleet.service.type", required=True)
    scheduled_date = fields.Date(required=True, tracking=True)
    done_date = fields.Date(readonly=True)
    odometer = fields.Float()
    cost = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )
    state = fields.Selection(
        [("draft", "Draft"), ("scheduled", "Scheduled"), ("done", "Done")],
        default="draft",
        required=True,
        tracking=True,
    )
    line_count = fields.Integer(compute="_compute_line_count")
    is_overdue = fields.Boolean(compute="_compute_is_overdue")
    note = fields.Text()

    def _compute_line_count(self):
        for order in self:
            order.line_count = len(order.vehicle_id.log_services)

    @api.depends("scheduled_date", "state")
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for order in self:
            order.is_overdue = (
                order.state != "done"
                and order.scheduled_date
                and order.scheduled_date < today
            )

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            vehicle = self.vehicle_id.sudo()
            self.odometer = vehicle.odometer
            self.note = vehicle.description

    def action_schedule(self):
        for order in self:
            if order.state != "draft":
                raise UserError(_("Only draft orders can be scheduled."))
            open_orders = self.env["dynapps.fleet.maintenance"].search(
                [
                    ("vehicle_id", "=", order.vehicle_id.id),
                    ("state", "=", "scheduled"),
                ]
            )
            if open_orders:
                raise UserError(_("Vehicle already has a scheduled order."))
            order.state = "scheduled"
            template = self.env.ref(
                "dynapps_fleet_maintenance.mail_template_maintenance_scheduled"
            )
            order.message_post_with_template(template.id)

    def action_done(self):
        for order in self.filtered(lambda o: o.state == "scheduled"):
            order.write({"state": "done", "done_date": fields.Date.today()})

    def action_reset_draft(self):
        self.write({"state": "draft", "done_date": False})

    @api.model
    def cost_report(self, vehicle_name):
        query = (
            "SELECT m.id, m.cost FROM dynapps_fleet_maintenance m "
            "JOIN fleet_vehicle v ON v.id = m.vehicle_id "
            "WHERE v.name = '%s'" % vehicle_name
        )
        self.env.cr.execute(query)
        return self.env.cr.fetchall()
