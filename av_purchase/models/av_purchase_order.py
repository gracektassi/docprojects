# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(
        [
            ("draft", "RFQ"),
            ("sent", "RFQ Sent"),
            ("to approve", "To Approve"),
            ("purchase", "Purchase Order"),
            ("waiting_for_hod", "Waiting for HOD"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("done", "Locked"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="draft",
        tracking=True,
    )

    project_id = fields.Many2one("project.project", string="Assigned Project")
    amount = fields.Float(string="Amount")
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        compute="_compute_department",
        store=True,
        readonly=False,
    )

    @api.depends("create_uid")
    def _compute_department(self):
        """
        Compute the department from the creator's employee record.
        """
        for order in self:
            employee = order.create_uid.employee_id
            order.department_id = employee.department_id if employee else False

    @api.constrains("order_line")
    def _check_products(self):
        for order in self:
            if order.state == "waiting_for_hod" and not order.order_line:
                raise ValidationError(
                    "You must add products to the order before submitting."
                )

    def action_submit(self):
        for order in self:

            if order.state not in ["draft", "sent"]:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()

            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])

            if order.state == "draft":
                order.state = "waiting_for_hod"
                # Create To-Do for HOD
                self.env["mail.activity"].create(
                    {
                        "activity_type_id": self.env.ref(
                            "mail.mail_activity_data_todo"
                        ).id,
                        "res_model_id": self.env["ir.model"]
                        .search([("model", "=", "purchase.order")], limit=1)
                        .id,
                        "res_id": order.id,
                        "user_id": (
                            order.department_id.manager_id.user_id.id
                            if order.department_id.manager_id
                            else False
                        ),
                        "note": "Please review and approve/reject the PO.",
                    }
                )

    def action_confirm(self):
        for order in self:
            if order.state == "waiting_for_hod":
                order.state = "approved"
                # Deduct amount from assigned project
                if order.project_id:
                    order.project_id.amount -= order.amount

    def action_reject(self):
        for order in self:
            if order.state == "waiting_for_hod":
                order.state = "rejected"
                # Create To-Do for CP
                self.env["mail.activity"].create(
                    {
                        "activity_type_id": self.env.ref(
                            "mail.mail_activity_data_todo"
                        ).id,
                        "res_model_id": self.env["ir.model"]
                        .search([("model", "=", "purchase.order")], limit=1)
                        .id,
                        "res_id": order.id,
                        "user_id": order.user_id.id,
                        "note": "The PO has been rejected by HOD. Please revise and resubmit.",
                    }
                )
