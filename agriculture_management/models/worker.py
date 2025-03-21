# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class AgricultureWorker(models.Model):
    """Worker Details"""
    _name = 'farm.worker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", required=True, translate=True)
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string='State',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char(string="Zip")
    contact_number = fields.Char(string="Phone")
