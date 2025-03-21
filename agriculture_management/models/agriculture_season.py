# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import date
import xlwt
import base64
from io import BytesIO

from odoo.exceptions import ValidationError
from odoo import fields, api, models, _


class AgricultureSeason(models.Model):
    """Agriculture Seasons"""
    _name = "agriculture.season"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    start_date = fields.Date(string=" Start Date")
    end_date = fields.Date(string="End Date")
    avatar = fields.Binary(string="Image")
    farm_id = fields.Many2one("agriculture.farm", string="Farm")
    crop_ids = fields.Many2many("agriculture.crop", string="Crops")
    farmer_id = fields.Many2one(string="Farmer", related='farm_id.farmer_id', store=True)
    agronomist_id = fields.Many2one('res.partner', string="Agronomist", domain=[('is_agronomist', '=', True)])
    field_manager_id = fields.Many2one('res.partner', string="Field Manager", domain=[('is_field_manager', '=', True)])
    financial_year_id = fields.Many2one("agriculture.financial.year", string="Financial Year")

    season_crop_ids = fields.One2many("season.crop", "farm_season_id", string="Season Crops")
    farm_labour_ids = fields.One2many("farm.labour", "farm_season_id", string="Farm Labours")
    crop_disease_ids = fields.One2many("farm.crop.disease", "farm_season_id", string="Crop Diseases")
    field_visit_ids = fields.One2many("field.visit", "farm_season_id", string="Field Visits")
    crop_pesticide_ids = fields.One2many("farm.crop.pesticides", "farm_season_id", string="Crop Pesticides")
    crop_seed_ids = fields.One2many("farm.crop.seed", "farm_season_id", string="Crop Seeds")
    crop_fertiliser_ids = fields.One2many("farm.crop.fertiliser", "farm_season_id", string="Crop Fertilisers")
    equipment_use_ids = fields.One2many("farm.equipment.uses", "farm_season_id", string="Uses of Equipments")
    crop_production_ids = fields.One2many("crop.production", "farm_season_id", string="Crop Productions")
    misc_expense_ids = fields.One2many("misc.expense", "farm_season_id", string="Misc Expenses")
    crop_incident_ids = fields.One2many("season.crop.incident", "farm_season_id", string="Crop Incident")
    electricity_expense_ids = fields.One2many("electricity.expense", "farm_season_id", string="Electricity Expenses")
    agriculture_warehouse_id = fields.Many2one("agriculture.warehouse")
    season_fleet_ids = fields.One2many("season.fleet", "farm_season_id", string="Season Fleet")
    season_budget_ids = fields.One2many("season.budget", "farm_season_id", string="Season Budget")

    labour_charge = fields.Monetary(string="Labour Expenses", compute="_compute_labour_charge", store=True)
    pesticide_charge = fields.Monetary(string="Pesticide Expenses", compute="_compute_pesticide_charge", store=True)
    seed_charge = fields.Monetary(string="Seed Expenses", compute="_compute_seed_charge", store=True)
    fertiliser_charge = fields.Monetary(string="Fertiliser Expenses", compute="_compute_fertiliser_charge", store=True)
    equipment_charge = fields.Monetary(string="Equipment Expenses", compute="_compute_equipment_charge", store=True)
    fleet_charge = fields.Monetary(string="Fleet Expenses", compute="_compute_fleet_charge", store=True)
    misc_expense = fields.Monetary(string="Misc Expense", compute="_compute_season_misc_expense", store=True)
    crop_incident = fields.Monetary(string="Crop Incidents", compute="_compute_crop_incident", store=True)
    electricity_expense = fields.Monetary(string="Electricity Expense", compute="_compute_electricity_expense",
                                          store=True)
    total_cost = fields.Monetary(string="Total Expenses", compute="_compute_total_costing", store=True)

    production_price = fields.Monetary(string="Production Income", compute="_compute_production_price", store=True)
    season_budget = fields.Monetary(string="Season Budget ", compute="_compute_season_budget", store=True)
    total_product_income = fields.Monetary(string="Profit & Loss", compute="_product_income", store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    agriculture_project_id = fields.Many2one('project.project', readonly=True, string="Season Project")
    agriculture_task_count = fields.Integer(compute='_get_season_tasks')
    agriculture_task_ids = fields.One2many('agriculture.task', 'agriculture_season_id', string="Project Task")

    responsible = fields.Many2one('res.users', default=lambda self: self.env.user, string="Responsible")

    season_bill_count = fields.Integer(compute='_get_season_bills')
    season_bill_id = fields.Many2one('account.move', string="Season Bill")

    status = fields.Selection([('draft', 'Season Start'), ('in_progress', 'Season in Progress'),
                               ('done', 'Season End')], default="draft", group_expand='_expand_groups')

    delivery_order_count = fields.Integer(compute="_get_delivery_order_count")

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'in_progress', 'done']

    def _check_season_crops(self):
        for record in self:
            # Check that the number of season crops is at least the number of crops
            if len(record.season_crop_ids) < len(record.crop_ids):
                raise ValidationError(_(f"You need to add at least {len(record.crop_ids)} Season Crops."))
            # Check for duplicate crops in the same season
            crop_ids_in_season = [crop.crop_id.id for crop in record.season_crop_ids]
            if len(crop_ids_in_season) != len(set(crop_ids_in_season)):
                raise ValidationError(_("A same crop cannot be added more than once in the same season."))

    def draft_to_in_progress(self):
        self._check_season_crops()
        self.status = 'in_progress'

    def in_progress_to_season_end(self):
        self._check_season_crops()
        if any(task.status != 'c_complete' for task in self.agriculture_task_ids):
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': "Kindly complete the pending agriculture tasks",
                    'sticky': False,
                }
            }
            return message
        self.status = 'done'

    @api.constrains('start_date', 'end_date')
    def _check_season_period(self):
        for record in self:
            if record.end_date <= record.start_date:
                raise ValidationError(_("Please ensure the season end date is greater than the start date"))

    @api.constrains('crop_ids')
    def _check_season_crop_records(self):
        for record in self:
            if record.crop_ids:
                # Get the related crops from season crop records
                related_crops = record.season_crop_ids.mapped('crop_id')
                # Check if any of the crop_ids are being removed that are in the related crops
                removed_crops = set(related_crops.ids) - set(record.crop_ids.ids)
                if removed_crops:
                    raise ValidationError(
                        _("You cannot remove the selected crop(s) because there are related season crops records. "
                          "First delete the season crop record, then try removing the crop_ids again."))

    def _get_season_tasks(self):
        for rec in self:
            task_counts = 0
            if rec.id:
                task_counts = self.env['project.task'].sudo().search_count([('farm_season_id', '=', rec.id)])
            rec.agriculture_task_count = task_counts

    def view_season_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'view_mode': 'kanban,tree,form',
            'res_model': "project.task",
            'domain': [('farm_season_id', '=', self.id)],
            'context': {
                'default_project_id': self.agriculture_project_id.id,
                'default_partner_id': self.farmer_id.id,
                'crop_ids': self.crop_ids.ids,
                'default_farm_id': self.farm_id.id,
                'search_default_crop_phase': True,
                'create': False
            }
        }

    def _get_season_bills(self):
        for rec in self:
            bill_count = 0
            if rec.id:
                bill_count = self.env['account.move'].sudo().search_count([('agriculture_season_id', '=', rec.id)])
            rec.season_bill_count = bill_count

    def view_season_bills(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Season Bills'),
            'view_mode': 'tree,form',
            'res_model': "account.move",
            'domain': [('agriculture_season_id', '=', self.id)],
            'context': {
                'default_agriculture_season_id': self.id,
                'create': False
            }
        }

    def _get_delivery_order_count(self):
        for rec in self:
            delivery_order_count = self.env['stock.picking'].search_count([('agriculture_season_id', '=', rec.id)])
            rec.delivery_order_count = delivery_order_count

    def view_delivery_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Orders'),
            'view_mode': 'kanban,tree,form',
            'res_model': "stock.picking",
            'domain': [('agriculture_season_id', '=', self.id)],
            'context': {
                'create': False,
            }
        }

    def get_season_labours(self):
        context = {
            'default_farm_season_id': self.id,
            'crop_ids': self.crop_ids.ids,
        }
        if self.status == 'done':
            context['create'] = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Labours'),
            'view_mode': 'tree,form',
            'res_model': "farm.labour",
            'domain': [('farm_season_id', '=', self.id)],
            'context': context,
        }

    def get_season_crop_fertilisers(self):
        context = {
            'default_farm_season_id': self.id,
            'crop_ids': self.crop_ids.ids,
        }
        if self.status == 'done':
            context['create'] = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Fertilisers'),
            'view_mode': 'tree,form',
            'res_model': "farm.crop.fertiliser",
            'domain': [('farm_season_id', '=', self.id)],
            'context': context,
        }

    def get_season_crop_pesticides(self):
        context = {
            'default_farm_season_id': self.id,
            'crop_ids': self.crop_ids.ids,
        }
        if self.status == 'done':
            context['create'] = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pesticides'),
            'view_mode': 'tree,form',
            'res_model': "farm.crop.pesticides",
            'domain': [('farm_season_id', '=', self.id)],
            'context': context,
        }

    def get_crop_seed(self):
        context = {
            'default_farm_season_id': self.id,
            'crop_ids': self.crop_ids.ids,
        }
        if self.status == 'done':
            context['create'] = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Seeds'),
            'view_mode': 'tree,form',
            'res_model': "farm.crop.seed",
            'domain': [('farm_season_id', '=', self.id)],
            'context': context,
        }

    def get_season_equipment_uses(self):
        context = {
            'default_farm_season_id': self.id,
            'crop_ids': self.crop_ids.ids,
        }
        if self.status == 'done':
            context['create'] = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Equipments'),
            'view_mode': 'tree,form',
            'res_model': "farm.equipment.uses",
            'domain': [('farm_season_id', '=', self.id)],
            'context': context,
        }

    def get_season_fleet_uses(self):
        context = {
            'default_farm_season_id': self.id,
            'crop_ids': self.crop_ids.ids,
        }
        if self.status == 'done':
            context['create'] = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Fleet'),
            'view_mode': 'tree,form',
            'res_model': "season.fleet",
            'domain': [('farm_season_id', '=', self.id)],
            'context': context,
        }

    def get_season_electricity_expanse(self):
        context = {
            'default_farm_season_id': self.id,
        }
        if self.status == 'done':
            context['create'] = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Electricity Expense'),
            'view_mode': 'tree,form',
            'res_model': "electricity.expense",
            'domain': [('farm_season_id', '=', self.id)],
            'context': context,
        }

    def get_season_misc_expanse(self):
        context = {
            'default_farm_season_id': self.id,
            'crop_ids': self.crop_ids.ids,
        }
        if self.status == 'done':
            context['create'] = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Misc Expanses'),
            'view_mode': 'tree,form',
            'res_model': "misc.expense",
            'domain': [('farm_season_id', '=', self.id)],
            'context': context,
        }

    def action_create_all_task(self):
        for rec in self.agriculture_task_ids:
            if not rec.agriculture_task_id:
                rec.action_create_task()

    @api.depends('farm_labour_ids.total_labour_cost')
    def _compute_labour_charge(self):
        for rec in self:
            rec.labour_charge = sum(p.total_labour_cost for p in rec.farm_labour_ids)

    @api.depends('crop_pesticide_ids.total_price')
    def _compute_pesticide_charge(self):
        for rec in self:
            rec.pesticide_charge = sum(p.total_price for p in rec.crop_pesticide_ids)

    @api.depends('crop_seed_ids.total_seed_price')
    def _compute_seed_charge(self):
        for rec in self:
            rec.seed_charge = sum(p.total_seed_price for p in rec.crop_seed_ids)

    @api.depends('crop_fertiliser_ids.total_fertiliser_price')
    def _compute_fertiliser_charge(self):
        for rec in self:
            rec.fertiliser_charge = sum(p.total_fertiliser_price for p in rec.crop_fertiliser_ids)

    @api.depends('equipment_use_ids.total')
    def _compute_equipment_charge(self):
        for rec in self:
            rec.equipment_charge = sum(p.total for p in rec.equipment_use_ids)

    @api.depends('season_fleet_ids.total_price')
    def _compute_fleet_charge(self):
        for rec in self:
            rec.fleet_charge = sum(p.total_price for p in rec.season_fleet_ids)

    @api.depends('misc_expense_ids.standard_price')
    def _compute_season_misc_expense(self):
        for rec in self:
            rec.misc_expense = sum(p.standard_price for p in rec.misc_expense_ids)

    @api.depends('electricity_expense_ids.standard_price')
    def _compute_electricity_expense(self):
        for rec in self:
            rec.electricity_expense = sum(p.standard_price for p in rec.electricity_expense_ids)

    @api.depends('crop_incident_ids.value')
    def _compute_crop_incident(self):
        for rec in self:
            rec.crop_incident = sum(p.value for p in rec.crop_incident_ids)

    @api.depends('season_budget_ids.total_price')
    def _compute_season_budget(self):
        for rec in self:
            rec.season_budget = sum(p.total_price for p in rec.season_budget_ids)

    @api.depends('crop_pesticide_ids', 'crop_fertiliser_ids', 'equipment_use_ids', 'farm_labour_ids',
                 'misc_expense_ids', 'season_fleet_ids', 'crop_seed_ids', 'electricity_expense_ids',
                 'crop_incident_ids')
    def _compute_total_costing(self):
        for cost in self:
            cost.total_cost = (cost.pesticide_charge + cost.fertiliser_charge + cost.equipment_charge +
                               cost.labour_charge + cost.misc_expense + cost.fleet_charge +
                               cost.seed_charge + cost.electricity_expense + cost.crop_incident)

    @api.depends('crop_production_ids.total_production_price')
    def _compute_production_price(self):
        for rec in self:
            rec.production_price = sum(p.total_production_price for p in rec.crop_production_ids)

    @api.depends('production_price', 'total_cost')
    def _product_income(self):
        for income in self:
            income.total_product_income = income.production_price - income.total_cost

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AgricultureSeason, self).create(vals_list)
        for rec in res:
            data = {
                'name': res.name,
                'user_id': self.env.user.id,
                'company_id': self.env.company.id,
                'date_start': res.start_date,
                'date': res.end_date,
                'farm_season_id': res.id,
            }
            agriculture_project_id = self.env['project.project'].create(data)
            rec.agriculture_project_id = agriculture_project_id.id
        return res

    def write(self, vals_list):
        rec = super(AgricultureSeason, self).write(vals_list)
        self.agriculture_project_id.write({
            'name': self.name,
        })
        return rec

    # XLS Report
    def print_excel(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet1 = workbook.add_sheet('Season', cell_overwrite_ok=True)
        format1 = xlwt.easyxf('align:horiz center, vert center;font: color black;')
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/mm/yy'
        format2 = xlwt.easyxf('align:horiz center, vert center;font: color black,bold True, height 250;')
        format3 = xlwt.easyxf('align:horiz center, vert center;font: color black,bold True, height 180;')
        format4 = xlwt.easyxf('font: color black,bold True, height 220;')
        format5 = xlwt.easyxf('font: color black, height 220;')

        crops = []
        for rec in self.crop_ids:
            crops.append(rec.crop_name)
        crops = ",".join(crops)

        sheet1.col(0).width = 4000
        sheet1.col(1).width = 8000
        sheet1.col(2).width = 4000
        sheet1.col(3).width = 3000
        sheet1.col(4).width = 5000
        sheet1.col(5).width = 700
        sheet1.col(6).width = 4800
        sheet1.col(7).width = 4500
        sheet1.col(8).width = 3000
        sheet1.col(9).width = 3000
        sheet1.col(10).width = 700
        sheet1.col(11).width = 4000
        sheet1.col(12).width = 3000
        sheet1.col(13).width = 700
        sheet1.col(14).width = 3000
        sheet1.col(15).width = 8000
        sheet1.col(16).width = 5000
        sheet1.col(17).width = 2500
        sheet1.col(18).width = 3000
        sheet1.col(19).width = 2500
        sheet1.col(20).width = 2500
        sheet1.col(21).width = 2500
        sheet1.col(22).width = 700
        sheet1.col(23).width = 4500
        sheet1.col(24).width = 2500
        sheet1.col(25).width = 2500
        sheet1.col(26).width = 3000
        sheet1.col(27).width = 3500

        sheet1.write_merge(0, 0, 0, 4, 'Farming Season', format2)
        sheet1.row(0).height = 700
        sheet1.write(2, 0, "Season Name", format4)
        sheet1.write(3, 0, "Financial Year", format4)
        sheet1.write(4, 0, "Farm Name", format4)
        sheet1.write(5, 0, "Farmer Name", format4)
        sheet1.write(6, 0, "Start Date", format4)
        sheet1.write(7, 0, "End Date", format4)
        sheet1.write(8, 0, "Responsible", format4)
        sheet1.write(9, 0, "Crops", format4)

        sheet1.write(2, 1, self.name, format5)
        sheet1.write(3, 1, self.financial_year_id.title, format5)
        sheet1.write(4, 1, self.farm_id.farm_name, format5)
        sheet1.write(5, 1, self.farmer_id.name, format5)
        sheet1.write(6, 1, self.start_date, date_format)
        sheet1.write(7, 1, self.end_date, date_format)
        sheet1.write(8, 1, self.responsible.name, format5)
        sheet1.write(9, 1, crops, format5)

        sheet1.write_merge(15, 15, 0, 4, "Season Crops", format2)
        sheet1.row(15).height = 500
        sheet1.write(16, 0, "Crop", format3)
        sheet1.write(16, 1, "Plantation Area", format3)
        sheet1.write(16, 2, "Land Measure", format3)
        sheet1.write(16, 3, "Planting Date", format3)
        sheet1.write(16, 4, "Status", format3)

        row = 17
        for rec in self.season_crop_ids:
            sheet1.write(row, 0, rec.crop_id.crop_name, format1)
            sheet1.write(row, 1, rec.plantation_area, format1)
            sheet1.write(row, 2, rec.land_measure, format1)
            sheet1.write(row, 3, rec.plantation_date, date_format)
            sheet1.write(row, 4, rec.status, format1)
            row += 1

        sheet1.write_merge(15, 15, 6, 9, "Crops Diseases", format2)
        sheet1.write(16, 6, "Crop Disease", format3)
        sheet1.write(16, 7, "Expect Damage(%)", format3)
        sheet1.write(16, 8, "Start Date", format3)
        sheet1.write(16, 9, "End Date", format3)

        row = 17
        for rec in self.crop_disease_ids:
            sheet1.write(row, 6, rec.crop_disease_id.name, format1)
            sheet1.write(row, 7, rec.expect_damage, format1)
            sheet1.write(row, 8, rec.start_date, date_format)
            sheet1.write(row, 9, rec.end_date, date_format)
            row += 1

        sheet1.write_merge(15, 15, 11, 12, "Misc Expense", format2)
        sheet1.write(16, 11, "Expense Type", format3)
        sheet1.write(16, 12, "Expense", format3)

        row = 17
        for rec in self.misc_expense_ids:
            sheet1.write(row, 11, rec.title, format1)
            sheet1.write(row, 12, rec.expense, format1)
            row += 1

        sheet1.write_merge(15, 15, 14, 21, "Crop Production", format2)
        sheet1.write(16, 14, "Crop", format3)
        sheet1.write(16, 15, "Description", format3)
        sheet1.write(16, 16, "Warehouse", format3)
        sheet1.write(16, 17, "Qty", format3)
        sheet1.write(16, 18, "Qty on Hand", format3)
        sheet1.write(16, 19, "Unit", format3)
        sheet1.write(16, 20, "Price(₹)", format3)
        sheet1.write(16, 21, "Total(₹)", format3)

        row = 17
        for rec in self.crop_production_ids:
            sheet1.write(row, 14, rec.crop_id.crop_name, format1)
            sheet1.write(row, 15, rec.description, format1)
            sheet1.write(row, 16, rec.agriculture_warehouse_id.name, format1)
            sheet1.write(row, 17, rec.qty, format1)
            sheet1.write(row, 18, rec.qty_on_hand, format1)
            sheet1.write(row, 19, rec.unit_id.name, format1)
            sheet1.write(row, 20, rec.price, format1)
            sheet1.write(row, 21, rec.total_production_price, format1)
            row += 1

        sheet1.write_merge(15, 15, 23, 27, "Season Budget", format2)
        sheet1.write(16, 23, "Budget Type", format3)
        sheet1.write(16, 24, "Qty", format3)
        sheet1.write(16, 25, "Unit", format3)
        sheet1.write(16, 26, "Price", format3)
        sheet1.write(16, 27, "Total price", format3)

        row = 17
        for rec in self.season_budget_ids:
            sheet1.write(row, 23, rec.budget_type, format1)
            sheet1.write(row, 24, rec.qty, format1)
            sheet1.write(row, 25, rec.unit_id.name, format1)
            sheet1.write(row, 26, rec.price, format1)
            sheet1.write(row, 27, rec.total_price, format1)
            row += 1

        sheet1.write_merge(0, 0, 6, 7, 'Estimation Cost', format2)
        sheet1.write(1, 6, "Production Income", format5)
        sheet1.write(2, 6, "Profit & Loss", format5)

        sheet1.write(1, 7, self.production_price, format5)
        sheet1.write(2, 7, self.total_product_income, format5)

        sheet1.write(3, 6, "Labour Charge", format5)
        sheet1.write(4, 6, "Pesticide Charge", format5)
        sheet1.write(5, 6, "Fertiliser Charge", format5)
        sheet1.write(6, 6, "Seed Charge", format5)
        sheet1.write(7, 6, "Equipment Charge", format5)
        sheet1.write(8, 6, "Fleet Charge", format5)
        sheet1.write(9, 6, "Misc Expense", format5)
        sheet1.write(10, 6, "Crop Incident", format5)
        sheet1.write(11, 6, "Electricity Expense", format5)
        sheet1.write(12, 6, "Total Cost", format5)

        sheet1.write(3, 7, self.labour_charge, format5)
        sheet1.write(4, 7, self.pesticide_charge, format5)
        sheet1.write(5, 7, self.fertiliser_charge, format5)
        sheet1.write(6, 7, self.seed_charge, format5)
        sheet1.write(7, 7, self.equipment_charge, format5)
        sheet1.write(8, 7, self.fleet_charge, format5)
        sheet1.write(9, 7, self.misc_expense, format5)
        sheet1.write(10, 7, self.crop_incident, format5)
        sheet1.write(11, 7, self.electricity_expense, format5)
        sheet1.write(12, 7, self.total_cost, format5)

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())

        attachment = self.env['ir.attachment'].sudo()
        filename = self.name + '.xls'
        attachment_id = attachment.create(
            {'name': filename,
             'type': 'binary',
             'public': False,
             'datas': out,
             })
        if attachment_id:
            report = {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment_id.id),
                'target': self,
                'nodestroy': False,
            }
            return report


class AgricultureProject(models.Model):
    """Agriculture Project"""
    _inherit = 'project.project'
    _description = __doc__

    farm_season_id = fields.Many2one('agriculture.season', string="Farm Season", ondelete='cascade')


class AgricultureProjectTask(models.Model):
    """Agriculture Project Task"""
    _inherit = 'project.task'
    _description = __doc__

    farm_season_id = fields.Many2one(related='project_id.farm_season_id', string="Farm Season", store=True)


class SeasonCrop(models.Model):
    """Crops by Season"""
    _name = "season.crop"
    _description = __doc__
    _rec_name = 'crop_id'

    plantation_area = fields.Float(string="Plantation Area")
    land_measure = fields.Selection([('sq_mt', "Square Meter"), ('acre', "Acre"), ('hectare', "Hectare"),
                                     ('bigha', "Bigha")], string="Land Measure Unit", default="acre")
    plantation_date = fields.Date(string="Start Date")
    expect_end_date = fields.Date(string="Expected End Date")
    status = fields.Selection([('plan', "Crop Planning"), ('purchase', "Purchase of Crop Inputs"),
                               ('soil_prepare', "Soil Preparation"), ('plant', "Planting"),
                               ('monitor', "Monitoring"), ('harvest', "Harvesting"), ('process', "Processing"),
                               ('storage', "At Storage")], string="Life Cycle")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    season_status = fields.Selection(related="farm_season_id.status", string="Status")
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", required=True, domain="[('id', 'in', crop_ids)]")

    plan_date = fields.Date()
    crop_input_date = fields.Date()
    soil_prepare_date = fields.Date()
    plant_date = fields.Date()
    monitor_date = fields.Date()
    harvest_date = fields.Date()
    process_date = fields.Date()
    storage_date = fields.Date()

    is_plan_done = fields.Boolean()
    is_crop_input_done = fields.Boolean()
    is_soil_prepare_done = fields.Boolean()
    is_plant_done = fields.Boolean()
    is_monitor_done = fields.Boolean()
    is_harvest_done = fields.Boolean()
    is_process_done = fields.Boolean()
    is_storage_done = fields.Boolean()

    labour_expense = fields.Monetary(string="Labour Expense", compute="_compute_labour_expense")
    fertiliser_expense = fields.Monetary(string="Fertiliser Expense", compute="_compute_fertiliser_expense")
    pesticide_expense = fields.Monetary(string="Pesticide Expense", compute="_compute_pesticide_expense")
    seed_expense = fields.Monetary(string="Seed Expense", compute="_compute_seed_expense")
    equipment_expense = fields.Monetary(string="Equipment Expense", compute="_compute_equipment_expense")
    fleet_expense = fields.Monetary(string="Fleet Expense", compute="_compute_fleet_expense")
    misc_expense = fields.Monetary(string="Misc Expense", compute="_compute_misc_expense")
    season_task = fields.Integer(string="Season Task", compute="_compute_season_task")
    crop_disease = fields.Integer(string="Crop Disease", compute="_compute_crop_disease_count")
    crop_production = fields.Integer(string="Crop Production", compute="_compute_crop_production_count")

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    @api.constrains('plantation_date', 'expect_end_date', 'farm_season_id')
    def _check_crop_planting_dates(self):
        for record in self:
            if record.plantation_date and record.expect_end_date:
                # Check if end date is greater than start date
                if record.expect_end_date < record.plantation_date:
                    raise ValidationError(_("Please ensure the expected end date is greater than the plantation date"))
                # Check if dates are within the farm season period
                if record.farm_season_id:
                    planting_start = record.farm_season_id.start_date
                    planting_end = record.farm_season_id.end_date
                    if planting_start and planting_end:
                        if (record.plantation_date < planting_start or
                                record.expect_end_date > planting_end):
                            raise ValidationError(_(
                                "The crop planting duration must be between the start date and end date of the"
                                "farming season"))

    @api.depends('farm_season_id', 'crop_id')
    def _compute_labour_expense(self):
        for rec in self:
            if rec.crop_id and rec.farm_season_id:
                # Search for labour expenses related to the crop and farm season
                labour_expense = self.env['farm.labour'].sudo().search([
                    ('crop_id', '=', rec.crop_id.id),
                    ('farm_season_id', '=', rec.farm_season_id.id)
                ]).mapped('total_labour_cost')
                # Calculate the total labour expense
                rec.labour_expense = sum(labour_expense)
            else:
                # Set to 0 if either crop_id or farm_season_id is missing
                rec.labour_expense = 0

    @api.depends('farm_season_id', 'crop_id')
    def _compute_fertiliser_expense(self):
        for rec in self:
            if rec.crop_id and rec.farm_season_id:
                # Search for fertiliser expenses related to the crop and farm season
                fertiliser_expense_list = self.env['farm.crop.fertiliser'].sudo().search(
                    [('crop_id', '=', rec.crop_id.id), ('farm_season_id', '=', rec.farm_season_id.id)]
                ).mapped('total_fertiliser_price')
                # Calculate the total fertiliser expense
                rec.fertiliser_expense = sum(fertiliser_expense_list)
            else:
                # Set to 0 if either crop_id or farm_season_id is missing
                rec.fertiliser_expense = 0

    @api.depends('farm_season_id', 'crop_id')
    def _compute_pesticide_expense(self):
        for rec in self:
            if rec.crop_id and rec.farm_season_id:
                # Search for pesticide expenses related to the crop and farm season
                pesticide_expense_list = self.env['farm.crop.pesticides'].sudo().search(
                    [('crop_id', '=', rec.crop_id.id), ('farm_season_id', '=', rec.farm_season_id.id)]
                ).mapped('total_price')
                # Calculate the total pesticide expense
                rec.pesticide_expense = sum(pesticide_expense_list)
            else:
                # Set to 0 if either crop_id or farm_season_id is missing
                rec.pesticide_expense = 0

    @api.depends('farm_season_id', 'crop_id')
    def _compute_seed_expense(self):
        for rec in self:
            if rec.crop_id and rec.farm_season_id:
                # Search for seed expenses related to the crop and farm season
                seed_expense = self.env['farm.crop.seed'].sudo().search(
                    [('crop_id', '=', rec.crop_id.id), ('farm_season_id', '=', rec.farm_season_id.id)]
                ).mapped('total_seed_price')
                # Calculate the total seed expense
                rec.seed_expense = sum(seed_expense)
            else:
                # Set to 0 if either crop_id or farm_season_id is missing
                rec.seed_expense = 0

    @api.depends('farm_season_id', 'crop_id')
    def _compute_equipment_expense(self):
        for rec in self:
            if rec.crop_id and rec.farm_season_id:
                # Search for equipment expenses related to the crop and farm season
                equipment_expense = self.env['farm.equipment.uses'].search(
                    [('crop_id', '=', rec.crop_id.id), ('farm_season_id', '=', rec.farm_season_id.id)]
                ).mapped('total')
                # Calculate the total equipment expense
                rec.equipment_expense = sum(equipment_expense)
            else:
                # Set to 0 if either crop_id or farm_season_id is missing
                rec.equipment_expense = 0

    @api.depends('farm_season_id', 'crop_id')
    def _compute_fleet_expense(self):
        for rec in self:
            if rec.crop_id and rec.farm_season_id:
                # Search for fleet expenses related to the crop and farm season
                fleet_expense = self.env['season.fleet'].sudo().search([
                    ('crop_id', '=', rec.crop_id.id),
                    ('farm_season_id', '=', rec.farm_season_id.id)
                ]).mapped('total_price')
                # Calculate the total fleet expense
                rec.fleet_expense = sum(fleet_expense)
            else:
                # Set to 0 if either crop_id or farm_season_id is missing
                rec.fleet_expense = 0

    @api.depends('farm_season_id', 'crop_id')
    def _compute_misc_expense(self):
        for rec in self:
            if rec.crop_id and rec.farm_season_id:
                # Search for misc expenses related to the crop and farm season
                misc_expense = self.env['misc.expense'].sudo().search([
                    ('crop_id', '=', rec.crop_id.id),
                    ('farm_season_id', '=', rec.farm_season_id.id)
                ]).mapped('standard_price')
                # Calculate the misc fleet expense
                rec.misc_expense = sum(misc_expense)
            else:
                # Set to 0 if either crop_id or farm_season_id is missing
                rec.misc_expense = 0

    def _compute_season_task(self):
        for rec in self:
            season_task_list = 0
            if rec.farm_season_id:
                season_task_list = self.env['project.task'].sudo().search_count(
                    [('crop_id', '=', rec.crop_id.id), ('farm_season_id', '=', rec.farm_season_id.id)])
            rec.season_task = season_task_list

    def view_season_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'view_mode': 'kanban,tree,form',
            'res_model': "project.task",
            'domain': [('farm_season_id', '=', self.farm_season_id.id), ('crop_id', '=', self.crop_id.id)],
            'context': {
                'default_project_id': self.farm_season_id.agriculture_project_id.id,
                'default_partner_id': self.farm_season_id.farmer_id.id,
                'default_crop_id': self.crop_id.id,
                'default_farm_id': self.farm_season_id.farm_id.id,
                'search_default_crop_phase': True,
                'create': False
            }
        }

    def action_farm_crop_disease(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Crop Diseases'),
            'view_mode': 'form',
            'res_model': 'farm.crop.disease',
            'domain': [('farm_season_id', '=', self.id)],
            'context': {
                'default_farm_season_id': self.farm_season_id.id,
                'default_crop_id': self.crop_id.id,
            }
        }

    def _compute_crop_disease_count(self):
        for rec in self:
            crop_disease = 0
            if rec.farm_season_id:
                crop_disease = self.env['farm.crop.disease'].sudo().search_count(
                    [('crop_id', '=', rec.crop_id.id), ('farm_season_id', '=', rec.farm_season_id.id)])
            rec.crop_disease = crop_disease

    def view_season_crop_disease(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Crop Diseases'),
            'view_mode': 'tree,form',
            'res_model': "farm.crop.disease",
            'domain': [('farm_season_id', '=', self.farm_season_id.id), ('crop_id', '=', self.crop_id.id)],
            'context': {
                'default_crop_id': self.crop_id.id,
                'default_farm_season_id': self.farm_season_id.id,
                'create': False
            }
        }

    def action_add_season_crop_production(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Crop Production'),
            'view_mode': 'form',
            'res_model': 'crop.production',
            'domain': [('farm_season_id', '=', self.id)],
            'context': {
                'default_farm_season_id': self.farm_season_id.id,
                'default_crop_id': self.crop_id.id,
            }
        }

    def _compute_crop_production_count(self):
        for rec in self:
            crop_production = 0
            if rec.farm_season_id:
                crop_production = self.env['crop.production'].sudo().search_count(
                    [('crop_id', '=', rec.crop_id.id), ('farm_season_id', '=', rec.farm_season_id.id)])
            rec.crop_production = crop_production

    def view_crop_production(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Crop Productions'),
            'view_mode': 'tree,form',
            'res_model': "crop.production",
            'domain': [('farm_season_id', '=', self.farm_season_id.id), ('crop_id', '=', self.crop_id.id)],
            'context': {
                'default_crop_id': self.crop_id.id,
                'default_farm_season_id': self.farm_season_id.id,
                'create': False
            }
        }

    def crop_plan(self):
        for rec in self:
            rec.status = 'plan'
            rec.plan_date = date.today()
            rec.is_plan_done = True

    def crop_input_stage(self):
        for rec in self:
            rec.status = 'purchase'
            rec.crop_input_date = date.today()
            rec.is_crop_input_done = True

    def soil_prepare_stage(self):
        for rec in self:
            rec.status = 'soil_prepare'
            rec.soil_prepare_date = date.today()
            rec.is_soil_prepare_done = True

    def crop_plant_stage(self):
        for rec in self:
            rec.status = 'plant'
            rec.plant_date = date.today()
            rec.is_plant_done = True

    def monitor_stage(self):
        for rec in self:
            rec.status = 'monitor'
            rec.monitor_date = date.today()
            rec.is_monitor_done = True

    def harvest_stage(self):
        for rec in self:
            rec.status = 'harvest'
            rec.harvest_date = date.today()
            rec.is_harvest_done = True

    def process_stage(self):
        for rec in self:
            rec.status = 'process'
            rec.process_date = date.today()
            rec.is_process_done = True

    def storage_stage(self):
        for rec in self:
            rec.status = 'storage'
            rec.storage_date = date.today()
            rec.is_storage_done = True

    def action_season_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Season Tasks'),
            'view_mode': 'form',
            'res_model': "project.task",
            'domain': [('farm_season_id', '=', self.id)],
            'context': {
                'default_project_id': self.farm_season_id.agriculture_project_id.id,
                'default_crop_id': self.crop_id.id,
                'default_farm_id': self.farm_season_id.farm_id.id,
                'search_default_crop_phase': True,
            }
        }


class FarmLabour(models.Model):
    """Season Work Details of workers"""
    _name = "farm.labour"
    _description = __doc__
    _rec_name = 'worker_id'

    worker_id = fields.Many2one('farm.worker', string="Name", required=True)
    work_date = fields.Date(string="Work Date")
    labour_work_type = fields.Selection(
        [('bush_burning', "Bush Burning"), ('clearing_of_bushes', "Clearing of Bushes"), ('harvesting', "Harvesting"),
         ('mound_making', "Mound Making"), ('manuring', "Manuring"), ('planting', "Planting"),
         ('soil_preparation', "Soil Preparation"), ('storage', "Storage"), ('weeding', "Weeding")], string="Work Type")
    labour_type = fields.Selection([('day/price', "Day / Price"), ('hour/price', "Hour / Price")],
                                   string="Labour Type", default="hour/price")
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")
    total_hour = fields.Float(string="Total Hours", default=1)
    rate_hour = fields.Monetary(string="Rate")
    total_labour_cost = fields.Monetary(string="Total Cost")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    labour_bill_status = fields.Selection([('pending', "Pending"), ('bill_created', "Bill Created")],
                                          string="Bill Status", default="pending", readonly=True)
    bill_id = fields.Many2one('account.move', string="Bill")

    @api.constrains('work_date', 'farm_season_id')
    def _check_work_date(self):
        for record in self:
            if record.farm_season_id and record.work_date:
                if record.farm_season_id.start_date and record.farm_season_id.end_date:
                    if record.work_date < record.farm_season_id.start_date or record.work_date > record.farm_season_id.end_date:
                        raise ValidationError(
                            "The labor work date must fall between the start date and end date of the season.")

    @api.onchange('total_hour', 'rate_hour')
    def _get_total_labour_cost(self):
        for rec in self:
            rec.total_labour_cost = rec.total_hour * rec.rate_hour

    @api.constrains('total_labour_cost')
    def _total_labour_value(self):
        for record in self:
            if record.total_labour_cost == 0:
                raise ValidationError(_("Please, total costing of labour charge can not be zero"))

    def action_farm_labour_bill(self):
        farm_labour_view = self.env.ref('agriculture_management.farm_labour_bill_form_view').id
        return {
            'name': _('Farm Labour Charges'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'farm.labour.bill',
            'view_id': farm_labour_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }


class FarmCropDisease(models.Model):
    """Crop disease by Season"""
    _name = "farm.crop.disease"
    _description = __doc__
    _rec_name = 'crop_disease_id'

    start_date = fields.Date(string="Date of Occur")
    end_date = fields.Date(string="Date of End")
    expect_damage = fields.Float(string="Crop Damage (%)")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")
    crop_disease_id = fields.Many2one("crop.disease", required=True, domain="[('crop_ids', 'in', crop_id)]")

    @api.onchange('crop_id')
    def _onchange_crop_id(self):
        self.crop_disease_id = False

    @api.constrains('start_date', 'end_date', 'farm_season_id')
    def _check_crop_disease_time_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                # Check if end date is greater than start date
                if record.end_date < record.start_date:
                    raise ValidationError(_("Please ensure the crop disease end date is greater than the start date."))
                # Check if dates are within the farm season period
                if record.farm_season_id:
                    season_start = record.farm_season_id.start_date
                    season_end = record.farm_season_id.end_date
                    if season_start and season_end:
                        if (record.start_date < season_start or
                                record.end_date > season_end):
                            raise ValidationError(_(
                                "The crop disease duration must be between the start "
                                "and end dates of the farming season."
                            ))


class FarmCropFertiliser(models.Model):
    """Fertilisers by Season"""
    _name = "farm.crop.fertiliser"
    _description = __doc__
    _rec_name = 'fertiliser_id'

    fertiliser_id = fields.Many2one("crop.fertiliser", string="Fertiliser", required=True)
    qty = fields.Float(string="Number of Package", default=1)
    pkg_qty = fields.Float(related='fertiliser_id.pkg_qty')
    unit = fields.Many2one(related='fertiliser_id.uom_id', string="Package Size")
    cost = fields.Monetary(string="Cost")
    total_fertiliser_price = fields.Monetary(string="Total Cost", compute="_total_price")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    bill_status = fields.Selection([('pending', "Pending"), ('bill_created', "Bill Created")], string="Bill Status",
                                   default="pending", readonly=True)
    bill_id = fields.Many2one('account.move', string="Bill")

    delivery_order_id = fields.Many2one('stock.picking')
    delivery_order_state = fields.Selection(related='delivery_order_id.state', string="Order Status")

    @api.onchange('fertiliser_id')
    def fertiliser_product_price(self):
        for rec in self:
            if rec.fertiliser_id:
                rec.cost = rec.fertiliser_id.standard_price

    @api.depends('qty', 'cost')
    def _total_price(self):
        for rec in self:
            rec.total_fertiliser_price = rec.qty * rec.cost

    def action_crop_fertiliser_bill(self):
        crop_fertiliser_view = self.env.ref('agriculture_management.crop_fertiliser_bill_form_view').id
        return {
            'name': _('Crop Fertilisers'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'crop.fertiliser.bill',
            'view_id': crop_fertiliser_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }

    def action_crop_fertiliser_consume_order(self):
        crop_fertiliser_consume_view = self.env.ref('agriculture_management.fertiliser_consume_order_form_view').id
        return {
            'name': _('Crop Fertilisers'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'fertiliser.consume.order',
            'view_id': crop_fertiliser_consume_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }


class FarmCropPesticides(models.Model):
    """Pesticides by Season"""
    _name = "farm.crop.pesticides"
    _description = __doc__
    _rec_name = 'pesticide_id'

    pesticide_id = fields.Many2one("crop.pesticides", string="Pesticide", required=True)
    farm_crop_disease_id = fields.Many2one("farm.crop.disease", string="Farm Crop Disease",
                                           domain="[('farm_season_id', '=', farm_season_id)]")
    qty = fields.Float(string="Number of Package", default=1)
    pkg_qty = fields.Float(related='pesticide_id.pkg_qty')
    unit_id = fields.Many2one(related='pesticide_id.uom_id', string="Package Size")
    cost = fields.Monetary(string="Cost")
    total_price = fields.Monetary(string="Total Cost", compute="_total_price")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    pesticide_bill_status = fields.Selection([('pending', "Pending"), ('bill_created', "Bill Created")],
                                             string="Bill Status", default="pending", readonly=True)
    bill_id = fields.Many2one('account.move', string="Bill")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")

    delivery_order_id = fields.Many2one('stock.picking')
    delivery_order_state = fields.Selection(related='delivery_order_id.state', string="Order Status")

    @api.onchange('crop_id')
    def _onchange_crop_id(self):
        self.farm_crop_disease_id = False

    @api.onchange('pesticide_id')
    def pesticide_product_price(self):
        for rec in self:
            if rec.pesticide_id:
                rec.cost = rec.pesticide_id.standard_price

    @api.depends('qty', 'cost')
    def _total_price(self):
        for rec in self:
            rec.total_price = rec.qty * rec.cost

    def action_crop_pesticide_bill(self):
        crop_pesticide_view = self.env.ref('agriculture_management.crop_pesticide_bill_form_view').id
        return {
            'name': _('Crop Pesticides'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'crop.pesticide.bill',
            'view_id': crop_pesticide_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }

    def action_crop_pesticide_consume_order(self):
        crop_pesticide_consume_view = self.env.ref('agriculture_management.pesticide_consume_order_form_view').id
        return {
            'name': _('Crop Pesticides'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'pesticide.consume.order',
            'view_id': crop_pesticide_consume_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }


class FarmEquipmentUses(models.Model):
    """Equipment Uses by Season"""
    _name = "farm.equipment.uses"
    _description = __doc__
    _rec_name = 'equipment_id'

    equipment_id = fields.Many2one("agriculture.equipment", string="Equipment", required=True)
    rent_hours = fields.Float(string="Total Hours", default=1)
    rent_price = fields.Monetary(string="Price/Hour")
    total = fields.Monetary(string="Total Cost", compute="_get_total_equipment_cost")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")
    equipment_bill_status = fields.Selection([('pending', "Pending"), ('bill_created', "Bill Created")],
                                             string="Bill Status", default="pending", readonly=True)
    bill_id = fields.Many2one('account.move', string="Bill")

    @api.onchange('equipment_id')
    def equipment_product_price(self):
        for rec in self:
            if rec.equipment_id:
                rec.rent_price = rec.equipment_id.standard_price

    @api.depends('rent_hours', 'rent_price')
    def _get_total_equipment_cost(self):
        for rec in self:
            rec.total = rec.rent_hours * rec.rent_price

    def action_farm_equipment_bill(self):
        farm_equipment_view = self.env.ref('agriculture_management.farm_equipment_bill_form_view').id
        return {
            'name': _('Farm Equipments'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'farm.equipment.bill',
            'view_id': farm_equipment_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }


class MiscExpense(models.Model):
    """Misc Expenses by Season"""
    _name = "misc.expense"
    _inherits = {'product.product': 'product_id'}
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(related="product_id.name", store=True, readonly=False, required=True, inherited=True,
                       translate=False)
    detailed_type = fields.Selection(related="product_id.detailed_type", default='service', readonly=False, store=True)
    product_id = fields.Many2one('product.product', required=True, ondelete='cascade', auto_join=True, index=True,
                                 string=' Product')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")
    bill_id = fields.Many2one('account.move', string="Bill")
    expense_bill_status = fields.Selection([('pending', "Pending"), ('bill_created', "Bill Created")],
                                           string="Bill Status", default="pending", readonly=True)

    # unused
    title = fields.Char(string=" Expense")
    expense = fields.Monetary(string="Expense")

    @api.constrains('product_id')
    def _check_standard_price(self):
        for record in self:
            if record.product_id.standard_price == 0:
                raise ValidationError(_("Misc expense charge value cannot be zero."))

    def action_misc_expense_bill(self):
        misc_expense_view = self.env.ref('agriculture_management.misc_expense_bill_form_view').id
        return {
            'name': _('Misc Expense'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'misc.expense.bill',
            'view_id': misc_expense_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }


class ElectricityExpense(models.Model):
    """Electricity Expenses by Season"""
    _name = "electricity.expense"
    _inherits = {'product.product': 'product_id'}
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(related="product_id.name", store=True, readonly=False, required=True, inherited=True,
                       translate=False)
    detailed_type = fields.Selection(related="product_id.detailed_type", default='service', readonly=False, store=True)
    product_id = fields.Many2one('product.product', required=True, ondelete='cascade', auto_join=True, index=True,
                                 string=' Product')

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    electricity_bill_status = fields.Selection([('pending', "Pending"), ('bill_created', "Bill Created")],
                                               string="Bill Status", default="pending", readonly=True)
    bill_id = fields.Many2one('account.move', string="Bill")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')

    # unused
    cost = fields.Monetary(string=" Cost")

    @api.constrains('product_id')
    def _check_standard_price(self):
        for record in self:
            if record.product_id.standard_price == 0:
                raise ValidationError(_("Electricity expense charge value cannot be zero."))

    @api.constrains('start_date', 'end_date', 'farm_season_id')
    def _check_electricity_expense_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                # Check if end date is greater than start date
                if record.end_date < record.start_date:
                    raise ValidationError(_("Please ensure the electricity expense end date is greater than the "
                                            "start date."))
                # Check if dates are within the farm season period
                if record.farm_season_id:
                    season_start = record.farm_season_id.start_date
                    season_end = record.farm_season_id.end_date
                    if season_start and season_end:
                        if (record.start_date < season_start or
                                record.end_date > season_end):
                            raise ValidationError(_(
                                "The electricity expanse time duration must be between the start date and end"
                                " date of the farming season"
                            ))

    def action_electricity_expense_bill(self):
        electricity_expense_view = self.env.ref('agriculture_management.electricity_expense_bill_form_view').id
        return {
            'name': _('Electricity Expense'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'electricity.expense.bill',
            'view_id': electricity_expense_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }


class SeasonFleet(models.Model):
    """Fleet uses by Season"""
    _name = "season.fleet"
    _description = __doc__
    _rec_name = 'fleet_id'

    fleet_id = fields.Many2one('agriculture.fleet', string="Name", required=True)
    date_of_used = fields.Date(string="Date")
    fuel = fields.Float(string="Fuel", default=1)
    price = fields.Monetary(string="Liter / Price")
    total_price = fields.Monetary(string="Total Price", compute='_total_price')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    fleet_bill_status = fields.Selection([('pending', "Pending"), ('bill_created', "Bill Created")],
                                         string="Bill Status", default="pending", readonly=True)
    bill_id = fields.Many2one('account.move', string="Bill")
    farm_season_id = fields.Many2one("agriculture.season", string="Farm Season", ondelete='cascade')
    crop_ids = fields.Many2many(related="farm_season_id.crop_ids")
    crop_id = fields.Many2one("agriculture.crop", string="Crop", domain="[('id', 'in', crop_ids)]")

    @api.constrains('date_of_used', 'farm_season_id')
    def _check_date_of_used(self):
        for record in self:
            if record.farm_season_id and record.date_of_used:
                start_date = record.farm_season_id.start_date
                end_date = record.farm_season_id.end_date
                if start_date and end_date and not (start_date <= record.date_of_used <= end_date):
                    raise ValidationError(_(
                        "The fleet work date must fall between the start date and end date of the season."))

    @api.constrains('price')
    def _fleet_expanse_value(self):
        for record in self:
            if record.price == 0:
                raise ValidationError(_("Please, fleet expanse charge value can not be zero"))

    @api.depends('fuel', 'price')
    def _total_price(self):
        for rec in self:
            rec.total_price = rec.fuel * rec.price

    def action_season_fleet_bill(self):
        season_fleet_view = self.env.ref('agriculture_management.season_fleet_bill_form_view').id
        return {
            'name': _('Season Fleet'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'season.fleet.bill',
            'view_id': season_fleet_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }
