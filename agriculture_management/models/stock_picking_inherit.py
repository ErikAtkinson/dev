# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class AgricultureStockPicking(models.Model):
    """Agriculture Stock Picking"""
    _inherit = 'stock.picking'
    _description = __doc__

    agriculture_season_id = fields.Many2one('agriculture.season', string="Agriculture Season")
