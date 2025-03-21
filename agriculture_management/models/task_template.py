# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class TemplateDetails(models.Model):
    """Template Details"""
    _name = "template.details"
    _description = __doc__
    _rec_name = 'crop_phase'

    crop_phase = fields.Selection([('planing', "Crop Planing"), ('purchase_of_crop_inputs', "Purchase of Crop Inputs"),
                                   ('soil_preparation', "Soil Preparation"), ('planting', "Planting"),
                                   ('monitoring', "Monitoring"), ('harvesting', "Harvesting"),
                                   ('processing', "Processing"), ('storage', "At Storage")], required=True,
                                  string=" Crop Phase")
    task_title = fields.Char(string="Task Title", required=True)
    task_description = fields.Char(string="Task Description")
    task_template_id = fields.Many2one('task.template')


class ReuseTemplateDetails(models.Model):
    """Template Details"""
    _name = "reuse.template.details"
    _description = __doc__
    _rec_name = 'crop_phase'

    crop_phase = fields.Selection([('planing', "Crop Planing"), ('purchase_of_crop_inputs', "Purchase of Crop Inputs"),
                                   ('soil_preparation', "Soil Preparation"), ('planting', "Planting"),
                                   ('monitoring', "Monitoring"), ('harvesting', "Harvesting"),
                                   ('processing', "Processing"), ('storage', "At Storage")], required=True,
                                  string=" Crop Phase")
    task_title = fields.Char(string="Task Title", required=True)
    task_description = fields.Char(string="Task Description")
    assignees_ids = fields.Many2many('res.users', string="Assign To")
    date_deadline = fields.Date(string="Deadline Date")


class TaskTemplate(models.Model):
    """Task Template"""
    _name = "task.template"
    _description = __doc__
    _rec_name = 'template_name'

    template_name = fields.Char(string="Name", required=True)
    template_details_ids = fields.One2many('template.details', 'task_template_id', string="Template Details")
