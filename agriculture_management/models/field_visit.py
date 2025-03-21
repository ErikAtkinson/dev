# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class FieldVisit(models.Model):
    """Field Visit"""
    _name = "field.visit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'crop_id'

    officer_id = fields.Many2one('res.partner', string="Visiting Officer", domain=[('is_agronomist', '=', True)],
                                 required=True)
    date_of_visit = fields.Date(string="Date of Visit")
    instruction_type = fields.Selection([('disease_control', "Disease Control"),
                                         ('nutrition_required', "Nutrition Required")], string="Instruction Type")
    current_status_of_crop = fields.Html(string="Current Status of Crop")
    instructions = fields.Html(string="Instructions")
    crop_images_ids = fields.One2many('crop.images', 'field_visit_id', string="Crop Images")
    farm_season_id = fields.Many2one('agriculture.season', string="Crop Season")
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", required=True, domain="[('id', 'in', crop_ids)]")

    @api.constrains('date_of_visit', 'farm_season_id')
    def _check_date_of_visit(self):
        for record in self:
            if record.farm_season_id and record.date_of_visit:
                start_date = record.farm_season_id.start_date
                end_date = record.farm_season_id.end_date
                if start_date and end_date and not (start_date <= record.date_of_visit <= end_date):
                    raise ValidationError(_(
                        "The field visiting date must fall between the start date and end date of the season."))


class CropImages(models.Model):
    """Crop Images"""
    _name = "crop.images"
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Image", required=True)
    name = fields.Char(string="Name", required=True, size=36)
    field_visit_id = fields.Many2one("field.visit", ondelete='cascade')
