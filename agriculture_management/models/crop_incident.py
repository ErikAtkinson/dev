# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class CropIncident(models.Model):
    """Crop Incident"""
    _name = 'crop.incident'
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Image")
    name = fields.Char(string="Name", required=True)


class SeasonCropIncident(models.Model):
    """Season wise Crop Incident"""
    _name = 'season.crop.incident'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'crop_incident_id'

    crop_incident_id = fields.Many2one('crop.incident', required=True)
    date = fields.Date(string="Date of Incident")
    description = fields.Text(string="Description")
    value = fields.Monetary(string="Value")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")

    @api.constrains('date', 'farm_season_id')
    def _check_incident_date(self):
        for record in self:
            if record.farm_season_id and record.date:
                if record.farm_season_id.start_date and record.farm_season_id.end_date:
                    if record.date < record.farm_season_id.start_date or record.date > record.farm_season_id.end_date:
                        raise ValidationError(_(
                            "The crop incident issue date must fall between the start date and end date of the season."))
