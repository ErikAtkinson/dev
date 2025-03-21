# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import xlwt
import base64
from io import BytesIO
from odoo import fields, models


class BudgetVsActualSpendReport(models.TransientModel):
    """Budget vs Actual Spent Report"""
    _name = "budget.vs.actual.spend.report"
    _description = __doc__

    agriculture_season_id = fields.Many2one('agriculture.season', string="Season Budget Report", required=True)

    def print_excel_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet1 = workbook.add_sheet('Budget vs Actual Spent Report', cell_overwrite_ok=True)
        format1 = xlwt.easyxf('align:horiz left, vert center;font: color black;')
        format2 = xlwt.easyxf('align:horiz center, vert center;font: color black,bold True, height 250;')
        format3 = xlwt.easyxf('align:horiz left, vert center;font: color black,bold True, height 180;')

        sheet1.col(0).width = 4000
        sheet1.col(1).width = 2800
        sheet1.col(2).width = 700
        sheet1.col(3).width = 4500
        sheet1.col(4).width = 2800
        sheet1.col(5).width = 700
        sheet1.col(6).width = 3200
        sheet1.col(7).width = 3200

        sheet1.write_merge(0, 0, 0, 7, "Budget Vs Actual Spent Report", format2)
        sheet1.row(0).height = 600
        sheet1.write_merge(2, 2, 0, 1, "Budget", format2)
        sheet1.row(2).height = 300
        sheet1.write(4, 0, "Budget Type", format3)
        sheet1.write(4, 1, "Total Cost", format3)

        row = 5
        for rec in self.agriculture_season_id.season_budget_ids:
            sheet1.write(row, 0, rec.budget_type, format1)
            sheet1.write(row, 1, rec.total_price, format1)
            row += 1
        sheet1.write(row, 0, "Total Budget", format3)
        sheet1.write(row, 1, self.agriculture_season_id.season_budget, format3)

        sheet1.write_merge(2, 2, 3, 4, "Actual Expense", format2)
        sheet1.row(2).height = 300
        sheet1.write(4, 3, "Labour Cost", format1)
        sheet1.write(5, 3, "Pesticide Cost", format1)
        sheet1.write(6, 3, "Fertiliser Cost", format1)
        sheet1.write(7, 3, "Seed Cost", format1)
        sheet1.write(8, 3, "Equipment Cost", format1)
        sheet1.write(9, 3, "Fleet Cost", format1)
        sheet1.write(10, 3, "Misc Expense", format1)
        sheet1.write(11, 3, "Crop Incident", format1)
        sheet1.write(12, 3, "Electricity Expense", format1)
        sheet1.write(13, 3, "Total Cost", format3)

        sheet1.write(4, 4, self.agriculture_season_id.labour_charge, format1)
        sheet1.write(5, 4, self.agriculture_season_id.pesticide_charge, format1)
        sheet1.write(6, 4, self.agriculture_season_id.fertiliser_charge, format1)
        sheet1.write(7, 4, self.agriculture_season_id.seed_charge, format1)
        sheet1.write(8, 4, self.agriculture_season_id.equipment_charge, format1)
        sheet1.write(9, 4, self.agriculture_season_id.fleet_charge, format1)
        sheet1.write(10, 4, self.agriculture_season_id.misc_expense, format1)
        sheet1.write(11, 4, self.agriculture_season_id.crop_incident, format1)
        sheet1.write(12, 4, self.agriculture_season_id.electricity_expense, format1)
        sheet1.write(13, 4, self.agriculture_season_id.total_cost, format3)

        sheet1.write_merge(2, 2, 6, 7, 'Budget vs Spent', format2)
        sheet1.row(2).height = 300
        sheet1.write(4, 6, "Budget Cost", format3)
        sheet1.write(4, 7, "Total Expanse", format3)

        sheet1.write(5, 6, self.agriculture_season_id.season_budget, format1)
        sheet1.write(5, 7, self.agriculture_season_id.total_cost, format1)

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())

        attachment = self.env['ir.attachment'].sudo()
        filename = self.agriculture_season_id.name + '_Budget.xls'
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
