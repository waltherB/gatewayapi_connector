from odoo import api, fields, models

class SmsSms(models.Model):
    _inherit = 'sms.sms'

    gateway_id = fields.Char('GatewayAPI Message ID')
