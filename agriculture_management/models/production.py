# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import date
from odoo.exceptions import ValidationError
from odoo import fields, api, models, _


class AgricultureWarehouse(models.Model):
    """Agriculture Warehouse"""
    _name = "agriculture.warehouse"
    _description = __doc__

    avatar = fields.Binary(string="Avatar")


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    avatar = fields.Binary(string="Avatar")
    crop_production_ids = fields.One2many("crop.production", "agriculture_warehouse_id", string="Crop Productions")
    product_count = fields.Integer(compute='_get_season_product')

    consume_stock_location_id = fields.Many2one('stock.location', string="Consume Location")

    def _get_season_product(self):
        for record in self:
            record.product_count = self.env["crop.production"].search_count(
                [('agriculture_warehouse_id', '=', self.id)])

    def view_production_item(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Production Item'),
            'view_mode': 'tree,form',
            'res_model': "crop.production",
            'domain': [('agriculture_warehouse_id', '=', self.id)],
        }


class CropProduction(models.Model):
    """Crop Production"""
    _name = "crop.production"
    _description = __doc__
    _rec_name = 'crop_id'

    date = fields.Date(string="Date")
    description = fields.Char(string="Description")
    product = fields.Many2one(related="crop_id.product_id")
    qty = fields.Float(string="Qty")
    qty_on_hand = fields.Float(string="Qty on Hand", required=True)
    unit_id = fields.Many2one(related="crop_id.uom_id", string="Unit")
    price = fields.Monetary(string="Price")
    total_production_price = fields.Monetary(string="Total", compute="_compute_production_income")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    agriculture_warehouse_id = fields.Many2one("stock.warehouse", string="WareHouse", required=True)
    farm_season_id = fields.Many2one("agriculture.season", string="Season", ondelete='cascade')
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", required=True, domain="[('id', 'in', crop_ids)]")
    stages = fields.Selection([('draft_stock', 'Draft Stocks'), ('update_stock', 'Updated in Inventory')],
                              default="draft_stock", string="Status")

    def action_update_stock(self):
        data = {
            'location_id': self.agriculture_warehouse_id.lot_stock_id.id,
            'product_id': self.crop_id.product_id.id,
            'quantity': self.qty_on_hand,
            'product_uom_id': self.unit_id.id,
            'inventory_date': date.today(),
            'in_date': date.today(),
            'user_id': self.env.user.id,
        }
        self.env['stock.quant'].create(data)
        self.stages = 'update_stock'
        return {
            'type': 'ir.actions.act_window',
            'name': _('Agriculture Product'),
            'view_mode': 'form',
            'res_model': "product.product",
            'res_id': self.crop_id.product_id.id,
        }

    @api.constrains('date', 'farm_season_id')
    def _check_production_date(self):
        for record in self:
            if record.farm_season_id and record.date:
                if record.farm_season_id.start_date and record.farm_season_id.end_date:
                    if record.date < record.farm_season_id.start_date or record.date > record.farm_season_id.end_date:
                        raise ValidationError(_(
                            "The crop production date must fall between the start date and end date of the season."))

    @api.depends('qty_on_hand', 'price')
    def _compute_production_income(self):
        for rec in self:
            rec.total_production_price = rec.qty_on_hand * rec.price
