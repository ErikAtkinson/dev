# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _


class CropFertiliserBill(models.TransientModel):
    """Crop Fertiliser Bill"""
    _name = 'crop.fertiliser.bill'
    _description = __doc__

    vendor_id = fields.Many2one('res.partner', string="Vendor", required=True)
    farm_crop_fertiliser_ids = fields.Many2many('farm.crop.fertiliser', string="Crop Fertilisers")
    invoice_id = fields.Many2one('account.move')

    @api.model
    def default_get(self, field):
        res = super(CropFertiliserBill, self).default_get(field)
        active_ids = self._context.get('active_ids', [])
        filtered_bills = self.env['farm.crop.fertiliser'].browse(active_ids).filtered(lambda f: not f.bill_id)
        res['farm_crop_fertiliser_ids'] = [(6, 0, filtered_bills.ids)]
        return res

    def action_create_fertiliser_bill(self):
        invoice_lines = []
        farm_season = self.farm_crop_fertiliser_ids.mapped('farm_season_id')
        if all(record.bill_id for record in self.farm_crop_fertiliser_ids):
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
        for data in self.farm_crop_fertiliser_ids:
            order_data = {
                'product_id': data.fertiliser_id.product_id.id,
                'quantity': data.qty,
                'product_uom_id': data.unit.id,
                'price_unit': data.cost,
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
        for rec in self.farm_crop_fertiliser_ids:
            if not rec.bill_id:
                rec.bill_id = invoice_id.id
                rec.bill_status = "bill_created"
