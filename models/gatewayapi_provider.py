from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json
import logging
import requests

_logger = logging.getLogger(__name__)

class GatewayAPIProvider(models.Model):
    _name = 'gatewayapi.provider'
    _description = 'GatewayAPI Provider'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    gatewayapi_platform = fields.Selection([
        ('eu', 'EU Platform (gatewayapi.eu)'),
        ('global', 'Global Platform (gatewayapi.com)')
    ], string='GatewayAPI Platform', default='eu')
    
    def _get_gatewayapi_account(self):
        return self.env['iap.account'].get_account('sms_gatewayapi')

    def _get_gatewayapi_base_url(self, account):
        if account.gatewayapi_platform == 'eu':
            return 'https://gatewayapi.eu'
        return 'https://gatewayapi.com'

    def _get_gatewayapi_endpoint(self, account):
        base_url = self._get_gatewayapi_base_url(account)
        return f"{base_url}/rest/mtsms"

    def _sanitize_sender_name(self, sender):
        """
        Sanitize sender name according to GatewayAPI's limitations:
        - Alphanumeric: Up to 11 characters
        - Numeric: Up to 15 digits
        - Full UTF-8: Up to 11 characters
        """
        if not sender:
            return ''
            
        # Check if sender is numeric
        if sender.isdigit():
            return sender[:15]
        
        # Otherwise treat as alphanumeric or UTF-8 with 11 char limit
        return sender[:11]
        
    def action_configure_gatewayapi_account(self):
        """Open the IAP Account configuration for GatewayAPI."""
        account = self._get_gatewayapi_account()
        action = self.env.ref('iap.iap_account_action').read()[0]
        action.update({
            'context': {
                'default_service_name': 'sms_gatewayapi',
                'default_provider_type': 'gatewayapi',
            }
        })
        if account:
            action['res_id'] = account.id
        return action
