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
        provider = self.env['gatewayapi.provider'].search([], limit=1)
        if not provider:
            return super()._send_sms(body, numbers)
            
        account = provider._get_gatewayapi_account()
        if not account or not account.gatewayapi_token:
            raise UserError(_("No valid GatewayAPI account found. Please configure one."))
        
        sms_records = []
        for number in numbers:
            sms = self.create({
                'number': number,
                'body': body,
            })
            sms_records.append(sms)
        
        # Send the SMS
        try:
            for record in sms_records:
                sender = provider._sanitize_sender_name(self.env.company.name)
                recipient = record.number
                message = record.body

                if not recipient:
                    record.write({'state': 'error', 'error_code': 'invalid_recipient'})
                    continue

                message_data = {
                    "message": message,
                    "recipients": [{"msisdn": int(recipient.replace('+', ''))}],
                    "sender": sender
                }

                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {account.gatewayapi_token}'
                }

                endpoint = provider._get_gatewayapi_endpoint(account)
                _logger.info(f"Sending SMS to GatewayAPI: {endpoint}")

                response = requests.post(endpoint, headers=headers, json=message_data)
                response_data = response.json()

                if response.status_code != 200:
                    error_message = response_data.get('message', 'Unknown error')
                    _logger.error(f"GatewayAPI error: {error_message}")
                    record.write({'state': 'error', 'error_code': error_message})
                else:
                    record.write({
                        'state': 'sent', 
                        'error_code': False,
                        'gateway_id': response_data.get('ids', [''])[0]
                    })
                    _logger.info(f"SMS sent successfully: {response_data}")
        except Exception as e:
            _logger.error(f"Error sending SMS through GatewayAPI: {e}")
            for record in sms_records:
                record.write({'state': 'error', 'error_code': str(e)})
        
        return True
