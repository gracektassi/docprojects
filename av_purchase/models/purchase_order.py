# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    project_id = fields.Many2one("project.project", string="Assigned Project")

    department_id = fields.Many2one(
        'hr.department', string="Department",
        default=lambda self: self._get_current_department(), tracking=True,
    )
    project_id_readonly = fields.Boolean(
        compute="_compute_project_id_readonly",
    )
    product_readonly = fields.Boolean(
        compute="_compute_project_id_readonly",
    )



    def _get_current_department(self):

        employee = self.env['hr.employee'].sudo().search([
            ('user_id', '=', self.env.user.id),
        ], limit=1)
        return employee.department_id if employee else self.env['hr.department']



    @api.constrains("amount")
    def _check_positive_amount(self):
        """
        Ensure the purchase order amount is strictly positive.
        """
        for order in self:
            if order.amount <= 0:
                raise ValidationError(
                    "The amount must be strictly positive. Please enter a valid amount."
                )


    def button_cancel(self):
        # Call the parent method to execute its original functionality
        result = super(PurchaseOrder, self).button_confirm()

        for order in self:
            # Create To-Do for CP
            self.env["mail.activity"].create(
                {
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "res_model_id": self.env["ir.model"]
                    .search([("model", "=", "purchase.order")], limit=1)
                    .id,
                    "res_id": order.id,
                    "user_id": order.user_id.id,
                    "note": "The PO has been rejected by HOD. Please revise and resubmit.",
                }
            )
        # Return the original result or modified result
        return result

    def button_confirm(self):
        # Call the parent method to execute its functionality
        # Call the parent method to execute its original functionality
        result = super(PurchaseOrder, self).button_confirm()

        # Add your custom logic here
        for order in self:
            # Ensure at least one product is added
            if not order.order_line:
                raise ValidationError(
                    "You must add at least one product to the order before submitting."
                )

            if order.state == "draft":
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

            if not order.project_id:
                continue  # Skip if no project is linked

            total_amount = sum(order.order_line.mapped("price_subtotal"))

            if order.project_id.amount < total_amount:
                raise ValidationError(
                    f"The assigned project '{order.project_id.name}' does not have enough funds "
                    f"to cover this purchase order amount ({total_amount:.2f}). "
                    "Please adjust the budget or choose another project."
                )
            if order.project_id.state != "in_progress":
                raise ValidationError("Please start or resume this project first.")

            # Deduct the total amount from the project budget
            order.project_id.amount -= total_amount

        # Return the original result or modified result
        return result

    def action_submit(self):
        """
        Save changes to the current record.

        :param values: A dictionary of field names and their new values.
        Example: {'field_name1': value1, 'field_name2': value2}
        """
        for order in self:
            if not order.order_line:
                raise ValidationError(
                    "You must add products to the order before submitting."
                )
            # Write the new values to the record
            self.write({"state": "sent"})

    def write(self, vals):
        # Track changes to state, trip_type and passengers
        """
        Save changes to the current record.

        :param values: A dictionary of field names and their new values.
        Example: {'field_name1': value1, 'field_name2': value2}
        """
        for order in self:
            if not order.order_line:
                raise ValidationError(
                    "You must add products to the order before submitting."
                )
            # Write the new values to the record

        result = super(PurchaseOrder, self).write(vals)  # Apply the updates

        return result

    @api.model_create_multi
    def create(self, vals):
        for order in self:
            if not order.order_line:
                raise ValidationError(
                    "You must add products to the order before submitting."
                )
            # Write the new values to the record

        result = super(PurchaseOrder, self).create(vals)  # Apply the updates

        return result

    @api.depends("state", "create_uid")
    def _compute_project_id_readonly(self):
        """
        Compute whether the project_id field should be readonly:
        - It is readonly if the user is NOT the HOD.
        - It is readonly if the purchase order state is NOT 'sent'.
        """
        for order in self:
            user = self.env.user
            # Get the creator's department
            creator_department = order.create_uid.employee_id.department_id

            # Check if the current user is the HOD of the creator's department
            is_hod = (
                creator_department.manager_id.user_id == user
                if creator_department and creator_department.manager_id
                else False
            )

            has_hod = user.has_group(
                "av_purchase.av_purchase_hod"
            )  # Check if user is an admin
            order.project_id_readonly = not (
                is_hod and order.state == "sent" and has_hod
            )

            # Check if the product can be edited only hod can edit unless it is a draft
            order.product_readonly = not (
                (is_hod and has_hod and order.state == "sent") or order.state == "draft"
            )

    def button_cancel_action(self):
        user = self.env.user
        # Get the creator's department
        creator_department = self.create_uid.employee_id.department_id

        # Check if the current user is the HOD of the creator's department
        is_hod = (
            creator_department.manager_id.user_id == user
            if creator_department and creator_department.manager_id
            else False
        )

        has_hod = user.has_group("av_purchase.av_purchase_hod")
        # Check if the current user belongs to the 'av_purchase.av_purchase_hod' group
        if is_hod and has_hod:
            # Execute the original button_cancel method as sudo
            # Write the new values to the record
            self.write({"state": "cancel"})
            return self.sudo().button_cancel()
        else:
            # Proceed with normal cancelation for non-HOD users
            return self.button_cancel()
