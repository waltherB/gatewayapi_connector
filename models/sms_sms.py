from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class SmsSms(models.Model):
    _inherit = 'sms.sms'

    gateway_id = fields.Char('GatewayAPI Message ID')
    
    @api.model
    def _send_sms(self, body, numbers):
        """Override to send SMS via GatewayAPI."""
        self = self.sudo()
        
        # Try to use GatewayAPI
        provider = self.env['sms.provider'].search([
            ('provider_type', '=', 'gatewayapi')
        ], limit=1)
        if not provider:
            return super()._send_sms(body, numbers)
            
        account = provider._get_gatewayapi_account()
        if not account or not account.gatewayapi_token:
            raise UserError(_("No valid GatewayAPI account found. Please configure one."))
        
        # Create SMS records in batch
        sms_values = [{
            'number': number,
            'body': body,
        } for number in numbers]
        sms_records = self.create(sms_values)
        
        # Send the SMS
        try:
            sender = provider._sanitize_sender_name(self.env.company.name)
            base_url = provider._get_gatewayapi_base_url(account)
            endpoint = f"{base_url}/mobile/single"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Token {account.gatewayapi_token}'
            }
            
            for record in sms_records:
                recipient = record.number
                if not recipient:
                    record.write({
                        'state': 'error', 
                        'error_code': 'invalid_recipient'
                    })
                    continue

                message_data = {
                    "sender": sender,
                    "message": record.body,
                    "recipient": int(recipient.replace('+', '')),
                    "priority": "normal",
                    "expiration": "P5D",  # Default 5 days expiration
                    "reference": str(record.id)  # Use record ID as reference
                }

                _logger.info(f"Sending SMS to GatewayAPI: {endpoint}")
                response = requests.post(endpoint, headers=headers, json=message_data)
                response_data = response.json()

                if response.status_code != 200:  # API spec defines 200 as success
                    error_message = response_data.get('detail', 'Unknown error')
                    _logger.error(f"GatewayAPI error: {error_message}")
                    record.write({
                        'state': 'error', 
                        'error_code': error_message
                    })
                else:
                    record.write({
                        'state': 'sent', 
                        'error_code': False,
                        'gateway_id': response_data.get('msg_id')
                    })
                    _logger.info(f"SMS sent successfully: {response_data}")
        except Exception as e:
            _logger.error(f"Error sending SMS through GatewayAPI: {e}")
            sms_records.write({
                'state': 'error', 
                'error_code': str(e)
            })
        
        return True
