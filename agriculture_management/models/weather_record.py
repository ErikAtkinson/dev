# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _
from datetime import datetime


class WeatherRecord(models.Model):
    """Weather Record"""
    _name = "weather.record"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'weather_no'

    weather_no = fields.Char(string='Weather No', required=True, readonly=True, default=lambda self: _('New'),
                             copy=False)
    agriculture_farm_id = fields.Many2one('agriculture.farm', string="Farm", required=True)
    street = fields.Char(related="agriculture_farm_id.street", translate=True)
    street2 = fields.Char(related="agriculture_farm_id.street2", translate=True)
    city = fields.Char(related="agriculture_farm_id.city", translate=True)
    state_id = fields.Many2one(related="agriculture_farm_id.state_id", string="State")
    country_id = fields.Many2one(related="agriculture_farm_id.country_id", string="Country")
    zip = fields.Char(related="agriculture_farm_id.zip")

    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Responsible",
                                     required=True)
    created_date = fields.Datetime(string="Created Date", default=fields.Datetime.now)
    min_temp = fields.Float(string="Min.Temp(in F)")
    max_temp = fields.Float(string="Max.Temp(in F)")
    max_uv_index = fields.Char(string="Max.UV Index")
    wind = fields.Char(string="Wind")
    wind_gusts = fields.Char(string="Wind Gusts")
    humidity = fields.Char(string="Humidity")
    indoor_humidity = fields.Char(string="Indoor Humidity")
    dew_point = fields.Char(string="Dew Point")
    pressure = fields.Char(string="Pressure")
    cloud_cover = fields.Float(string="Cloud Cover (%)")
    visibility = fields.Char(string="Visibility")
    cloud_ceiling = fields.Char(string="Cloud Ceiling")
    daily_weather_ids = fields.One2many('daily.weather', 'weather_record_id', string="Daily Weather")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('weather_no', _('New')) == _('New'):
                vals['weather_no'] = self.env['ir.sequence'].next_by_code('weather.record') or _('New')
        res = super(WeatherRecord, self).create(vals_list)
        return res


class DailyWeather(models.Model):
    """Daily Weather"""
    _name = "daily.weather"
    _description = __doc__
    _rec_name = 'weather_type_id'

    weather_type_id = fields.Many2one('weather.type', string="Weather", required=True)
    date = fields.Date(string="Date", default=datetime.today())

    temperature = fields.Float(string="Temperature")
    forecast = fields.Char(string="Forecast")
    real_feel = fields.Float(string="Real Feel")
    wind = fields.Char(string="Wind")
    rain = fields.Float(string="Rain (%)")
    snow = fields.Float(string="Snow (%)")
    ice = fields.Float(string="Ice (%)")
    humidity = fields.Float(string="Humidity (%)")
    visibility = fields.Char(string="Visibility")
    weather_record_id = fields.Many2one('weather.record', ondelete='cascade')


class WeatherType(models.Model):
    """Weather Type"""
    _name = "weather.type"
    _description = __doc__
    _rec_name = 'title'

    title = fields.Char(string="Title", required=True)
