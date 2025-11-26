# -*- coding: utf-8 -*-
from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # External unique reference, used for upsert
    x_external_id = fields.Char(index=True, copy=False)
