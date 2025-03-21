# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import xlwt
import base64
from io import BytesIO
from odoo import models, fields, api, _


class AgricultureFinancialYear(models.Model):
    """Financial Year"""
    _name = "agriculture.financial.year"
    _description = __doc__
    _rec_name = 'title'

    avatar = fields.Binary(string="Image")
    title = fields.Char(string="Title", translate=True)


class AgriculturalFinance(models.Model):
    """Financial Information"""
    _name = "agricultural.finance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'agriculture_financial_year_id'

    agriculture_financial_year_id = fields.Many2one("agriculture.financial.year", string="Agriculture Financial Year")
    farmer_id = fields.Many2one("res.partner", string="Farmer", domain=[('is_farmer', '=', True)])
    farm_id = fields.Many2one("agriculture.farm", string="Farm")
    season_id = fields.Many2one("agriculture.season", string="Agriculture Season")
    expense = fields.Monetary(string="Expense", related="season_id.total_cost")
    income = fields.Monetary(string="Income", related="season_id.production_price")
    profit_loss = fields.Monetary(string="Profit & Loss", related="season_id.total_product_income")

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    # XLS Report
    def print_excel_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet1 = workbook.add_sheet('Financial', cell_overwrite_ok=True)
        format1 = xlwt.easyxf('align:horiz center, vert center;font: color black;')
        format2 = xlwt.easyxf('align:horiz center, vert center;font: color black,bold True, height 250;')

        sheet1.col(0).width = 5000
        sheet1.col(1).width = 5000
        sheet1.col(2).width = 6000
        sheet1.col(3).width = 6000
        sheet1.col(4).width = 5000
        sheet1.col(5).width = 4000
        sheet1.col(6).width = 5000

        sheet1.write_merge(0, 0, 0, 6, 'Financial Report', format2)
        sheet1.row(0).height = 500
        sheet1.write(1, 0, "Financial Year", format2)
        sheet1.write(1, 1, "Farm Name", format2)
        sheet1.write(1, 2, "Farmer Name", format2)
        sheet1.write(1, 3, "Agriculture Season", format2)
        sheet1.write(1, 4, "Income(₹)", format2)
        sheet1.write(1, 5, "Expense(₹)", format2)
        sheet1.write(1, 6, "Profit & Loss(₹)", format2)

        sheet1.write(2, 0, self.agriculture_financial_year_id.title, format1)
        sheet1.write(2, 1, self.farm_id.farm_name, format1)
        sheet1.write(2, 2, self.farmer_id.name, format1)
        sheet1.write(2, 3, self.season_id.name, format1)
        sheet1.write(2, 4, self.income, format1)
        sheet1.write(2, 5, self.expense, format1)
        sheet1.write(2, 6, self.profit_loss, format1)

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())

        attachment = self.env['ir.attachment'].sudo()
        filename = self.agriculture_financial_year_id.title + '.xls'
        attachment_id = attachment.create(
            {'name': filename,
             'type': 'binary',
             'public': False,
             'datas': out
             })
        if attachment_id:
            report = {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment_id.id),
                'target': self,
                'nodestroy': False,
            }
            return report
