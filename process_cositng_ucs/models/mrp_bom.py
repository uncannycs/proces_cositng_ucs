# -*- coding: utf-8 -*-
from odoo import api, fields, models

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    mrp_costing_method = fields.Selection(related='company_id.mrp_costing_method')
    
    bom_material_cost_ids = fields.One2many('mrp.bom.material.cost', 'bom_id', string="Direct Material Cost")
    bom_labor_cost_ids = fields.One2many('mrp.bom.labor.cost', 'bom_id', string="Direct Labour Cost")
    bom_overhead_cost_ids = fields.One2many('mrp.bom.overhead.cost', 'bom_id', string="Direct Overhead Cost")

    total_material_cost = fields.Monetary(compute="_compute_total_costs", string="Total Material Cost")
    total_labor_cost = fields.Monetary(compute="_compute_total_costs", string="Total Labour Cost")
    total_overhead_cost = fields.Monetary(compute="_compute_total_costs", string="Total Overhead Cost")
    total_bom_cost = fields.Monetary(compute="_compute_total_costs", string="Total BOM Cost")

    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.depends('bom_material_cost_ids.total_cost', 'bom_labor_cost_ids.total_cost', 'bom_overhead_cost_ids.total_cost')
    def _compute_total_costs(self):
        for bom in self:
            bom.total_material_cost = sum(bom.bom_material_cost_ids.mapped('total_cost'))
            bom.total_labor_cost = sum(bom.bom_labor_cost_ids.mapped('total_cost'))
            bom.total_overhead_cost = sum(bom.bom_overhead_cost_ids.mapped('total_cost'))
            bom.total_bom_cost = bom.total_material_cost + bom.total_labor_cost + bom.total_overhead_cost

    def action_compute_bom_costs(self):
        for bom in self:
            # Auto compute material cost
            bom.bom_material_cost_ids.unlink()
            material_vals = []
            for line in bom.bom_line_ids:
                material_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.product_qty,
                    'uom_id': line.product_uom_id.id,
                    'unit_cost': line.product_id.standard_price,
                }))
            
            labor_vals = []
            overhead_vals = []
            
            if bom.mrp_costing_method == 'work_center':
                bom.bom_labor_cost_ids.unlink()
                bom.bom_overhead_cost_ids.unlink()
                for op in bom.operation_ids:
                    wc = op.workcenter_id
                    duration = op.time_cycle_manual or 0.0
                    hours = duration / 60.0
                    if wc.labor_costs_hour:
                        labor_vals.append((0, 0, {
                            'operation_id': op.id,
                            'workcenter_id': wc.id,
                            'duration': hours,
                            'cost_per_hour': wc.labor_costs_hour,
                        }))
                    if wc.overhead_costs_hour:
                        overhead_vals.append((0, 0, {
                            'operation_id': op.id,
                            'workcenter_id': wc.id,
                            'duration': hours,
                            'cost_per_hour': wc.overhead_costs_hour,
                        }))
            
            bom.write({
                'bom_material_cost_ids': material_vals,
                'bom_labor_cost_ids': labor_vals if bom.mrp_costing_method == 'work_center' else [],
                'bom_overhead_cost_ids': overhead_vals if bom.mrp_costing_method == 'work_center' else [],
            })

class MrpBomMaterialCost(models.Model):
    _name = 'mrp.bom.material.cost'
    _description = 'BOM Material Cost'

    bom_id = fields.Many2one('mrp.bom', string="BOM", ondelete='cascade')
    company_id = fields.Many2one(related='bom_id.company_id', store=True)
    currency_id = fields.Many2one(related='company_id.currency_id')
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    uom_id = fields.Many2one('uom.uom', string="UoM")
    unit_cost = fields.Monetary(string="Unit Cost")
    total_cost = fields.Monetary(compute="_compute_total_cost", string="Total Cost", store=True)

    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
            self.unit_cost = self.product_id.standard_price

class MrpBomLaborCost(models.Model):
    _name = 'mrp.bom.labor.cost'
    _description = 'BOM Labor Cost'

    bom_id = fields.Many2one('mrp.bom', string="BOM", ondelete='cascade')
    company_id = fields.Many2one(related='bom_id.company_id', store=True)
    currency_id = fields.Many2one(related='company_id.currency_id')
    operation_id = fields.Many2one('mrp.routing.workcenter', string="Operation")
    workcenter_id = fields.Many2one('mrp.workcenter', string="Work Center")
    duration = fields.Float(string="Duration (Hours)", default=0.0)
    cost_per_hour = fields.Monetary(string="Cost per Hour")
    total_cost = fields.Monetary(compute="_compute_total_cost", string="Total Cost", store=True)

    @api.depends('duration', 'cost_per_hour')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.duration * rec.cost_per_hour
            
    @api.onchange('operation_id')
    def _onchange_operation_id(self):
        if self.operation_id:
            self.workcenter_id = self.operation_id.workcenter_id
            self.duration = (self.operation_id.time_cycle_manual or 0.0) / 60.0
            if self.workcenter_id:
                self.cost_per_hour = self.workcenter_id.labor_costs_hour

    @api.onchange('workcenter_id')
    def _onchange_workcenter_id(self):
        if self.workcenter_id:
            self.cost_per_hour = self.workcenter_id.labor_costs_hour

class MrpBomOverheadCost(models.Model):
    _name = 'mrp.bom.overhead.cost'
    _description = 'BOM Overhead Cost'

    bom_id = fields.Many2one('mrp.bom', string="BOM", ondelete='cascade')
    company_id = fields.Many2one(related='bom_id.company_id', store=True)
    currency_id = fields.Many2one(related='company_id.currency_id')
    operation_id = fields.Many2one('mrp.routing.workcenter', string="Operation")
    workcenter_id = fields.Many2one('mrp.workcenter', string="Work Center")
    duration = fields.Float(string="Duration (Hours)", default=0.0)
    cost_per_hour = fields.Monetary(string="Cost per Hour")
    total_cost = fields.Monetary(compute="_compute_total_cost", string="Total Cost", store=True)

    @api.depends('duration', 'cost_per_hour')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.duration * rec.cost_per_hour

    @api.onchange('operation_id')
    def _onchange_operation_id(self):
        if self.operation_id:
            self.workcenter_id = self.operation_id.workcenter_id
            self.duration = (self.operation_id.time_cycle_manual or 0.0) / 60.0
            if self.workcenter_id:
                self.cost_per_hour = self.workcenter_id.overhead_costs_hour

    @api.onchange('workcenter_id')
    def _onchange_workcenter_id(self):
        if self.workcenter_id:
            self.cost_per_hour = self.workcenter_id.overhead_costs_hour
