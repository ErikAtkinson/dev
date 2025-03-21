# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import xlwt
import base64
from io import BytesIO
from odoo import fields, models


class SeasonReport(models.TransientModel):
    """Crop Season Report"""
    _name = "season.report"
    _description = __doc__

    agriculture_season_id = fields.Many2one('agriculture.season', required=True)

    def print_excel_report(self):
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
        for rec in self.agriculture_season_id.crop_ids:
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

        sheet1.write(2, 1, self.agriculture_season_id.name, format5)
        sheet1.write(3, 1, self.agriculture_season_id.financial_year_id.title, format5)
        sheet1.write(4, 1, self.agriculture_season_id.farm_id.farm_name, format5)
        sheet1.write(5, 1, self.agriculture_season_id.farmer_id.name, format5)
        sheet1.write(6, 1, self.agriculture_season_id.start_date, date_format)
        sheet1.write(7, 1, self.agriculture_season_id.end_date, date_format)
        sheet1.write(8, 1, self.agriculture_season_id.responsible.name, format5)
        sheet1.write(9, 1, crops, format5)

        sheet1.write_merge(15, 15, 0, 4, "Season Crops", format2)
        sheet1.row(15).height = 500
        sheet1.write(16, 0, "Crop", format3)
        sheet1.write(16, 1, "Plantation Area", format3)
        sheet1.write(16, 2, "Land Measure", format3)
        sheet1.write(16, 3, "Planting Date", format3)
        sheet1.write(16, 4, "Status", format3)

        row = 17
        for rec in self.agriculture_season_id.season_crop_ids:
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
        for rec in self.agriculture_season_id.crop_disease_ids:
            sheet1.write(row, 6, rec.crop_disease_id.name, format1)
            sheet1.write(row, 7, rec.expect_damage, format1)
            sheet1.write(row, 8, rec.start_date, date_format)
            sheet1.write(row, 9, rec.end_date, date_format)
            row += 1

        sheet1.write_merge(15, 15, 11, 12, "Misc Expense", format2)
        sheet1.write(16, 11, "Expense Type", format3)
        sheet1.write(16, 12, "Expense", format3)

        row = 17
        for rec in self.agriculture_season_id.misc_expense_ids:
            sheet1.write(row, 11, rec.title, format1)
            sheet1.write(row, 12, rec.expense, format1)
            row += 1

        sheet1.write_merge(15, 15, 14, 20, "Crop Production", format2)
        sheet1.write(16, 14, "Crop", format3)
        sheet1.write(16, 15, "Description", format3)
        sheet1.write(16, 16, "Warehouse", format3)
        sheet1.write(16, 17, "Qty", format3)
        sheet1.write(16, 18, "Qty on Hand", format3)
        sheet1.write(16, 19, "Unit", format3)
        sheet1.write(16, 20, "Price", format3)
        sheet1.write(16, 21, "Total", format3)

        row = 17
        for rec in self.agriculture_season_id.crop_production_ids:
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
        for rec in self.agriculture_season_id.season_budget_ids:
            sheet1.write(row, 23, rec.budget_type, format1)
            sheet1.write(row, 24, rec.qty, format1)
            sheet1.write(row, 25, rec.unit_id.name, format1)
            sheet1.write(row, 26, rec.price, format1)
            sheet1.write(row, 27, rec.total_price, format1)
            row += 1

        sheet1.write_merge(0, 0, 6, 7, 'Estimation Cost', format2)
        sheet1.write(1, 6, "Production Income", format5)
        sheet1.write(2, 6, "Profit & Loss", format5)

        sheet1.write(1, 7, self.agriculture_season_id.production_price, format5)
        sheet1.write(2, 7, self.agriculture_season_id.total_product_income, format5)

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

        sheet1.write(3, 7, self.agriculture_season_id.labour_charge, format5)
        sheet1.write(4, 7, self.agriculture_season_id.pesticide_charge, format5)
        sheet1.write(5, 7, self.agriculture_season_id.fertiliser_charge, format5)
        sheet1.write(6, 7, self.agriculture_season_id.seed_charge, format5)
        sheet1.write(7, 7, self.agriculture_season_id.equipment_charge, format5)
        sheet1.write(8, 7, self.agriculture_season_id.fleet_charge, format5)
        sheet1.write(9, 7, self.agriculture_season_id.misc_expense, format5)
        sheet1.write(10, 7, self.agriculture_season_id.crop_incident, format5)
        sheet1.write(11, 7, self.agriculture_season_id.electricity_expense, format5)
        sheet1.write(12, 7, self.agriculture_season_id.total_cost, format5)

        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())

        attachment = self.env['ir.attachment'].sudo()
        filename = self.agriculture_season_id.name + '.xls'
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
