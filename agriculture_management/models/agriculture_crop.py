# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class AgricultureCrop(models.Model):
    """Crop Details"""
    _name = "agriculture.crop"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'crop_name'

    color = fields.Integer(default=1)
    crop_image = fields.Binary(string="Crop Image")
    crop_name = fields.Char(string="Name", translate=True)
    crop_period = fields.Integer(string="Crop Period (Days)")
    crop_type = fields.Selection([('annual', "Annual"), ('perennial', "Perennial"), ('biennial', "Biennial")],
                                 string="Type")
    cropping_type_id = fields.Many2one('cropping.type', string="Cropping Type")
    description = fields.Text(string="Description", translate=True)
    instructions = fields.Text(string="Instructions", translate=True)
    prescriptions = fields.Text(string="prescriptions", translate=True)
    product_id = fields.Many2one('product.product', string="Product")
    uom_id = fields.Many2one('uom.uom', string="Measurement Unit")

    # Link to Product
    def action_link_product(self):
        data = {
            'image_1920': self.crop_image,
            'name': self.crop_name,
            'detailed_type': 'product',
            'sale_ok': True,
            'purchase_ok': False,
            'uom_id': self.uom_id.id if self.uom_id else False,
            'uom_po_id': self.uom_id.id if self.uom_id else False,
        }
        product_id = self.env['product.product'].create(data)
        self.product_id = product_id.id


class CropHealthyManure(models.Model):
    """Crop Healthy Manure"""
    _name = "crop.healthy.manure"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", translate=True)
    crop_id = fields.Many2one("agriculture.crop", string="Crop")
    qty = fields.Float(string="Qty")
    unit_id = fields.Many2one("uom.uom", string="Unit")
    price = fields.Monetary(string="Price")
    dosage = fields.Char(string="Dosage", translate=True)
    benefits = fields.Text(string="Benefits", translate=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")


class CroppingType(models.Model):
    """Cropping Type"""
    _name = "cropping.type"
    _description = __doc__
    _rec_name = 'title'

    title = fields.Char(string="Title")
    description = fields.Text(string="Description")
