# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class CropSeed(models.Model):
    """Crop Seed"""
    _name = "crop.seed"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'product.product': 'product_id'}
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(related="product_id.name", store=True, readonly=False, required=True, inherited=True,
                       translate=False)
    is_seed = fields.Boolean(related="product_id.is_seed", default=True, readonly=False, store=True)
    detailed_type = fields.Selection(related="product_id.detailed_type", default='product', readonly=False, store=True)
    product_id = fields.Many2one('product.product', required=True, ondelete='cascade', auto_join=True, index=True,
                                 string=' Product')
    pkg_qty = fields.Float(string="Package Qty")
    description = fields.Text(string="Description")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    # unused
    avatar = fields.Binary(string=" Image")
    cost = fields.Monetary(string=" Cost")
    unit_id = fields.Many2one("uom.uom", string="Package Size")


class SeedsBySeason(models.Model):
    """Seed uses by Season"""
    _name = "farm.crop.seed"
    _description = __doc__
    _rec_name = 'seed_id'

    seed_id = fields.Many2one("crop.seed", string="Seed", required=True)
    pkg_qty = fields.Float(related='seed_id.pkg_qty')
    qty = fields.Float(string="Number of Package", required=True, default=1)
    unit = fields.Many2one(related='seed_id.uom_id', string="Package Size")
    cost = fields.Monetary(string="Cost")
    total_seed_price = fields.Monetary(string="Total Price", compute="_total_price")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    seed_bill_status = fields.Selection([('pending', "Pending"), ('bill_created', "Bill Created")],
                                        string="Bill Status", default="pending", readonly=True)
    bill_id = fields.Many2one('account.move', string="Bill")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season")
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")

    delivery_order_id = fields.Many2one('stock.picking')
    delivery_order_state = fields.Selection(related='delivery_order_id.state', string="Order Status")

    @api.onchange('seed_id')
    def seed_product_price(self):
        for rec in self:
            if rec.seed_id:
                rec.cost = rec.seed_id.standard_price

    @api.depends('qty', 'cost')
    def _total_price(self):
        for rec in self:
            rec.total_seed_price = rec.qty * rec.cost

    def action_crop_seed_bill(self):
        crop_seed_view = self.env.ref('agriculture_management.crop_seed_bill_form_view').id
        return {
            'name': _('Crop Seeds'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'crop.seed.bill',
            'view_id': crop_seed_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }

    def action_crop_seed_consume_order(self):
        crop_seed_consume_view = self.env.ref('agriculture_management.seed_consume_order_form_view').id
        return {
            'name': _('Crop Seeds'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'seed.consume.order',
            'view_id': crop_seed_consume_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }
