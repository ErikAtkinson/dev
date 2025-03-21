# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    farm_season_id = fields.Many2one(related='project_id.farm_season_id', string="Farm Season", store=True)
    farm_id = fields.Many2one('agriculture.farm', string="Farm")
    crop_id = fields.Many2one("agriculture.crop", string="Crop")
    status = fields.Selection([('a_start', "Start"), ('b_in_progress', "In Progress"), ('c_complete', "Complete")],
                              string="Status ", default='a_start')
    crop_phase = fields.Selection(
        [('planing', "Crop Planing"), ('purchase_of_crop_inputs', "Purchase of Crop Inputs"),
         ('soil_preparation', "Soil Preparation"), ('planting', "Planting"), ('monitoring', "Monitoring"),
         ('harvesting', "Harvesting"), ('processing', "Processing"), ('storage', "At Storage")], string=" Crop Phase")

    def a_start_to_b_in_progress(self):
        self.status = 'b_in_progress'

    def b_in_progress_to_c_complete(self):
        self.status = 'c_complete'


class AgricultureTask(models.Model):
    """Agriculture Task"""
    _name = "agriculture.task"
    _description = __doc__
    _rec_name = 'title'

    title = fields.Char(string="Title", required=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Assign To")
    start_date = fields.Date(string="Start Date")
    expected_end_date = fields.Date(string="Expected End Date")
    agriculture_season_id = fields.Many2one('agriculture.season', ondelete='cascade')
    crop_ids = fields.Many2many(related="agriculture_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")
    agriculture_task_id = fields.Many2one('project.task', string="Task")
    status = fields.Selection(related='agriculture_task_id.status', string="Task Status")
    crop_phase = fields.Selection(
        [('planing', "Crop Planing"), ('purchase_of_crop_inputs', "Purchase of Crop Inputs"),
         ('soil_preparation', "Soil Preparation"), ('planting', "Planting"), ('monitoring', "Monitoring"),
         ('harvesting', "Harvesting"), ('processing', "Processing"), ('storage', "At Storage")], string=" Crop Phase")

    @api.constrains('start_date', 'expected_end_date', 'agriculture_season_id')
    def _check_task_dates(self):
        for record in self:
            # Check if expected_end_date is before start_date
            if record.expected_end_date < record.start_date:
                raise ValidationError(_("Please ensure the end date is greater than or equal to the start date"))
            # Ensure the dates are within the agriculture season period
            season = record.agriculture_season_id
            if season and season.start_date and season.end_date:
                if (record.start_date < season.start_date or
                        record.expected_end_date > season.end_date):
                    raise ValidationError(_(
                        "The agriculture season task time duration must be between "
                        "the start date and end date of the farming season"))

    def action_create_task(self):
        agriculture_task_id = self.env['project.task'].sudo().create({
            'name': self.title,
            'project_id': self.agriculture_season_id.agriculture_project_id.id,
            'farm_id': self.agriculture_season_id.farm_id.id,
            'crop_id': self.crop_id.id,
            'user_ids': self.user_id.ids,
            'date_assign': self.start_date,
            'date_deadline': self.expected_end_date,
            'crop_phase': self.crop_phase,
        })
        self.agriculture_task_id = agriculture_task_id.id
