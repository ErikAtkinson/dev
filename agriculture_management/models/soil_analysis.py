# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import fields, api, models, _


class SoilIndicator(models.Model):
    """Soil Indicator"""
    _name = "soil.indicator"
    _description = __doc__
    _rec_name = "name"

    name = fields.Char(string="Title", required=True)
    description = fields.Char(string="Description")
    type = fields.Selection([('physical', "Physical"), ('biological', "Biological"), ('chemical', "Chemical")],
                            string="Type")
    ideal_value = fields.Float(string="Ideal Value")

    @api.constrains('type')
    def _check_soil_indicator_type(self):
        for record in self:
            if not record.type:
                raise ValidationError(_("Please select a water indicator type: physical, chemical or biological"))


class SoilAnalysisIndicator(models.Model):
    """Soil Analysis Indicator"""
    _name = "soil.analysis.indicator"
    _description = __doc__
    _rec_name = "soil_indicator_id"

    soil_indicator_id = fields.Many2one("soil.indicator", string="Soil Indicator", required=True)
    type = fields.Selection(related="soil_indicator_id.type", string="Type")
    ideal_value = fields.Float(string="Ideal Value", related="soil_indicator_id.ideal_value")
    actual_value = fields.Float(string="Value")
    rate = fields.Float(string="Rating")
    soil_constraint = fields.Char(string="Constraint")
    soil_analysis_id = fields.Many2one("soil.analysis", string="Soil Analysis")


class SoilAnalysis(models.Model):
    """Soil Analysis"""
    _name = "soil.analysis"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = "name"

    name = fields.Char(string="Title", required=True)
    date_of_report = fields.Date(string="Date", default=fields.date.today())
    farm_id = fields.Many2one("agriculture.farm", string="Farm")
    slope = fields.Float(string="Slope (%)")
    drainage_system = fields.Selection([('surface', "Surface Drainage"), ('sub_surface', "Subsurface Drainage")],
                                       string="Drainage System")
    soil_texture = fields.Selection(
        [('sand', "Sand"), ('loamy_sand', "Loamy sand"), ('sandy_loam', "Sandy loam"), ('silt_loam', "Silt loam"),
         ('sandy_clay', "Sandy clay"), ('silty_clay', "Silty clay"), ('silt', "Silt")], string="Soil Texture")
    crop_ids = fields.Many2many("agriculture.crop", string="Crops")
    soil_quality = fields.Char(string="Soil Quality")
    quality_score = fields.Float(string="Overall Quality Score (%)")

    physical_si_ids = fields.One2many("soil.analysis.indicator", "soil_analysis_id",
                                      domain=[('type', '=', 'physical')])
    biological_si_ids = fields.One2many("soil.analysis.indicator", "soil_analysis_id",
                                        domain=[('type', '=', 'biological')])
    chemical_si_ids = fields.One2many("soil.analysis.indicator", "soil_analysis_id",
                                      domain=[('type', '=', 'chemical')])
