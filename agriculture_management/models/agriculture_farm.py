# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_farmer = fields.Boolean(string="Farmer")
    farmer_region_id = fields.Many2one('farmer.region', string="Region")
    is_agronomist = fields.Boolean(string="Agronomist")
    is_field_manager = fields.Boolean(string="Field Manager")
    farm_ids = fields.One2many("agriculture.farm", 'farmer_id')

    farm_count = fields.Integer(compute='_get_farms')

    def _get_farms(self):
        for record in self:
            record.farm_count = self.env["agriculture.farm"].search_count([('farmer_id', '=', self.id)])

    def view_agriculture_farm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Farms',
            'view_mode': 'tree,form',
            'res_model': "agriculture.farm",
            'domain': [('farmer_id', '=', self.id)],
        }


class AgricultureFarm(models.Model):
    """Agriculture Lands/Farms"""
    _name = "agriculture.farm"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'farm_name'

    farm_image = fields.Binary(string="Farm Image")
    farm_name = fields.Char(string="Farm Name", translate=True)

    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(string="City", translate=True)
    state_id = fields.Many2one("res.country.state", string='State',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char(string="Zip")
    latitude_location = fields.Char(string='Latitude')
    longitude_location = fields.Char(string='Longitude')

    farmer_id = fields.Many2one("res.partner", string="Farmer", domain=[('is_farmer', '=', True)])
    agriculture_fleet_ids = fields.Many2many("agriculture.fleet", string="Fleets")
    farm_id = fields.Many2one("agriculture.season")
    farm_type_id = fields.Many2one("farm.types", string="Farm Type")
    animals_count = fields.Integer(compute='_get_animals')
    farm_season_count = fields.Integer(compute='_get_farm_season')

    # unused
    farm_animal_ids = fields.One2many("farm.animal", "farm_id", string="Farm Animal")

    def _get_animals(self):
        for record in self:
            record.animals_count = self.env["farm.animal"].search_count([('farm_id', '=', self.id)])

    def view_farm_animal(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Animals'),
            'view_mode': 'tree,form',
            'res_model': 'farm.animal',
            'domain': [('farm_id', '=', self.id)],
            'context': {'default_farm_id': self.id},
        }

    def _get_farm_season(self):
        for record in self:
            record.farm_season_count = self.env["agriculture.season"].search_count([('farm_id', '=', self.id)])

    def view_agriculture_farm_season(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Farm Seasons'),
            'view_mode': 'tree,form',
            'res_model': "agriculture.season",
            'domain': [('farm_id', '=', self.id)],
        }


class FarmAnimal(models.Model):
    """Animal Details"""
    _name = "farm.animal"
    _description = __doc__
    _rec_name = "animal_name"

    avatar = fields.Binary(string="Image")
    animal_name = fields.Char(string="Animal")
    animal_type = fields.Selection([('animal', "Animal"), ('bird', "Bird")], string="Animal Type")
    farm_id = fields.Many2one("agriculture.farm", string="Farm", ondelete='cascade')

    @api.constrains('animal_type')
    def _check_animal_type(self):
        for record in self:
            if not record.animal_type:
                raise ValidationError(_("Please select a animal type: animal or bird"))


class FarmTypes(models.Model):
    """Farm Types"""
    _name = "farm.types"
    _description = __doc__
    _rec_name = "farm_types"

    avatar = fields.Binary(string="Image")
    farm_types = fields.Char(string="Farm Type")


class FarmerRegion(models.Model):
    """ Farmer Region """
    _name = "farmer.region"
    _description = __doc__
    _rec_name = "name"

    name = fields.Char(string="Name")
