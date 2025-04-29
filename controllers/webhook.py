from odoo import http
from odoo.http import request
import logging
import jwt
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)


def _get_jwt_secret():
    # Fetch the secret from Odoo system parameters
    Param = request.env['ir.config_parameter'].sudo()
    return Param.get_param('gatewayapi_webhook_jwt_secret', default='')


def _validate_jwt(token):
    secret = _get_jwt_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except Exception as e:
        _logger.warning('JWT validation failed: %s', e)
        raise AccessDenied('Invalid JWT token')


class GatewayAPIWebhookController(http.Controller):
    @http.route(
        '/gatewayapi/webhook',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False
    )
    def gatewayapi_webhook(self, **post):
        # JWT authentication
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AccessDenied('Missing or invalid Authorization header')
        token = auth_header.split(' ', 1)[1]
        _validate_jwt(token)

        payload = request.jsonrequest
        _logger.info('Received GatewayAPI webhook: %s', payload)
        msg_id = payload.get('event', {}).get('msg_id')
        status = payload.get('event', {}).get('status')
        if not msg_id or not status:
            return {'error': 'Missing msg_id or status'}
        sms = request.env['sms.sms'].sudo().search([
            ('external_id', '=', msg_id)
        ], limit=1)
        if sms:
            sms.state = status
            _logger.info('Updated SMS %s to status %s', msg_id, status)
        return {'result': 'ok'} 