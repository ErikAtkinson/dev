# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class CropDisease(models.Model):
    """Crop Disease"""
    _name = "crop.disease"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Image")
    name = fields.Char(string="Name", required=True)
    crop_ids = fields.Many2many("agriculture.crop", string="Affected Crops")
    sample_ids = fields.One2many("crop.disease.sample", "crop_disease_id", string="Samples")
    treatments = fields.Text(string="Treatments")
    prescription = fields.Text(string="Prescriptions")


class CropDiseaseSample(models.Model):
    """Crop Disease Sample"""
    _name = "crop.disease.sample"
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Image")
    name = fields.Char(string="Name")
    disease_id = fields.Many2one("crop.disease", string="Disease", ondelete='cascade')
    crop_disease_id = fields.Many2one("crop.disease", ondelete='cascade')
