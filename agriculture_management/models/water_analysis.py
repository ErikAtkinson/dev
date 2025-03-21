# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import fields, api, models, _


class WaterIndicator(models.Model):
    """Water Indicator"""
    _name = "water.indicator"
    _description = __doc__
    _rec_name = "parameter"

    parameter = fields.Char(string="Parameter", required=True)
    type = fields.Selection([('physical', "Physical"), ('chemical', "Chemical"),
                             ('bacteriological', "Bacteriological")], string="Type")

    @api.constrains('type')
    def _check_water_indicator_type(self):
        for record in self:
            if not record.type:
                raise ValidationError(_("Please select a water indicator type: physical, chemical or bacteriological"))


class WaterAnalysisIndicator(models.Model):
    """Water Analysis Indicator"""
    _name = "water.analysis.indicator"
    _description = __doc__
    _rec_name = "water_indicator_id"

    water_indicator_id = fields.Many2one("water.indicator", string="Water Indicator", required=True)
    type = fields.Selection(related="water_indicator_id.type", string="Type")
    unit = fields.Char(string="Unit")
    test_remarks = fields.Char(string="Test Remarks")
    requirements = fields.Char(string="Requirements")
    methods = fields.Char(string="Methods")
    water_analysis_id = fields.Many2one("water.analysis", string="Water Analysis")


class WaterAnalysis(models.Model):
    """Water Analysis"""
    _name = "water.analysis"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = "sample"

    sample = fields.Char(string="Sample ID", required=True)
    farm_id = fields.Many2one("agriculture.farm", string="Farm")
    farmer_id = fields.Many2one(related="farm_id.farmer_id", string="Farmer")
    crop_ids = fields.Many2many("agriculture.crop", string="Crops")
    analysis_date = fields.Date(string="Analysis Date", default=fields.date.today())
    report_date = fields.Date(string="Report Date")
    water_use = fields.Char(string="Water Used")
    water_source = fields.Char(string="Water Source")

    physical_ids = fields.One2many("water.analysis.indicator", "water_analysis_id", domain=[('type', '=', 'physical')])
    chemical_ids = fields.One2many("water.analysis.indicator", "water_analysis_id", domain=[('type', '=', 'chemical')])
    bacteriological_ids = fields.One2many("water.analysis.indicator", "water_analysis_id",
                                          domain=[('type', '=', 'bacteriological')])
