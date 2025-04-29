from odoo import fields, models, _
from odoo.exceptions import UserError
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
            return 'https://messaging.gatewayapi.eu'
        return 'https://messaging.gatewayapi.com'

    def _get_gatewayapi_endpoint(self, account):
        base_url = self._get_gatewayapi_base_url(account)
        return f"{base_url}/mobile/multi"

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
            raise UserError(_(
                "No valid GatewayAPI account found. Please configure one."
            ))

        messages = []
        invalid_records = self.env['sms.sms']
        valid_records = self.env['sms.sms']

        for record in records:
            sender = self._sanitize_sender_name(record.sender)
            recipient = record.sanitized_number

            if not recipient:
                invalid_records |= record
                continue

            messages.append({
                "sender": sender,
                "message": record.message,
                "recipient": int(recipient.replace('+', '')),
                "priority": "normal",
                "expiration": "P5D",  # Default 5 days expiration
                "reference": record.id  # Use record ID as reference
            })
            valid_records |= record

        if invalid_records:
            invalid_records.write({
                'state': 'error',
                'error_code': 'invalid_recipient'
            })

        if not valid_records:
            return True

        headers = {
            'Content-Type': 'application/json',
            'Authorization': (
                f'Token {account.gatewayapi_token}'  # Updated auth format
            )
        }

        endpoint = self._get_gatewayapi_endpoint(account)
        _logger.info(f"Sending SMS to GatewayAPI: {endpoint}")

        try:
            # Send messages in batch using /mobile/multi endpoint
            response = requests.post(
                endpoint,
                headers=headers,
                json={"messages": messages}
            )
            response_data = response.json()

            if response.status_code != 200:  # API spec defines 200 as success
                error_message = response_data.get('detail', 'Unknown error')
                _logger.error(f"GatewayAPI error: {error_message}")
                valid_records.write({
                    'state': 'error',
                    'error_code': error_message
                })
            else:
                # Handle batch response
                for response_msg in response_data.get('responses', []):
                    msg_id = response_msg.get('msg_id')
                    reference = response_msg.get('reference')
                    if reference:
                        record = valid_records.filtered(
                            lambda r: str(r.id) == str(reference)
                        )
                        if record:
                            record.write({
                                'state': 'sent',
                                'error_code': False,
                                'gateway_id': msg_id
                            })
                            _logger.info(
                                f"SMS sent successfully: {response_msg}"
                            )

        except Exception as e:
            _logger.error(f"Error sending SMS through GatewayAPI: {e}")
            valid_records.write({
                'state': 'error',
                'error_code': str(e)
            })

        return True
