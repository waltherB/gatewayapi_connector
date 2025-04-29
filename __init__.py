from . import models
from . import controllers

gatewayapi_base_url = fields.Selection([
    ('eu', 'EU Platform (gatewayapi.eu)'),
    ('global', 'Global Platform (gatewayapi.com)')
], string='GatewayAPI Platform', default='eu', required=True)
