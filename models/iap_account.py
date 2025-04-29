from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import requests
import re

GATEWAYAPI_BASE_URLS = {
    'eu': 'https://gatewayapi.eu',
    'global': 'https://gatewayapi.com',
}

SENDER_REGEX = re.compile(r'^[A-Za-z0-9]{1,11}$|^[0-9]{1,15}$')

class IapAccount(models.Model):
    _inherit = 'iap.account'

    provider_type = fields.Selection(
        selection=[('gatewayapi', 'GatewayAPI')],
        string='Provider Type',
    )
    gatewayapi_base_url = fields.Selection([
        ('eu', 'EU Platform (gatewayapi.eu)'),
        ('global', 'Global Platform (gatewayapi.com)')
    ], string='GatewayAPI Platform', default='eu', required=True)
    gatewayapi_token = fields.Char(string='API Token', required=True)
    gatewayapi_sender = fields.Char(
        string='Sender Name',
        help=(
            'Sender name for SMS sent via GatewayAPI. '
            'Alphanumeric up to 11 chars or numeric up to 15 digits.'
        ),
        size=15,
        required=True
    )

    @api.constrains('gatewayapi_sender')
    def _check_sender_name(self):
        for rec in self:
            if rec.provider_type == 'gatewayapi' and rec.gatewayapi_sender:
                if not SENDER_REGEX.match(rec.gatewayapi_sender):
                    raise ValidationError(_(
                        'Sender name must be alphanumeric (up to 11 chars) or numeric (up to 15 digits).'
                    ))

    def action_test_gatewayapi_connection(self):
        for rec in self:
            if rec.provider_type != 'gatewayapi':
                continue
            url = (
                GATEWAYAPI_BASE_URLS[rec.gatewayapi_base_url]
                + '/rest/auth'
            )
            headers = {'Authorization': f'Token {rec.gatewayapi_token}'}
            try:
                response = requests.get(
                    url, headers=headers, timeout=10
                )
                if response.status_code == 200:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Connection Successful'),
                            'message': _('Successfully connected to GatewayAPI.'),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    raise UserError(_(
                        'Connection failed: %s'
                    ) % response.text)
            except Exception as e:
                raise UserError(_(
                    'Connection error: %s'
                ) % str(e))

    def send_sms_gatewayapi(self, message, recipient):
        self.ensure_one()
        if self.provider_type != 'gatewayapi':
            raise UserError(_(
                'This account is not configured for GatewayAPI.'
            ))
        url = (
            GATEWAYAPI_BASE_URLS[self.gatewayapi_base_url]
            + '/v1/message'
        )
        headers = {'Authorization': f'Token {self.gatewayapi_token}'}
        payload = {
            'sender': self.gatewayapi_sender,
            'message': message,
            'recipients': [recipient],
        }
        response = requests.post(
            url, json=payload, headers=headers
        )
        if response.status_code not in (200, 202):
            raise UserError(_(
                'Failed to send SMS: %s'
            ) % response.text)
        return response.json()

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
