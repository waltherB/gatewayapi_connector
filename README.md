# GatewayAPI Connector for Odoo 17

This module replaces Odoo's SMS IAP with GatewayAPI, using their REST API. It allows you to send SMS messages via GatewayAPI, select the EU or Global platform, configure the sender name, and test connectivity directly from the IAP Account form.

## Features
- Full replacement for Odoo's SMS IAP
- Supports GatewayAPI EU and Global platforms
- Sender name configuration with validation (per GatewayAPI rules)
- Test Connection button in the IAP Account form
- Handles all GatewayAPI status types
- Odoo 17-compliant UI and code

## Requirements
- Odoo 17.0
- Python package: `requests`
- A GatewayAPI account and API token

## Installation
1. Clone this repository into your Odoo addons directory:
   ```bash
   cd /path/to/odoo/addons
   git clone https://github.com/yourusername/gatewayapi_connector.git
   ```
2. Update your Odoo apps list and install the module via the Apps menu.

## Configuration
1. Go to Settings → Technical → IAP → IAP Accounts
2. Create or edit an IAP Account
3. Set Provider Type to "GatewayAPI"
4. Select the platform (EU or Global)
5. Enter your API token
6. Enter your Sender Name (see rules below)
7. Click the "Test Connection" button to verify connectivity

### Sender Name Rules
- Alphanumeric: Up to 11 characters (A-Z, a-z, 0-9)
- Numeric: Up to 15 digits
- See: https://gatewayapi.com/docs/limitations/#sms-sender

## Usage
- When sending SMS via Odoo, messages will be routed through GatewayAPI using your configuration.
- All message statuses from GatewayAPI are handled and mapped to Odoo's SMS status system.

## Troubleshooting
- If the Test Connection fails, check your API token and platform selection.
- Ensure your sender name meets GatewayAPI's requirements.
- Check Odoo logs for detailed error messages.

## License
This module is licensed under AGPL-3.

## Webhook JWT Authentication Example

When configuring the webhook in GatewayAPI, you must include a JWT in the Authorization header. This JWT token should be created during the webhook configuration on the GatewayAPI side, using the same shared secret that you set in Odoo (system parameter `gatewayapi_webhook_jwt_secret`).

```
Authorization: Bearer <your_jwt_token>
```

Here is an example of how to generate a JWT in Python using the `pyjwt` library (for use in GatewayAPI webhook configuration):

```python
import jwt
import datetime

# Use the same secret as set in Odoo system parameters (gatewayapi_webhook_jwt_secret)
secret = 'your_shared_secret_here'

payload = {
    'iat': int(datetime.datetime.utcnow().timestamp()),
    'iss': 'gatewayapi',
    # You can add more claims as needed
}

jwt_token = jwt.encode(payload, secret, algorithm='HS256')
print(jwt_token)
```

Include the resulting token in the Authorization header when calling the webhook endpoint.
