# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _


class PesticideConsumeOrder(models.TransientModel):
    """Pesticide Consume Order"""
    _name = 'pesticide.consume.order'
    _description = __doc__

    farm_crop_pesticide_ids = fields.Many2many('farm.crop.pesticides', string="Crop Pesticides")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    delivery_order_id = fields.Many2one('stock.picking')

    @api.model
    def default_get(self, field):
        res = super(PesticideConsumeOrder, self).default_get(field)
        active_ids = self._context.get('active_ids', [])
        filtered_pesticides = self.env['farm.crop.pesticides'].browse(active_ids).filtered(
            lambda f: not f.delivery_order_id)
        res['farm_crop_pesticide_ids'] = [(6, 0, filtered_pesticides.ids)]
        return res

    def action_create_consume_order(self):
        dest_location_id = self.warehouse_id.consume_stock_location_id
        if not dest_location_id:
            dest_location_id = self.env['stock.location'].create(
                {'name': f"Consume Location/{self.warehouse_id.name}", 'usage': 'production'})
            self.warehouse_id.consume_stock_location_id = dest_location_id.id

        lines = []
        farm_season = self.farm_crop_pesticide_ids.mapped('farm_season_id')
        if all(record.delivery_order_id for record in self.farm_crop_pesticide_ids):
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("All Delivery orders already created"),
                    'sticky': False,
                }
            }
            return message
        for line in self.farm_crop_pesticide_ids:
            lines.append((0, 0, {
                'product_id': line.pesticide_id.product_id.id,
                'product_uom_qty': line.qty,
                'product_uom': line.pesticide_id.product_id.uom_id.id,
                'location_id': self.warehouse_id.lot_stock_id.id,
                'location_dest_id': dest_location_id.id,
                'name': line.pesticide_id.product_id.name
            }))
        stock_picking_type_id = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('warehouse_id', '=', self.warehouse_id.id)], limit=1)
        delivery_record = {
            'picking_type_id': stock_picking_type_id.id,
            'location_id': self.warehouse_id.lot_stock_id.id,
            'location_dest_id': dest_location_id.id,
            'move_ids_without_package': lines,
            'move_type': 'one',
            'agriculture_season_id': farm_season.id,
        }
        delivery_order_id = self.env['stock.picking'].create(delivery_record)
        for rec in self.farm_crop_pesticide_ids:
            if not rec.delivery_order_id:
                rec.delivery_order_id = delivery_order_id.id
