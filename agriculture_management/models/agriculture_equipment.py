# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class EquipmentTags(models.Model):
    """Equipment Tags"""
    _name = "equipment.tags"
    _description = __doc__
    _rec_name = 'name'

    color = fields.Integer(default=1)
    name = fields.Char(string="Name", translate=True)


class AgricultureFleet(models.Model):
    """Fleets"""
    _name = 'agriculture.fleet'
    _inherits = {'product.product': 'product_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    color = fields.Integer(default=1)
    name = fields.Char(related="product_id.name", store=True, readonly=False, required=True, inherited=True,
                       translate=False)
    is_fleet = fields.Boolean(related="product_id.is_fleet", default=True, readonly=False, store=True)
    detailed_type = fields.Selection(related="product_id.detailed_type", default='service', readonly=False, store=True)
    product_id = fields.Many2one('product.product', required=True, ondelete='cascade', auto_join=True, index=True,
                                 string=' Product')
    tags_ids = fields.Many2many('equipment.tags', string="Tags")
    farm_id = fields.Many2one("agriculture.farm")

    # unused
    avatar = fields.Binary(string=" Image")


class AgricultureEquipment(models.Model):
    """Equipments"""
    _name = "agriculture.equipment"
    _inherits = {'product.product': 'product_id'}
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(related="product_id.name", store=True, readonly=False, required=True, inherited=True,
                       translate=False)
    is_equipment = fields.Boolean(related="product_id.is_equipment", default=True, readonly=False, store=True)
    detailed_type = fields.Selection(related="product_id.detailed_type", default='service', readonly=False, store=True)
    product_id = fields.Many2one('product.product', required=True, ondelete='cascade', auto_join=True, index=True,
                                 string=' Product')

    farmer_id = fields.Many2one("res.partner", string="Farmer ", domain=[('is_farmer', '=', True)])
    is_farmer_property = fields.Boolean(string="Own by Farmer")
    tags_ids = fields.Many2many('equipment.tags', string="Tags")
    description = fields.Text(string="Description", translate=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    # unused
    avatar = fields.Binary(string=" Image")
    price_of_equipment = fields.Monetary(string="Price/Hour")
