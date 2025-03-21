# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class AgricultureDashboard(models.Model):
    """Agriculture Dashboard"""
    _name = "agriculture.dashboard"
    _description = __doc__

    @api.model
    def get_agriculture_dashboard(self):
        agriculture_farms = self.env['agriculture.farm'].search_count([])
        agriculture_farmer = self.env['res.partner'].search_count([('is_farmer', '=', True), ('company_id', 'in', self.env.user.company_ids.ids)])
        agriculture_season = self.env['agriculture.season'].search_count([])
        agriculture_crop = self.env['agriculture.crop'].search_count([])

        currency = self.env.company.currency_id.symbol
        agriculture_crop_production = self.env['crop.production'].search([]).mapped('total_production_price')
        total = 0
        for price in agriculture_crop_production:
            total = total + price
        total_str = str(total)

        season_crop_incident = self.env['season.crop.incident'].search_count([])

        season_start = self.env['agriculture.season'].search_count([('status', '=', 'draft')])
        season_in_progress = self.env['agriculture.season'].search_count([('status', '=', 'in_progress')])
        season_end = self.env['agriculture.season'].search_count([('status', '=', 'done')])
        season_status = [['Season Start', 'Season In Progress', 'Season End'],
                         [season_start, season_in_progress, season_end]]

        agriculture_agronomists = self.env['res.partner'].search_count([('is_agronomist', '=', True), 
                                                                               ('company_id', 'in', self.env.user.company_ids.ids)])
        agriculture_fleet = self.env['agriculture.fleet'].search_count([('company_id', 'in', self.env.user.company_ids.ids)])
        agriculture_equipment = self.env['agriculture.equipment'].search_count([('company_id', 'in', self.env.user.company_ids.ids)])
        agriculture_employee = self.env['hr.employee'].search_count([('company_id', 'in', self.env.user.company_ids.ids)])
        farm_animal = self.env['farm.animal'].search_count([])
        farm_worker = self.env['farm.worker'].search_count([])

        agriculture_resources = [['Agronomists', 'Agriculture Fleets', 'Agriculture Equipments', 'Employees',
                                  'Farm Animals', 'Farm Workers'],
                                 [agriculture_agronomists, agriculture_fleet, agriculture_equipment,
                                  agriculture_employee, farm_animal, farm_worker]]

        data = {
            'agriculture_farms': agriculture_farms,
            'agriculture_farmer': agriculture_farmer,
            'agriculture_season': agriculture_season,
            'agriculture_crop': agriculture_crop,
            'agriculture_crop_production': currency + ' ' + total_str,
            'season_crop_incident': season_crop_incident,
            'season_expense_report': self.get_season_expense_report(),
            'season_overall_info': self.get_season_overall_info(),
            'crop_incident_report': self.get_crop_incident_report(),
            'crop_season_duration': self.get_crop_season(),
            'season_status': season_status,
            'crop_stock': self.get_agriculture_crop_stocks(),
            'agriculture_resources': agriculture_resources,

            'agronomists': agriculture_agronomists,
            'fleets': agriculture_fleet,
            'equipments': agriculture_equipment,
            'employees': agriculture_employee,
            'animals': farm_animal,
            'workers': farm_worker,
        }
        return data

    def get_season_expense_report(self):
        name = []
        labour_charge = []
        fertiliser_charge = []
        pesticide_charge = []
        seed_charge = []
        equipment_charge = []
        fleet_charge = []
        electricity_expense = []
        data = []
        for group in self.env['agriculture.season'].read_group([], ['name', 'labour_charge', 'fertiliser_charge',
                                                                    'pesticide_charge', 'seed_charge',
                                                                    'equipment_charge', 'fleet_charge',
                                                                    'electricity_expense'], ['name']):
            if group['name']:
                name.append(group['name'])
                labour_charge.append(group['labour_charge'])
                fertiliser_charge.append(group['fertiliser_charge'])
                pesticide_charge.append(group['pesticide_charge'])
                seed_charge.append(group['seed_charge'])
                equipment_charge.append(group['equipment_charge'])
                fleet_charge.append(group['fleet_charge'])
                electricity_expense.append(group['electricity_expense'])

        data = [name, labour_charge, fertiliser_charge, pesticide_charge, seed_charge, equipment_charge, fleet_charge,
                electricity_expense]
        return data

    def get_season_overall_info(self):
        name, season_budget, misc_expense, production_price, total_product_income, season_data = [], [], [], [], [], []
        for group in self.env['agriculture.season'].read_group([], ['name', 'season_budget', 'misc_expense',
                                                                    'production_price', 'total_product_income'],
                                                               ['name']):
            if group['name']:
                name.append(group['name'])
                season_budget.append(group['season_budget'])
                misc_expense.append(group['misc_expense'])
                production_price.append(group['production_price'])
                total_product_income.append(group['total_product_income'])
        season_data = [name, season_budget, misc_expense, production_price, total_product_income]
        return season_data

    def get_crop_incident_report(self):
        name, crop_incident, incident_data = [], [], []
        for group in self.env['agriculture.season'].read_group([], ['name', 'crop_incident'], ['name']):
            if group['name']:
                name.append(group['name'])
                crop_incident.append(group['crop_incident'])
        incident_data = [name, crop_incident]
        return incident_data

    def get_crop_season(self):
        season_data = []
        seasons = self.env['agriculture.season'].search([])
        for season in seasons:
            season_data.append({
                'name': season.name,
                'start_date': str(season.start_date),
                'end_date': str(season.end_date),
            })
        return season_data

    def get_agriculture_crop_stocks(self):
        crop_qty, crops_name = [], []
        for group in self.env['crop.production'].read_group([], ['qty_on_hand'], ['crop_id']):
            agriculture_crop = self.env['agriculture.crop'].browse(int(group['crop_id'][0])).crop_name
            crop_quantity = group['qty_on_hand']
            crops_name.append(agriculture_crop)
            crop_qty.append(crop_quantity)
        data = {
            'crop_quantity': crop_qty,
            'crops_name': crops_name,
        }
        return data
