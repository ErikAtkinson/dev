# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _


class SeasonFleetBill(models.TransientModel):
    """Season Fleet Bill"""
    _name = 'season.fleet.bill'
    _description = __doc__

    vendor_id = fields.Many2one('res.partner', string="Vendor", required=True)
    season_fleet_ids = fields.Many2many("season.fleet", string="Season Fleets")
    invoice_id = fields.Many2one('account.move')

    @api.model
    def default_get(self, field):
        res = super(SeasonFleetBill, self).default_get(field)
        active_ids = self._context.get('active_ids', [])
        filtered_fleets = self.env['season.fleet'].browse(active_ids).filtered(lambda f: not f.bill_id)
        res['season_fleet_ids'] = [(6, 0, filtered_fleets.ids)]
        return res

    def action_season_fleet_bill(self):
        invoice_lines = []
        farm_season = self.season_fleet_ids.mapped('farm_season_id')
        if all(record.bill_id for record in self.season_fleet_ids):
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("All bills already created"),
                    'sticky': False,
                }
            }
            return message
        for data in self.season_fleet_ids:
            order_data = {
                'product_id': data.fleet_id.product_id.id,
                'quantity': data.fuel,
                'price_unit': data.price,
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
        for rec in self.season_fleet_ids:
            if not rec.bill_id:
                rec.bill_id = invoice_id.id
                rec.fleet_bill_status = "bill_created"
