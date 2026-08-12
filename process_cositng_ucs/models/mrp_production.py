# -*- coding: utf-8 -*-
from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mrp_costing_method = fields.Selection(related='company_id.mrp_costing_method')

    prod_material_cost_ids = fields.One2many('mrp.production.material.cost', 'production_id', string="Direct Material Costs")
    prod_labor_cost_ids = fields.One2many('mrp.production.labor.cost', 'production_id', string="Direct Labour Costs")
    prod_overhead_cost_ids = fields.One2many('mrp.production.overhead.cost', 'production_id', string="Direct Overhead Costs")

    est_material_cost = fields.Monetary(compute="_compute_est_costs", string="Estimated Material Cost")
    est_labor_cost = fields.Monetary(compute="_compute_est_costs", string="Estimated Labour Cost")
    est_overhead_cost = fields.Monetary(compute="_compute_est_costs", string="Estimated Overhead Cost")
    est_total_cost = fields.Monetary(compute="_compute_est_costs", string="Estimated Total Cost")
    
    act_material_cost = fields.Monetary(compute="_compute_act_costs", string="Actual Material Cost", store=True)
    act_labor_cost = fields.Monetary(compute="_compute_act_costs", string="Actual Labour Cost", store=True)
    act_overhead_cost = fields.Monetary(compute="_compute_act_costs", string="Actual Overhead Cost", store=True)
    act_total_cost = fields.Monetary(compute="_compute_act_costs", string="Actual Total Cost", store=True)
    
    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.depends('prod_material_cost_ids.total_cost', 'prod_labor_cost_ids.total_cost', 'prod_overhead_cost_ids.total_cost')
    def _compute_est_costs(self):
        for prod in self:
            prod.est_material_cost = sum(prod.prod_material_cost_ids.mapped('total_cost'))
            prod.est_labor_cost = sum(prod.prod_labor_cost_ids.mapped('total_cost'))
            prod.est_overhead_cost = sum(prod.prod_overhead_cost_ids.mapped('total_cost'))
            prod.est_total_cost = prod.est_material_cost + prod.est_labor_cost + prod.est_overhead_cost

    @api.depends('move_raw_ids.quantity', 'workorder_ids.duration')
    def _compute_act_costs(self):
        for prod in self:
            act_mat = sum((move.quantity * move.product_id.standard_price) for move in prod.move_raw_ids if move.state != 'cancel')
            act_lab = sum((wo.duration / 60.0 * wo.workcenter_id.labor_costs_hour) for wo in prod.workorder_ids if wo.workcenter_id.labor_costs_hour)
            act_ovh = sum((wo.duration / 60.0 * wo.workcenter_id.overhead_costs_hour) for wo in prod.workorder_ids if wo.workcenter_id.overhead_costs_hour)
                
            prod.act_material_cost = act_mat
            prod.act_labor_cost = act_lab
            prod.act_overhead_cost = act_ovh
            prod.act_total_cost = act_mat + act_lab + act_ovh

    @api.model_create_multi
    def create(self, vals_list):
        records = super(MrpProduction, self).create(vals_list)
        for prod in records:
            prod._generate_costing_lines()
        return records

    def write(self, vals):
        res = super(MrpProduction, self).write(vals)
        if 'product_qty' in vals or 'bom_id' in vals:
            for prod in self:
                if prod.state == 'draft':
                    prod.action_compute_production_costs()
        return res

    def _generate_costing_lines(self):
        for prod in self:
            if not prod.bom_id:
                continue
            
            bom = prod.bom_id
            qty_ratio = prod.product_qty / (bom.product_qty or 1.0)
            
            # Materials
            mat_vals = []
            for mat in bom.bom_material_cost_ids:
                mat_vals.append({
                    'production_id': prod.id,
                    'product_id': mat.product_id.id,
                    'quantity': mat.quantity * qty_ratio,
                    'uom_id': mat.uom_id.id,
                    'unit_cost': mat.unit_cost,
                })
            if mat_vals:
                self.env['mrp.production.material.cost'].create(mat_vals)
                
            # Labor
            lab_vals = []
            for lab in bom.bom_labor_cost_ids:
                lab_vals.append({
                    'production_id': prod.id,
                    'operation_id': lab.operation_id.id,
                    'workcenter_id': lab.workcenter_id.id,
                    'duration': lab.duration * qty_ratio,
                    'cost_per_hour': lab.cost_per_hour,
                })
            if lab_vals:
                self.env['mrp.production.labor.cost'].create(lab_vals)
                
            # Overhead
            ovh_vals = []
            for ovh in bom.bom_overhead_cost_ids:
                ovh_vals.append({
                    'production_id': prod.id,
                    'operation_id': ovh.operation_id.id,
                    'workcenter_id': ovh.workcenter_id.id,
                    'duration': ovh.duration * qty_ratio,
                    'cost_per_hour': ovh.cost_per_hour,
                })
            if ovh_vals:
                self.env['mrp.production.overhead.cost'].create(ovh_vals)

    def action_compute_production_costs(self):
        self.prod_material_cost_ids.unlink()
        self.prod_labor_cost_ids.unlink()
        self.prod_overhead_cost_ids.unlink()
        self._generate_costing_lines()

class MrpProductionMaterialCost(models.Model):
    _name = 'mrp.production.material.cost'
    _description = 'Production Material Cost'

    production_id = fields.Many2one('mrp.production', string="Production", ondelete='cascade')
    company_id = fields.Many2one(related='production_id.company_id', store=True)
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

class MrpProductionLaborCost(models.Model):
    _name = 'mrp.production.labor.cost'
    _description = 'Production Labor Cost'

    production_id = fields.Many2one('mrp.production', string="Production", ondelete='cascade')
    company_id = fields.Many2one(related='production_id.company_id', store=True)
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

class MrpProductionOverheadCost(models.Model):
    _name = 'mrp.production.overhead.cost'
    _description = 'Production Overhead Cost'

    production_id = fields.Many2one('mrp.production', string="Production", ondelete='cascade')
    company_id = fields.Many2one(related='production_id.company_id', store=True)
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
