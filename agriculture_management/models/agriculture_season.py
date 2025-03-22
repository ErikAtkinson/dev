# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AgricultureSeason(models.Model):
    """Agriculture Season"""
    _name = "agriculture.season"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'  # This remains, now valid with the new field

    name = fields.Char(string="Season Name", required=True)  # Added field
    image = fields.Binary(string="Image")
    farm_id = fields.Many2one('agriculture.farm', string="Farm", required=True)
    financial_year_id = fields.Many2one('agriculture.financial.year', string="Financial Year")
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    responsible = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user)
    agronomist_id = fields.Many2one('res.partner', string="Agronomist", domain=[('is_agronomist', '=', True)])
    status = fields.Selection([('draft', "Draft"), ('in_progress', "In Progress"), ('done', "Done")],
                              string="Status", default="draft")
    season_crop_ids = fields.One2many('season.crop', 'farm_season_id', string="Season Crop")
    crop_ids = fields.Many2many('agriculture.crop', string="Crops", compute="_compute_crop_ids")
    agriculture_project_id = fields.Many2one('project.project', string="Season Project")
    total_acre = fields.Float(string="Total Acre", compute="_compute_total_acre")
    season_budget_ids = fields.One2many('season.budget', 'farm_season_id', string="Season Budget")
    season_budget = fields.Monetary(string="Season Budget", compute="_compute_budget_price")
    labour_charge = fields.Monetary(string="Labour Charge", compute="_compute_budget_price")
    fertiliser_charge = fields.Monetary(string="Fertiliser Charge", compute="_compute_budget_price")
    pesticide_charge = fields.Monetary(string="Pesticide Charge", compute="_compute_budget_price")
    seed_charge = fields.Monetary(string="Seed Charge", compute="_compute_budget_price")
    equipment_charge = fields.Monetary(string="Equipment Charge", compute="_compute_budget_price")
    fleet_charge = fields.Monetary(string="Fleet Charge", compute="_compute_budget_price")
    electricity_expense = fields.Monetary(string="Electricity Expense", compute="_compute_budget_price")
    misc_expense = fields.Monetary(string="Miscellaneous Expense", compute="_compute_budget_price")
    total_cost = fields.Monetary(string="Total Cost", compute="_compute_budget_price")
    production_price = fields.Monetary(string="Production Price", compute="_compute_budget_price")
    total_product_income = fields.Monetary(string="Total Product Income", compute="_compute_budget_price")
    task_ids = fields.One2many('agriculture.task', 'farm_season_id', string="Tasks")
    crop_incident = fields.Integer(string="Crop Incident", compute="_compute_crop_incident")
    season_crop_incident_ids = fields.One2many('season.crop.incident', 'farm_season_id', string="Crop Incident")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    @api.depends('season_crop_ids')
    def _compute_crop_ids(self):
        for rec in self:
            rec.crop_ids = rec.season_crop_ids.mapped('crop_id')

    @api.depends('season_crop_ids')
    def _compute_total_acre(self):
        for rec in self:
            rec.total_acre = sum(rec.season_crop_ids.mapped('acre'))

    @api.depends('season_budget_ids', 'season_crop_ids')
    def _compute_budget_price(self):
        for rec in self:
            rec.season_budget = sum(rec.season_budget_ids.filtered(lambda x: x.budget_type == 'other').mapped('total_price'))
            rec.labour_charge = sum(rec.season_budget_ids.filtered(lambda x: x.budget_type == 'labour_cost_type').mapped('total_price'))
            rec.fertiliser_charge = sum(rec.season_budget_ids.filtered(lambda x: x.budget_type == 'fertiliser').mapped('total_price'))
            rec.pesticide_charge = sum(rec.season_budget_ids.filtered(lambda x: x.budget_type == 'pesticide').mapped('total_price'))
            rec.seed_charge = sum(rec.season_budget_ids.filtered(lambda x: x.budget_type == 'seed').mapped('total_price'))
            rec.equipment_charge = sum(rec.season_budget_ids.filtered(lambda x: x.budget_type == 'equipment').mapped('total_price'))
            rec.fleet_charge = sum(rec.season_budget_ids.filtered(lambda x: x.budget_type == 'fuel').mapped('total_price'))
            rec.electricity_expense = sum(rec.season_budget_ids.filtered(lambda x: x.budget_type == 'sallary').mapped('total_price'))
            rec.misc_expense = sum(rec.season_budget_ids.filtered(lambda x: x.budget_type == 'other').mapped('total_price'))
            rec.total_cost = rec.season_budget + rec.labour_charge + rec.fertiliser_charge + rec.pesticide_charge + rec.seed_charge + rec.equipment_charge + rec.fleet_charge + rec.electricity_expense + rec.misc_expense
            rec.production_price = sum(rec.season_crop_ids.mapped('production_price'))
            rec.total_product_income = sum(rec.season_crop_ids.mapped('total_product_income'))

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError("End date cannot be set before Start date.")

    @api.constrains('season_crop_ids', 'status')
    def _check_crop_ids(self):
        for record in self:
            if record.status == 'in_progress' and not record.season_crop_ids:
                raise ValidationError("Please add at least one crop in season before starting season!")

    def action_open_project(self):
        if not self.agriculture_project_id:
            project_id = self.env['project.project'].create({
                'name': self.name,
                'partner_id': self.farm_id.farmer_id.id,
            })
            self.agriculture_project_id = project_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Season Project',
            'view_mode': 'form',
            'res_model': 'project.project',
            'res_id': self.agriculture_project_id.id