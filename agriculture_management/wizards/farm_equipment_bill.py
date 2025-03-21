# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _


class FarmEquipmentBill(models.TransientModel):
    """Farm Equipment Bill"""
    _name = 'farm.equipment.bill'
    _description = __doc__

    vendor_id = fields.Many2one('res.partner', string="Vendor", required=True)
    equipment_use_ids = fields.Many2many("farm.equipment.uses", string="Uses of Equipments")
    invoice_id = fields.Many2one('account.move')

    @api.model
    def default_get(self, field):
        res = super(FarmEquipmentBill, self).default_get(field)
        active_ids = self._context.get('active_ids', [])
        filtered_bills = self.env['farm.equipment.uses'].browse(active_ids).filtered(lambda f: not f.bill_id)
        res['equipment_use_ids'] = [(6, 0, filtered_bills.ids)]
        return res

    def action_farm_equipment_bill(self):
        invoice_lines = []
        farm_season = self.equipment_use_ids.mapped('farm_season_id')
        if all(record.bill_id for record in self.equipment_use_ids):
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
        for data in self.equipment_use_ids:
            order_data = {
                'product_id': data.equipment_id.product_id.id,
                'quantity': data.rent_hours,
                'product_uom_id': data.equipment_id.product_id.uom_id.id,
                'price_unit': data.rent_price,
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
        for rec in self.equipment_use_ids:
            if not rec.bill_id:
                rec.bill_id = invoice_id.id
                rec.equipment_bill_status = "bill_created"
