# INSTALLATION & CONFIGURATION GUIDE

## 1. Requirements
- Odoo 17.0
- Python packages: `requests`, `pyjwt`
- A GatewayAPI account and API token

## 2. Installation

### a. Install Python dependencies
```
pip install -r requirements.txt
```

### b. Add the module to your Odoo addons path
- Clone or copy the `gatewayapi_connector` directory into your Odoo addons directory:
  ```bash
  cd /path/to/odoo/addons
  git clone https://github.com/yourusername/gatewayapi_connector.git
  ```

### c. Update Odoo app list and install the module
- Go to the Odoo Apps menu
- Click "Update Apps List"
- Search for "GatewayAPI Connector"
- Click "Install"

## 3. Configuration

### a. Create or edit an IAP Account
- Go to **Settings → Technical → IAP → IAP Accounts**
- Click "Create" or edit an existing account
- Set **Provider Type** to `GatewayAPI`
- Select the platform (EU or Global)
- Enter your API token
- Enter your Sender Name (see rules below)
- Click the **Test Connection** button to verify connectivity

### b. Sender Name Rules
- Alphanumeric: Up to 11 characters (A-Z, a-z, 0-9)
- Numeric: Up to 15 digits
- See: https://gatewayapi.com/docs/limitations/#sms-sender

### c. Webhook Setup (for delivery status updates)
- Set up a webhook in your GatewayAPI dashboard pointing to:
  ```
  https://<your-odoo-domain>/gatewayapi/webhook
  ```
- The webhook must include a JWT in the Authorization header, generated with the same secret as set in Odoo system parameters (`gatewayapi_webhook_jwt_secret`).
- See the README for a JWT generation example.

## 4. Usage
- All SMS sent via Odoo will now use GatewayAPI if the IAP account is configured as above.
- Message statuses will be updated automatically if the webhook is configured.

## 5. Troubleshooting
- If the Test Connection fails, check your API token and platform selection.
- Ensure your sender name meets GatewayAPI's requirements.
- Check Odoo logs for detailed error messages.
- For webhook issues, ensure the JWT secret matches and the endpoint is reachable from GatewayAPI.

---
For more details, see the README.md file. 