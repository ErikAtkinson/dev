# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _


class MiscExpenseBill(models.TransientModel):
    """Misc Expense Bill"""
    _name = 'misc.expense.bill'
    _description = __doc__

    vendor_id = fields.Many2one('res.partner', string="Vendor", required=True)
    misc_expense_ids = fields.Many2many("misc.expense", string="Misc Expenses")
    invoice_id = fields.Many2one('account.move')

    @api.model
    def default_get(self, field):
        res = super(MiscExpenseBill, self).default_get(field)
        active_ids = self._context.get('active_ids', [])
        filtered_bills = self.env['misc.expense'].browse(active_ids).filtered(lambda f: not f.bill_id)
        res['misc_expense_ids'] = [(6, 0, filtered_bills.ids)]
        return res

    def action_misc_expense_bill(self):
        invoice_lines = []
        farm_season = self.misc_expense_ids.mapped('farm_season_id')
        if all(record.bill_id for record in self.misc_expense_ids):
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
        for data in self.misc_expense_ids:
            order_data = {
                'product_id': data.product_id.id,
                'price_unit': data.standard_price,
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
        for rec in self.misc_expense_ids:
            if not rec.bill_id:
                rec.bill_id = invoice_id.id
                rec.expense_bill_status = "bill_created"
