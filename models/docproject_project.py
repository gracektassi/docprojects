# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Project(models.Model):
    _inherit = 'project.project'

    amount = fields.Float(string="Amount")
    department_id = fields.Many2one('hr.department', string="Department")
    hod_id = fields.Many2one('hr.employee', string="Head of Department", compute="_compute_hod", store=True)

    @api.depends('department_id')
    def _compute_hod(self):
        for record in self:
            if record.department_id.manager_id:
                record.hod_id = record.department_id.manager_id
            else:
                record.hod_id = False

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('project.group_project_manager'):  # Only project admins can create projects
            raise ValidationError("You are not allowed to create a project.")
        return super(Project, self).create(vals)

    @api.constrains('department_id')
    def _check_department_manager(self):
        for record in self:
            if not record.department_id.manager_id:
                raise ValidationError("The department must have a manager to assign the Head of Department.")
