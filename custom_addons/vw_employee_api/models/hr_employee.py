# -*- coding: utf-8 -*-
from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Stores the GUID from Power Apps / Dataverse for idempotent syncs
    x_powerapps_id = fields.Char(index=True, copy=False)
