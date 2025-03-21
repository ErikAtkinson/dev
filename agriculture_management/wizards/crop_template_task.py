# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import fields, api, models, _


class CropTemplateTask(models.TransientModel):
    """Crop Template Task"""
    _name = 'crop.template.task'
    _description = __doc__

    task_template_id = fields.Many2one('task.template', string="Template")
    crop_id = fields.Many2one("agriculture.crop", string="Crop")
    template_details_ids = fields.Many2many('template.details')
    reuse_template_details_ids = fields.Many2many('reuse.template.details')
    project_task_id = fields.Many2one('project.task', string="Task")
    season_crop_id = fields.Many2one('season.crop', string="Season Crop")
    agriculture_season_id = fields.Many2one('agriculture.season', string="Agriculture Season")

    @api.model
    def default_get(self, fields):
        res = super(CropTemplateTask, self).default_get(fields)
        rec = self._context.get('active_id')
        if rec:
            season_crop_id = self.env['season.crop'].browse(rec)
            if season_crop_id:
                res['season_crop_id'] = rec
                res['crop_id'] = season_crop_id.crop_id.id
                res['agriculture_season_id'] = season_crop_id.farm_season_id.id
        return res

    @api.constrains('reuse_template_details_ids', 'agriculture_season_id')
    def _check_date_deadline(self):
        for template_detail in self.reuse_template_details_ids:
            if self.agriculture_season_id and template_detail.date_deadline:
                season_start_date = self.agriculture_season_id.start_date
                season_end_date = self.agriculture_season_id.end_date
                if season_start_date and season_end_date and not (
                        season_start_date <= template_detail.date_deadline <= season_end_date):
                    raise ValidationError(_(
                        "The task deadline date must fall between the start date and end date of the season."
                    ))

    @api.onchange('task_template_id')
    def get_task_template_items(self):
        for rec in self:
            if not rec.task_template_id:
                return
            task_items = []
            for item in rec.task_template_id.template_details_ids:
                reuse_task = self.env['reuse.template.details'].sudo().create({
                    'crop_phase': item.crop_phase,
                    'task_title': item.task_title,
                    'task_description': item.task_description
                }).id
                task_items.append(reuse_task)
            rec.reuse_template_details_ids = [(5, 0, 0)]  # Clears the existing records
            rec.reuse_template_details_ids = [(6, 0, task_items)]  # Adds the new records

    def template_tasks_assign(self):
        for reuse in self.reuse_template_details_ids:
            if not reuse.assignees_ids:
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': "Please first select the task assignees, and then proceed.",
                        'sticky': False,
                    }
                }
                return message
            data = {
                'name': reuse.task_title,
                'project_id': self.agriculture_season_id.agriculture_project_id.id,
                'farm_season_id': self.agriculture_season_id.id,
                'farm_id': self.agriculture_season_id.farm_id.id,
                'crop_id': self.crop_id.id,
                'crop_phase': reuse.crop_phase,
                'description': reuse.task_description,
                'user_ids': [(6, 0, reuse.assignees_ids.ids)],
                'date_deadline': reuse.date_deadline,
            }
            self.env['project.task'].sudo().create(data)
        # Assuming you want to delete all records from the model 'reuse.template.details'
        reuse_template = self.env['reuse.template.details'].search([])
        reuse_template.unlink()
