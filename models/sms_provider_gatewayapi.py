from odoo import models, _
from odoo.exceptions import UserError

GATEWAYAPI_STATUS_MAP = {
    'delivered': 'delivered',
    'enroute': 'sent',
    'accepted': 'sent',
    'expired': 'error',
    'deleted': 'error',
    'undeliverable': 'error',
    'unknown': 'error',
    'rejected': 'error',
}


class SmsProviderGatewayapi(models.Model):
    _inherit = 'sms.provider'

    def _gatewayapi_get_account(self):
        account = self.env['iap.account'].search([
            ('provider_type', '=', 'gatewayapi')
        ], limit=1)
        if not account:
            raise UserError(_('No GatewayAPI IAP account configured.'))
        return account

    def send_message(self, sms, **kwargs):
        account = self._gatewayapi_get_account()
        response = account.send_sms_gatewayapi(sms.body, sms.partner_mobile)
        # Store GatewayAPI message id for webhook matching
        sms.external_id = response.get('msg_id')
        sms.state = GATEWAYAPI_STATUS_MAP.get(
            response.get('status', 'sent'), 'sent'
        )
        return True

    def get_message_status(self, sms):
        # Optionally implement polling if needed
        return sms.state 