# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = "project.project"

    amount = fields.Float(string="Amount")
    department_id = fields.Many2one("hr.department", string="Department")
    hod_id = fields.Many2one(
        "hr.employee", string="Head of Department", compute="_compute_hod", store=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("stopped", "Stopped"),
        ],
        string="Status",
        default="draft",
        readonly=True,
        tracking=True,
    )

    @api.depends("department_id")
    def _compute_hod(self):
        for record in self:
            if record.department_id.manager_id:
                record.hod_id = record.department_id.manager_id
            else:
                record.hod_id = False

    @api.depends("amount")
    def _compute_amount(self):
        for record in self:
            if record.amount<0:
                raise ValidationError(
                    "The department must have a manager to assign the Head of Department."
                )


    @api.constrains("department_id")
    def _check_department_manager(self):
        for record in self:
            if not record.department_id.manager_id:
                raise ValidationError(
                    "The department must have a manager to assign the Head of Department."
                )

    def action_start_project(self):
        """
        Action to set the start date to today and mark the project as in progress.
        """

        for project in self:
            if project.state == "in_progress":
                raise ValidationError("The project is already in progress.")
            if not project.date_start:
                raise ValidationError("Start date cannot be empty when the project is in progress.")

            project.state = "in_progress"

    def action_stop_project(self):
        """
        Action to stop the project. Sets the stop date and updates the state to 'stopped'.
        """
        for project in self:
            if project.state == "stopped":
                raise ValidationError("The project is already stopped.")
            if project.state == "draft":
                raise ValidationError(
                    "You cannot stop a project that has not been started."
                )
            project.state = "stopped"
    def action_set_todraft(self):
        """
        Action to set the start date to today and mark the project as in progress.
        """

        for project in self:
            if project.state == "draft":
                raise ValidationError("The project is already in daft.")
            if not project.date_start:
                raise ValidationError("Start date cannot be empty when the project is in progress.")

            project.state = "draft"
