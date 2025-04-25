from odoo import fields, models, api

class IapAccount(models.Model):
    _inherit = 'iap.account'

    provider_type = fields.Selection(selection_add=[('gatewayapi', 'GatewayAPI')])
    gatewayapi_platform = fields.Selection([
        ('eu', 'EU Platform (gatewayapi.eu)'),
        ('global', 'Global Platform (gatewayapi.com)')
    ], string='GatewayAPI Platform', default='eu')
    gatewayapi_token = fields.Char(string='API Token')

    @api.model
    def _get_service_from_provider(self, provider_type):
        if provider_type == 'gatewayapi':
            return 'sms_gatewayapi'
        return super()._get_service_from_provider(provider_type)

    @api.model
    def _get_service_from_provider_form(self):
        res = super()._get_service_from_provider_form()
        res['gatewayapi'] = 'sms_gatewayapi'
        return res
