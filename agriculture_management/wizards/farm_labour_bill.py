# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _


class FarmLabourBill(models.TransientModel):
    """Farm Labour Bill"""
    _name = 'farm.labour.bill'
    _description = __doc__

    vendor_id = fields.Many2one('res.partner', string="Vendor", required=True)
    farm_labour_ids = fields.Many2many("farm.labour", string="Farm Labours")
    invoice_id = fields.Many2one('account.move')

    @api.model
    def default_get(self, field):
        res = super(FarmLabourBill, self).default_get(field)
        active_ids = self._context.get('active_ids', [])
        filtered_bills = self.env['farm.labour'].browse(active_ids).filtered(lambda f: not f.bill_id)
        res['farm_labour_ids'] = [(6, 0, filtered_bills.ids)]
        return res

    def action_farm_labour_bill(self):
        invoice_lines = []
        farm_season = self.farm_labour_ids.mapped('farm_season_id')
        if all(record.bill_id for record in self.farm_labour_ids):
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': "All bills already created",
                    'sticky': False,
                }
            }
            return message
        for data in self.farm_labour_ids:
            worker_name = ""
            work_types = ""
            worker_working_date = ""

            for worker in data:
                worker_name = worker_name + " {} ".format(worker.worker_id.name)
            for w_type in data:
                work_types = work_types + " {} ".format(
                    dict(w_type._fields['labour_work_type'].selection).get(w_type.labour_work_type))
            for date in data:
                worker_working_date = worker_working_date + " {} ".format(date.work_date)
            if data.labour_type == 'day/price':
                order_data = {
                    'product_id': self.env.ref('agriculture_management.labour_service_charge_per_day').id,
                    'name': worker_name + "/" + work_types + "/" + worker_working_date,
                    'quantity': 1,
                    'price_unit': data.total_labour_cost,
                }
                invoice_lines.append((0, 0, order_data))
            if data.labour_type == 'hour/price':
                order_data = {
                    'product_id': self.env.ref('agriculture_management.labour_service_charge_per_hour').id,
                    'name': worker_name + "/" + work_types + "/" + worker_working_date,
                    'quantity': data.total_hour,
                    'price_unit': data.rate_hour,
                }
                invoice_lines.append((0, 0, order_data))
        data = {
            'partner_id': self.vendor_id.id,
            'move_type': 'in_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
            'agriculture_season_id': farm_season.id
        }
        invoice_id = self.env['account.move'].sudo().create(data)
        for rec in self.farm_labour_ids:
            if not rec.bill_id:
                rec.bill_id = invoice_id.id
                rec.labour_bill_status = "bill_created"
