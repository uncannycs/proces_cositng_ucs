# -*- coding: utf-8 -*-
from odoo import fields, models

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    labor_costs_hour = fields.Float(string="Labour Costs per hour", default=0.0)
    overhead_costs_hour = fields.Float(string="Overhead Costs per hour", default=0.0)
