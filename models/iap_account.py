from odoo import fields, models, api


class IapAccount(models.Model):
    _inherit = 'iap.account'

    provider_type = fields.Selection(
        selection=[('gatewayapi', 'GatewayAPI')],
        string='Provider Type'
    )
    gatewayapi_platform = fields.Selection([
        ('eu', 'EU Platform (gatewayapi.eu)'),
        ('global', 'Global Platform (gatewayapi.com)')
    ], string='GatewayAPI Platform', default='eu')
    gatewayapi_token = fields.Char(string='API Token')
    gatewayapi_sender = fields.Char(
        string='Sender Name',
        help=(
            'Sender name for SMS sent via GatewayAPI. '
            'Alphanumeric up to 11 chars or numeric up to 15 digits.'
        ),
        size=15
    )

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
