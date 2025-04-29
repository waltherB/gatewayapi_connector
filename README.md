# GatewayAPI Connector for Odoo

This module integrates GatewayAPI's SMS service with Odoo, allowing you to send SMS messages directly from your Odoo instance using GatewayAPI's reliable messaging platform.

## Features

- Send SMS messages through GatewayAPI's platform
- Support for both EU and Global platforms (messaging.gatewayapi.eu and messaging.gatewayapi.com)
- Batch SMS sending capability
- Customizable sender names
- Message status tracking
- Integration with Odoo's SMS framework
- IAP (In-App Purchase) account management

## Requirements

- Odoo 17.0 or later
- A GatewayAPI account with valid API token
- Python 3.7 or later
- Required Python packages:
  - requests

## Installation

1. Clone this repository into your Odoo addons directory:
   ```bash
   cd /path/to/odoo/addons
   git clone https://github.com/yourusername/gatewayapi_connector.git
   ```

2. Update your Odoo addons list and install the module:
   - Go to the Apps menu in Odoo
   - Click "Update Apps List"
   - Search for "GatewayAPI Connector"
   - Click Install

## Configuration

### 1. GatewayAPI Account Setup

1. Sign up for a GatewayAPI account at [GatewayAPI](https://gatewayapi.com/)
2. Generate an API token from your GatewayAPI dashboard
3. Note down your API token for later use

### 2. Module Configuration

1. Go to Settings → Technical → SMS → IAP Accounts
2. Create or edit an IAP Account and select "GatewayAPI" as the provider type
3. Enter your GatewayAPI token
4. Select your preferred platform:
   - Global (gatewayapi.com)
   - EU (gatewayapi.eu)
5. Save the account

### 3. Testing the Integration

1. Go to Settings → Technical → SMS → Send SMS
2. Create a new SMS message
3. Enter the recipient's phone number
4. Write your message
5. Click Send to test the integration

## Usage

### Sending Individual SMS

1. Navigate to any record with SMS functionality
2. Click on the SMS button
3. Enter your message
4. Click Send

### Sending Batch SMS

1. Go to Settings → Technical → SMS → Send SMS
2. Create a new SMS message
3. Add multiple recipients
4. Write your message
5. Click Send to dispatch to all recipients

## Technical Details

- Success Response Code: 200
- Sender Name Limitations:
  - Alphanumeric: Up to 11 characters
  - Numeric: Up to 15 digits
  - Full UTF-8: Up to 11 characters
- Message Expiration: 5 days by default
- Priority: Normal (default)

## Troubleshooting

Common issues and solutions:

1. **Invalid Token Error**
   - Verify your API token in the IAP account settings
   - Ensure the token has the necessary permissions

2. **Invalid Sender Name**
   - Check that your sender name follows the length limitations
   - Use only allowed characters

3. **Message Not Sent**
   - Check your internet connection
   - Verify recipient number format (should include country code)
   - Check Odoo logs for detailed error messages

## Support

For support:
1. Check the [GatewayAPI Documentation](https://gatewayapi.com/docs/)
2. Submit issues on the GitHub repository
3. Contact your Odoo support team

## License

This module is licensed under LGPL-3.

## Contributors

- Your organization/name
- Community contributors

## Changelog

### 1.0.0
- Initial release
- Basic SMS sending functionality
- EU/Global platform support
- IAP integration
