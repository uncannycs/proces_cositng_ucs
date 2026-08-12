# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    mrp_costing_method = fields.Selection([
        ('manual', 'Manually'),
        ('work_center', 'Work-Center')
    ], string="Manufacturing Process Costing", default='manual')
