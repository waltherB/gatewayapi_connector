{
    'name': 'GatewayAPI Connector',
    'version': '17.0.1.0.0',
    'category': 'SMS',
    'summary': 'Send SMS through GatewayAPI',
    'author': 'Custom',
    'website': 'https://gatewayapi.com',
    'license': 'AGPL-3',
    'depends': ['sms', 'iap'],  # Keep the IAP dependency
    'data': [
        'views/iap_account_views.xml',
        'views/sms_provider_views.xml',
        'data/sms_provider_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
