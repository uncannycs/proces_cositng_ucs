# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mrp_costing_method = fields.Selection(
        related='company_id.mrp_costing_method',
        readonly=False,
        string="Manufacturing Process Costing"
    )
