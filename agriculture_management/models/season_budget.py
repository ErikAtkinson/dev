# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class SeasonBudget(models.Model):
    """Season Budget"""
    _name = "season.budget"
    _description = __doc__
    _rec_name = 'budget_type'

    budget_type = fields.Selection([('fertiliser', "Fertilisers"), ('pesticide', "Pesticides"), ('seed', "Seeds"),
                                    ('labour_cost_type', "Labour Cost"), ('equipment', "Equipments"), ('fuel', "Fuels"),
                                    ('sallary', "Salaries"), ('other', "Others")], string="Budget Type", required=True)
    qty = fields.Float(string="Qty")
    unit_id = fields.Many2one("uom.uom", string="Unit")
    price = fields.Monetary(string="Price")
    total_price = fields.Monetary(string="Total Price", compute="_total_price")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", required=True, domain="[('id', 'in', crop_ids)]")

    @api.onchange('crop_id')
    def _onchange_crop_id(self):
        for rec in self:
            rec.unit_id = rec.crop_id.uom_id.id

    @api.depends('qty', 'price')
    def _total_price(self):
        for rec in self:
            rec.total_price = rec.qty * rec.price
