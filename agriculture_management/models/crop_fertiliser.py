# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class CropFertiliser(models.Model):
    """Crop Fertiliser"""
    _name = "crop.fertiliser"
    _inherits = {'product.product': 'product_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(related="product_id.name", store=True, readonly=False, required=True, inherited=True,
                       translate=False)
    is_fertiliser = fields.Boolean(related="product_id.is_fertiliser", default=True, readonly=False, store=True)
    detailed_type = fields.Selection(related="product_id.detailed_type", default='product', readonly=False, store=True)
    product_id = fields.Many2one('product.product', required=True, ondelete='cascade', auto_join=True, index=True,
                                 string=' Product')

    type = fields.Selection([('organic', "Organic"), ('non_organic', "Non-Organic")], string="Type")
    uses_of_fertiliser = fields.Selection([('liquid_form', "Liquid Form"), ('solid_form', "Solid Form")],
                                          string="Use of")
    pkg_qty = fields.Float(string="Package Qty")
    description = fields.Text(string="Description")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    # UnUsed
    avatar = fields.Binary(string=" Image")
    cost = fields.Monetary(string=" Cost")
    unit_id = fields.Many2one("uom.uom", string="Package Size")
