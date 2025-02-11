# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    project_id = fields.Many2one(
        "project.project",
        string="Assigned Project",
        domain=lambda self: self._get_project_domain(),
    )