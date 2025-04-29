{
    'name': 'GatewayAPI Connector',
    'version': '17.0.1.0.0',
    'category': 'SMS',
    'summary': 'Send SMS through GatewayAPI',
    'author': 'Custom',
    'website': 'https://gatewayapi.com',
    'license': 'AGPL-3',
    'depends': ['sms', 'iap'],
    'data': [
        'security/ir.model.access.csv',
        'views/iap_account_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
