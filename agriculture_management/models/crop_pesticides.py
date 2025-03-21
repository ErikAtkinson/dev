# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class CropPesticides(models.Model):
    """Crop Pesticides"""
    _name = "crop.pesticides"
    _inherits = {'product.product': 'product_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(related="product_id.name", store=True, readonly=False, required=True, inherited=True,
                       translate=False)
    is_pesticide = fields.Boolean(related="product_id.is_pesticide", default=True, readonly=False, store=True)
    detailed_type = fields.Selection(related="product_id.detailed_type", default='product', readonly=False, store=True)
    product_id = fields.Many2one('product.product', required=True, ondelete='cascade', auto_join=True, index=True,
                                 string=' Product')
    pkg_qty = fields.Float(string="Package Qty")
    description = fields.Text(string="Description")
    threat_level = fields.Selection(
        [('poisonous', "Poisonous"), ('flammable', "Flammable"), ('explosive', "Explosive"), ('corrosive', "Corrosive"),
         ('danger', "Danger"), ('warning', "Warning"), ('caution', "Caution")], string="Threat Danger Level")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    # unused
    avatar = fields.Binary(string=" Image")
    cost = fields.Monetary(string=" Cost")
    unit_id = fields.Many2one("uom.uom", string="Package Size")
