# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class AgricultureProduct(models.Model):
    """Agriculture Product"""
    _inherit = "product.product"
    _description = __doc__

    is_fertiliser = fields.Boolean(string="Fertiliser")
    is_pesticide = fields.Boolean(string="Pesticide")
    is_seed = fields.Boolean(string="Seed")
    is_equipment = fields.Boolean(string="Equipment")
    is_fleet = fields.Boolean(string="Fleet")


class AgricultureProductTemplate(models.Model):
    """Agriculture Product Template"""
    _inherit = "product.template"
    _description = __doc__

    is_fertiliser = fields.Boolean(string="Fertiliser")
    is_pesticide = fields.Boolean(string="Pesticide")
    is_seed = fields.Boolean(string="Seed")
    is_equipment = fields.Boolean(string="Equipment")
    is_fleet = fields.Boolean(string="Fleet")


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = __doc__

    agriculture_season_id = fields.Many2one('agriculture.season', string="Season")
