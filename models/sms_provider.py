from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json
import logging
import requests

_logger = logging.getLogger(__name__)

class GatewayAPIProvider(models.Model):
    _inherit = 'sms.provider'
    _description = 'GatewayAPI Provider'

    provider_type = fields.Selection(
        selection_add=[('gatewayapi', 'GatewayAPI')],
        ondelete={'gatewayapi': 'set default'}
    )

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

    def _send_sms_batch(self, records):
        if self.provider_type != 'gatewayapi':
            return super()._send_sms_batch(records)

        account = self._get_gatewayapi_account()
        if not account or not account.gatewayapi_token:
            raise UserError(_("No valid GatewayAPI account found. Please configure one."))

        messages = []
        for record in records:
            sender = self._sanitize_sender_name(record.sender)
            recipient = record.sanitized_number
            message = record.message

            if not recipient:
                record.state = 'error'
                record.error_code = 'invalid_recipient'
                continue

            messages.append({
                "message": message,
                "recipients": [{"msisdn": int(recipient)}],
                "sender": sender
            })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {account.gatewayapi_token}'
        }

        endpoint = self._get_gatewayapi_endpoint(account)
        _logger.info(f"Sending SMS to GatewayAPI: {endpoint}")

        try:
            for message in messages:
                response = requests.post(endpoint, headers=headers, json=message)
                response_data = response.json()

                if response.status_code != 200:
                    error_message = response_data.get('message', 'Unknown error')
                    _logger.error(f"GatewayAPI error: {error_message}")
                    record.state = 'error'
                    record.error_code = error_message
                else:
                    record.state = 'sent'
                    record.error_code = False
                    # Store message ID for reference
                    record.gateway_id = response_data.get('ids', [''])[0]
                    
                    _logger.info(f"SMS sent successfully: {response_data}")
        except Exception as e:
            _logger.error(f"Error sending SMS through GatewayAPI: {e}")
            record.state = 'error'
            record.error_code = str(e)

        return True

    def _get_available_provider_types(self):
        res = super()._get_available_provider_types()
        res.append('gatewayapi')
        return res
        
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
