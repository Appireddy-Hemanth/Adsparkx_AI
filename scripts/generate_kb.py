import os
from fpdf import FPDF

# Ensure output directories exist
os.makedirs("data/pdf", exist_ok=True)
os.makedirs("data/txt", exist_ok=True)
os.makedirs("data/md", exist_ok=True)

# 1. novasuite_sla_policy.pdf
sla_text = """
NovaSuite Service Level Agreement (SLA) Policy
Effective Date: June 2026

1. Overview
This Service Level Agreement ("SLA") defines the core performance and availability standards for NovaSuite's cloud platform. NovaSuite is committed to providing a reliable, enterprise-grade software-as-a-service (SaaS) platform to all subscription tiers. This document details our service level targets, credit eligibility, and incident response procedures.

2. Uptime Commitment
NovaSuite guarantees a Monthly Uptime Percentage of at least 99.9% for all production environments. "Monthly Uptime Percentage" is calculated by subtracting from 100% the percentage of minutes during the month in which the platform was in a state of "Unscheduled Downtime".
Unscheduled Downtime is defined as any period where the NovaSuite API or core web application is completely inaccessible or unresponsive to requests, excluding:
- Planned Maintenance windows (announced at least 48 hours in advance)
- Force Majeure events (natural disasters, regional network outages, etc.)
- Outages caused by client integrations or custom configurations
- Issues with third-party networks or client internet service provider failures.

3. SLA Credit Policy
If NovaSuite fails to meet the 99.9% uptime guarantee in a given calendar month, clients are eligible to request service credits applied against their next billing cycle. Service credits are calculated as a percentage of the total monthly subscription fee paid by the client:
- Uptime < 99.9% but >= 99.5%: 10% credit of the monthly fee.
- Uptime < 99.5% but >= 99.0%: 25% credit of the monthly fee.
- Uptime < 99.0%: 50% credit of the monthly fee.
To claim service credits, clients must submit a formal ticket to the billing department within thirty (30) days of the end of the month in which the outage occurred. Claims must include date, time, and logs demonstrating the downtime.

4. Incident Response Timelines
NovaSuite classifies platform incidents into four severity levels to prioritize engineering resources and communicate status update reports:
- Severity 1 (P1) - Critical: Core system is completely down, affecting all users. Response target: under 15 minutes. Update frequency: every 30 minutes. Resolution target: 4 hours.
- Severity 2 (P2) - High: Key features are unavailable with no workaround. Response target: under 30 minutes. Update frequency: every 2 hours. Resolution target: 8 hours.
- Severity 3 (P3) - Medium: Minor bugs or performance degradation with a workaround. Response target: under 4 hours. Update frequency: daily. Resolution target: 3 business days.
- Severity 4 (P4) - Low: General questions or cosmetic issues. Response target: under 24 hours. Update frequency: as needed.

Our dedicated Site Reliability Engineering (SRE) team is on-call 24/7/365 to handle P1 incidents. Escalation procedures are automatically triggered when monitoring tools detect an outage.
"""

def generate_sla_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text=sla_text.strip())
    pdf.output("data/pdf/novasuite_sla_policy.pdf")
    print("Generated data/pdf/novasuite_sla_policy.pdf")

# Other files data dictionary
files_data = {
    # 2. password_reset_guide.txt
    "data/txt/password_reset_guide.txt": """
NovaSuite Password Reset & MFA Recovery Guide

1. Standard Password Reset Process
If you have forgotten your password or are locked out of your NovaSuite account, follow these standard recovery steps:
- Navigate to the NovaSuite login page (https://app.novasuite.com/login).
- Click on the "Forgot Password?" link located just below the login form.
- Enter the email address associated with your NovaSuite account and click "Send Reset Link".
- Check your email inbox for an email from "no-reply@novasuite.com" with the subject "Reset Your NovaSuite Password".
- Click the secure link inside the email. Note that this link is only valid for sixty (60) minutes from the time it was requested.
- Enter your new password, confirm it, and click "Update Password". Your new password must meet the following complexity requirements: minimum 12 characters, at least one uppercase letter, one lowercase letter, one number, and one special character (e.g., !, @, #, $, %).

2. MFA Recovery Process
If you have Multi-Factor Authentication (MFA) enabled and cannot access your authenticator app, you must use your backup recovery codes:
- During the MFA prompt on login, click "Use Backup Recovery Code".
- Enter one of the 8-digit recovery codes generated when you first set up MFA. Note that each recovery code can only be used once.
- Once logged in, go to Security Settings and reset your MFA configuration.
- If you have lost your recovery codes, you must escalate this request to your organization's NovaSuite Administrator. Admin users can temporarily disable MFA for team members via the Admin Console under User Management.

3. Troubleshooting & Support Escalation
If you do not receive the password reset email:
- Verify that the email address entered is correct.
- Check your Spam/Junk folders.
- Ensure that your company's email server is not blocking emails from "novasuite.com".
- Wait 5 minutes as email delivery can sometimes be delayed.
If standard recovery fails, or if you are the sole Administrator and are locked out, contact the NovaSuite Security Support Team at security@novasuite.com.
""",

    # 3. api_authentication_errors.txt
    "data/txt/api_authentication_errors.txt": """
NovaSuite API Authentication & Authorization Error Guide

1. Overview
All requests to the NovaSuite REST API must be authenticated using a valid Bearer Token in the HTTP Authorization header. Authentication failures will result in HTTP 401 or 403 error status codes. Understanding these errors is critical for integration developers.

2. HTTP 401 Unauthorized Errors
A 401 error indicates that the request lacked valid credentials. This usually occurs under the following circumstances:
- Missing Header: The HTTP Authorization header was not sent with the request.
- Invalid Format: The header was sent but did not use the "Bearer <token>" format.
- Expired Token: The JWT token has expired. Access tokens are valid for exactly 60 minutes.
- Revoked Token: The API key or token has been revoked by an administrator or due to a security rotation event.
To resolve a 401 error:
- Verify that your token is actively copied and formatted correctly.
- Implement token refresh logic in your code. When a 401 is received, use your OAuth2 refresh token to request a new access token from the `/oauth/token` endpoint.

3. HTTP 403 Forbidden Errors
A 403 error indicates that the token is valid, but the authenticated user or application does not have permission to access the requested resource. Common causes:
- Insufficient Scopes: The token was generated with limited scopes (e.g., `read:users`) but the request tried to perform a write operation (e.g., `POST /api/users`).
- Role-Based Access Control (RBAC): The user's role in NovaSuite (e.g., Member) does not allow access to admin-only API endpoints (e.g., `/api/billing`).
- IP Restriction: The organization has enabled IP Whitelisting, and the request originated from an unauthorized IP address.
To resolve a 403 error, check the JSON response body. It will detail the missing scope or role required.

4. HTTP 429 Too Many Requests
NovaSuite enforces rate limits to ensure platform stability. If you exceed the rate limits (detailed in rate_limiting_policy.md), the API will return a 429 error. Your client must inspect the `Retry-After` header to know how many seconds to wait before retrying the request.
""",

    # 4. billing_faq.txt
    "data/txt/billing_faq.txt": """
NovaSuite Billing & Subscription FAQ

1. Invoice Cycles & Payment Methods
NovaSuite charges customers on a recurring monthly or annual basis, depending on the plan selected during signup.
- Billing Cycle: Monthly subscriptions are billed on the same calendar day each month (e.g., if you signed up on the 15th, you are billed on the 15th). Annual plans are billed on the anniversary of the signup date.
- Payment Methods: We accept major credit cards (Visa, Mastercard, American Express), PayPal, and wire transfers for enterprise clients.
- Invoices: All invoices are sent to the billing email address configured in the Subscription settings and can also be downloaded as PDF files directly from the billing section of the Admin Dashboard.

2. Refund Policy
NovaSuite offers a 14-day money-back guarantee for all new subscriptions.
- Monthly Subscriptions: Requests for refunds must be made within 14 days of the initial subscription purchase. Subsequent monthly renewals are non-refundable.
- Annual Subscriptions: Requests for refunds must be made within 14 days of the initial purchase or renewal date.
- Processing Refunds: Approved refunds will be credited back to the original payment method within 5 to 10 business days.
- Disputes: If you believe you were charged in error, please contact billing@novasuite.com before filing a charge dispute with your credit card company. Filing a dispute or chargeback will result in the immediate suspension of your NovaSuite account.

3. Plan Upgrades & Downgrades
You can change your plan at any time through the Admin Console:
- Upgrades: Upgrading to a higher plan takes effect immediately. The billing system will calculate a pro-rated charge for the remainder of the current billing cycle.
- Downgrades: Downgrades take effect at the end of the current billing cycle. No pro-rated refunds are given for downgrades.
- Seat Management: Adding seats to your team plan will incur immediate pro-rated charges for the current billing cycle. Removing seats takes effect at the next renewal date.
""",

    # 5. account_lock_troubleshooting.txt
    "data/txt/account_lock_troubleshooting.txt": """
NovaSuite Account Lockout Troubleshooting Guide

1. Why is My Account Locked?
NovaSuite employs strict security measures to protect user data from unauthorized access. An account lockout is typically triggered by:
- Brute-Force Protection: Five (5) consecutive failed login attempts within a 15-minute window. This automatically locks the account to prevent password guessing attacks.
- Administrative Lock: A NovaSuite Administrator in your organization has manually locked your account via the Admin Dashboard.
- Compliance/Security Review: NovaSuite Security has locked the account due to suspicious activity, such as logins from geographically impossible locations within a short timeframe.

2. Unlock Procedures
Depending on the cause of the lock, follow these resolution steps:
- Temporary Lock (Brute-Force): This lock lasts for exactly thirty (30) minutes. You can wait for the lockout timer to expire and try logging in again with the correct password.
- Reset Password: If you cannot remember your password, you can trigger a password reset by clicking "Forgot Password" on the login page. A successful password reset will automatically clear the brute-force lockout status.
- Admin Unlock: If your account has been administratively locked, you must contact your organization's NovaSuite Administrator. The admin can unlock your account by navigating to User Management, selecting your user profile, and clicking "Unlock Account".
- Security Lock: If your account was locked by NovaSuite Security, you must open a ticket with support@novasuite.com and verify your identity before the account can be re-activated.

3. Best Practices to Avoid Lockout
- Use a password manager to avoid typing incorrect passwords.
- Verify that your caps-lock key is off before logging in.
- If you change your password, update it immediately in all automated scripts, browser autofills, and API clients to avoid rapid failed login attempts.
""",

    # 6. getting_started.md
    "data/md/getting_started.md": """
# Getting Started with NovaSuite

Welcome to NovaSuite! This guide will walk you through the initial setup of your workspace so you and your team can start collaborating effectively.

## 1. Step 1: Account Activation
When your organization creates your account, you will receive an activation email from "welcome@novasuite.com".
- Click the **Activate Account** link in the email.
- Set a secure password (at least 12 characters, uppercase, lowercase, numbers, special characters).
- Set up Multi-Factor Authentication (MFA) as described in the security prompts.

## 2. Step 2: First Time Login
Once activated, log in to NovaSuite at https://app.novasuite.com.
- Enter your email and password.
- Enter the 6-digit MFA code from your authenticator app.
- You will be greeted by the NovaSuite Setup Wizard.

## 3. Step 3: Workspace Setup
A workspace is where your projects, files, and integrations live.
- **Name Your Workspace**: Choose a name that represents your team or department (e.g., "Marketing Team" or "DevOps").
- **Invite Team Members**: Go to Workspace Settings -> Members. Click "Invite Member", enter their email address, and select their role:
  - *Owner*: Full billing and administrative access.
  - *Admin*: User management, integrations, and project setup.
  - *Member*: Can create and view projects, but cannot manage billing or user permissions.
  - *Guest*: Restricted access to specific projects only.
- **Configure Integrations**: If you use Slack or Zapier, connect them now to receive notifications.

## 4. Troubleshooting Initial Setup
If you run into issues during activation:
- Ensure your browser is updated to the latest version (Chrome, Firefox, Safari, and Edge are fully supported).
- Clear browser cookies and cache if the activation link does not load.
- For issues with organization setups, contact your IT administrator.
""",

    # 7. integration_guide.md
    "data/md/integration_guide.md": """
# NovaSuite Integration Guide

NovaSuite supports native connections and OAuth integrations with third-party tools like Slack, Zapier, and Salesforce to streamline your workflow.

## 1. Slack Integration
The Slack integration allows NovaSuite to send real-time notifications to Slack channels.
- Go to **Integrations** in the Admin Console.
- Click **Connect** next to Slack.
- Authorize the NovaSuite Slack App to access your Slack workspace.
- Choose which channels receive notifications for platform alerts, invoice updates, or task assignments.
- To disconnect, click **Configure** and choose "Uninstall Slack Integration".

## 2. Zapier Connector
With Zapier, you can trigger workflows in thousands of apps when events happen in NovaSuite.
- Go to Zapier.com and log in.
- Create a new Zap and select "NovaSuite" as the Trigger App.
- Authenticate using your NovaSuite API Key (generated in your profile under API Keys).
- Select a trigger event (e.g., "New Task Created", "Invoice Issued").
- Set up the action app in Zapier.

## 3. Salesforce Connector
Our Salesforce integration is available on Enterprise plans and syncs customer contact details.
- Navigate to Integrations -> Salesforce.
- Click **Enable Salesforce Sync**.
- Log in to your Salesforce sandbox or production environment.
- Map NovaSuite custom fields to Salesforce Lead or Contact fields.
- Enable automatic bi-directional sync or manual sync.

## 4. OAuth Configuration for Custom Apps
If you are building a custom application, you can configure NovaSuite as an OAuth2 provider:
- Go to Developer Settings -> OAuth Applications.
- Click **Register New Application**.
- Enter your Application Name and Redirect URI.
- Save the client ID and client secret safely. Use the authorization code flow to obtain user tokens.
""",

    # 8. troubleshooting_connectivity.md
    "data/md/troubleshooting_connectivity.md": """
# Troubleshooting Network Connectivity Issues

This document helps troubleshoot connectivity issues between your local network or application servers and the NovaSuite platform.

## 1. Diagnostic Steps
If you receive timeout errors or fail to connect to `api.novasuite.com`, follow these troubleshooting steps:
- **Ping Test**: Run `ping api.novasuite.com` in your terminal. Verify that DNS resolves to our active IP addresses.
- **Traceroute**: Run `traceroute api.novasuite.com` (macOS/Linux) or `tracert api.novasuite.com` (Windows) to identify where network packets are being dropped.
- **Port Check**: NovaSuite only accepts HTTPS traffic on port 443. Test connectivity to port 443 using telnet or nc:
  `nc -zv api.novasuite.com 443`

## 2. Firewall and Proxy Configuration
If your company uses a strict corporate firewall or proxy server, you may need to whitelist NovaSuite domains:
- Whitelist the following domains:
  - `*.novasuite.com`
  - `api.novasuite.com`
  - `cdn.novasuite.com`
- If your firewall requires static IP whitelisting, contact Enterprise Support at network-ops@novasuite.com to request our current IP address range. Note that we recommend whitelisting by domain name as IPs may change during maintenance.

## 3. SSL/TLS Certificate Issues
If you encounter SSL handshake failures or untrusted certificate warnings:
- Ensure your local operating system or programming environment has the latest root certificate authorities (CA) installed. NovaSuite certificates are signed by Let's Encrypt.
- Verify that your local clock is synchronized. Significant clock drift (more than 5 minutes) will cause SSL verification to fail.
- Do not bypass SSL validation in production scripts as this exposes your data to Man-in-the-Middle (MITM) attacks.
""",

    # 9. data_export_guide.md
    "data/md/data_export_guide.md": """
# NovaSuite Data Export & GDPR Compliance Guide

NovaSuite supports full data portability. You can export your data at any time in industry-standard formats.

## 1. Exporting Data via User Interface
To export workspace data through the Admin Console:
- Navigate to **Workspace Settings** -> **Data Administration**.
- Choose the data types to export (e.g., Tasks, Messages, Users, Billing History).
- Select the export format: **CSV** or **JSON**.
- Click **Generate Export**. Depending on the size of your workspace, this may take up to 30 minutes.
- You will receive an email containing a link to download a secure, password-protected ZIP archive of your data. The download link will expire after 48 hours.

## 2. Programmatic Export via API
For automated backups, utilize our REST API endpoints:
- Use `GET /api/v1/export` to initiate an export.
- Implement pagination to fetch large datasets. Use `limit` and `starting_after` query parameters:
  `GET /api/v1/tasks?limit=100&starting_after=task_099`
- The API returns a cursor-based pagination scheme. Always read the `has_more` boolean in the response metadata.

## 3. GDPR Data Deletion (Right to Be Forgotten)
Under GDPR regulations, clients have the right to request deletion of personal data:
- Admin users can permanently delete team member profiles via User Management -> Delete User.
- To request a complete deletion of all organization data, the Workspace Owner must submit a ticket to gdpr@novasuite.com.
- Data deletion requests are processed within 14 business days. Note that backup archives may retain data for up to 90 days before it is fully overwritten. Some invoice data must be kept for financial compliance.
""",

    # 10. mfa_setup_guide.md
    "data/md/mfa_setup_guide.md": """
# Multi-Factor Authentication (MFA) Setup Guide

Multi-Factor Authentication (MFA) adds an extra layer of security to your NovaSuite account by requiring a second verification step during login.

## 1. How to Enable MFA
We highly recommend that all users enable MFA. To configure it:
- Log in to your NovaSuite account.
- Click on your profile picture in the top-right corner and select **Security Settings**.
- Click the **Enable MFA** button.
- Scan the QR code displayed on the screen using your preferred authenticator app (such as Google Authenticator, Microsoft Authenticator, Authy, or Duo).
- Enter the 6-digit verification code generated by the app to confirm setup.
- **Save Backup Recovery Codes**: Write down or print the provided recovery codes and store them in a secure place. These codes are required if you lose access to your phone.

## 2. Using Hardware Security Keys
For enterprise security, NovaSuite supports hardware keys (such as YubiKeys) using the WebAuthn standard:
- In Security Settings, click **Add Security Key**.
- Insert your hardware key into a USB port or hold it near your NFC reader.
- Touch the button on the key when prompted by your browser.
- Name the key and save the configuration.

## 3. MFA Enforcement Policy
Workspace Owners can require MFA for all users in the organization:
- Go to Workspace Settings -> Security Policy.
- Toggle **Enforce MFA for all organization members**.
- Once enabled, members who do not have MFA set up will be prompted to configure it on their next login and will be unable to access workspace features until setup is complete.
""",

    # 11. rate_limiting_policy.md
    "data/md/rate_limiting_policy.md": """
# NovaSuite API Rate Limiting Policy

To ensure equitable distribution of platform resources and prevent abuse, NovaSuite enforces API rate limits on all endpoints.

## 1. Rate Limit Quotas by Subscription Plan
Rate limits are calculated on a rolling-window basis based on the subscription tier of your workspace:
- **Starter Plan**: 60 requests per minute (RPM), 5,000 requests per day (RPD).
- **Professional Plan**: 300 requests per minute (RPM), 50,000 requests per day (RPD).
- **Enterprise Plan**: 1,200 requests per minute (RPM), 500,000 requests per day (RPD).

## 2. API Headers
Every response returned by the NovaSuite API contains headers indicating your current rate limit status:
- `X-RateLimit-Limit`: The maximum number of requests allowed in the current window.
- `X-RateLimit-Remaining`: The number of requests remaining in the current window.
- `X-RateLimit-Reset`: The Unix epoch timestamp indicating when the current rate limit window resets.

## 3. Handling 429 Errors
If you exceed your rate limit quota, the API will reject requests and return an HTTP **429 Too Many Requests** status code.
- Your application must inspect the `Retry-After` header, which specifies the number of seconds to wait before making another request.
- **Exponential Backoff**: When designing integrations, implement exponential backoff retry logic. If a request fails, wait 1 second, then 2 seconds, then 4 seconds before retrying.
- **Caching**: Cache static resources locally (such as user profiles or settings) to reduce the number of API calls.
""",

    # 12. webhook_configuration.md
    "data/md/webhook_configuration.md": """
# Webhook Configuration & Validation Guide

Webhooks allow NovaSuite to send real-time HTTP POST notifications to your server when events happen within your workspace.

## 1. Configuring a Webhook Endpoint
To set up a webhook:
- Go to Admin Console -> Developer Settings -> Webhooks.
- Click **Add Endpoint**.
- Enter your Destination URL (must begin with `https://`).
- Select the events you want to listen to (e.g., `invoice.paid`, `user.created`, `task.completed`).
- Save the configuration. You will be provided with a **Signing Secret** (starting with `whsec_`).

## 2. Verifying Webhook Signatures
To prevent spoofing attacks, you must verify that webhook requests originate from NovaSuite.
- NovaSuite includes a signature in the `X-NovaSuite-Signature` header of every webhook POST request.
- The signature is generated using Hash-based Message Authentication Code (HMAC) with the SHA-256 algorithm, using your endpoint's Signing Secret as the key.
- To validate the request, compute the HMAC SHA-256 signature of the raw request payload (the request body as a raw string) and compare it to the signature in the header.
- Example code in Python:
  ```python
  import hmac
  import hashlib
  
  def verify_signature(payload, secret, header_sig):
      computed_sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
      return hmac.compare_digest(computed_sig, header_sig)
  ```

## 3. Retry Logic & Failures
If your server returns an HTTP status code outside the 2xx range (e.g., 500, 503, or connection timeout), NovaSuite will retry delivery:
- Retries are attempted up to 5 times over 24 hours using exponential backoff.
- If an endpoint fails consistently for 7 days, it will be automatically disabled, and an email will be sent to the administrator.
""",

    # 13. subscription_management.md
    "data/md/subscription_management.md": """
# NovaSuite Subscription & Account Management

Manage your team subscription tiers, invoice configurations, and account cancellations easily.

## 1. Changing Subscription Plans
You can upgrade or downgrade your plan at any time through the Admin Dashboard:
- **Upgrading**: Navigate to Subscription Management -> Pricing. Select the plan you wish to upgrade to. The new features will be unlocked immediately. The billing engine will calculate the pro-rated cost for the remaining days of your current billing cycle and charge the payment method on file.
- **Downgrading**: You can downgrade to a lower tier. The downgrade will not take effect until the end of your current pre-paid billing cycle. You will not receive a refund for the unused portion of the current cycle.

## 2. User Seat Allocation
Our Professional and Enterprise plans are billed per active seat:
- Adding Seats: You can invite new team members at any time. If you exceed your current seat allocation, the system will add seats automatically and charge a pro-rated fee.
- Removing Seats: To lower your bill, deactivate users in User Management. Then, go to Subscription settings and reduce the number of seats on your plan.

## 3. Cancellation Policy
We are sorry to see you go. If you decide to cancel your subscription:
- Navigate to Subscription Management -> Billing Details.
- Click **Cancel Subscription** at the bottom of the page.
- Complete the short exit survey.
- Your subscription will remain active until the end of your current billing period. After this, your account will be downgraded to the Free Read-Only archive tier. Data is kept for 180 days before permanent deletion.
""",

    # 14. api_reference_overview.md
    "data/md/api_reference_overview.md": """
# NovaSuite API Reference Overview

Welcome to the REST API reference documentation for the NovaSuite SaaS platform.

## 1. Base URL
All API requests must be sent to the following base URL:
`https://api.novasuite.com/v1`

## 2. API Versioning & Deprecation
NovaSuite versions its API using path versioning (e.g., `/v1`).
- We guarantee backward compatibility for at least 12 months after a version is deprecated.
- When an API endpoint is deprecated, we will send warning messages in the HTTP response headers:
  - `Warning: 299 - "Deprecation Notice: This version will be retired on YYYY-MM-DD."`
- Deprecated endpoints are logged, and workspace administrators will receive periodic email notifications.

## 3. Core Resource Endpoints
- **Users**: `/users` - Create, retrieve, update, and delete workspace users.
- **Projects**: `/projects` - Organize tasks and collaboration resources.
- **Tasks**: `/tasks` - Manage workflows, statuses, assignees, and deadlines.
- **Invoices**: `/billing/invoices` - Query billing history and payments.

## 4. Query Parameters & Response Format
All API responses are returned in JSON format.
- **Pagination**: Use `limit` (max 100) and `starting_after` (cursor ID) for listing resources.
- **Filtering**: Filter resources using exact match parameters (e.g., `/tasks?status=completed`).
- **Sorting**: Use `sort` parameter (e.g., `sort=created_at:desc`).
All requests must use HTTPS. Standard HTTP requests will be automatically redirected to HTTPS.
""",

    # 15. incident_response_playbook.md
    "data/md/incident_response_playbook.md": """
# NovaSuite Incident Response Playbook

This internal playbook details how NovaSuite engineers handle and resolve production outages.

## 1. Incident Detection & Triage
Production incidents are detected via automated monitoring (Datadog, Sentry, Pingdom) or customer escalation.
- Once an alert fires, the SRE on-call engineer is paged.
- The engineer performs triage to determine the incident severity (P1 to P4):
  - **P1**: Core system down, customer data loss risk, or security breach.
  - **P2**: Main features down for multiple clients (e.g., billing engine failing).
  - **P3**: Performance degradation or minor functionality issues.
  - **P4**: Minor bug with simple workaround.

## 2. Command Structure for P1 Incidents
When a P1 incident is declared:
- An **Incident Commander** is appointed to lead the resolution effort.
- A **Communications Lead** is appointed to update the public Status Page (https://status.novasuite.com) and notify customer support teams.
- Public updates must be posted within 15 minutes of declaration and updated every 30 minutes.

## 3. Communication Templates
- *Outage Declaration*: "We are currently experiencing a platform outage affecting user logins. Our engineering team is investigating the root cause. Next update in 30 minutes."
- *Resolution*: "The login issue has been resolved. The root cause was an expired database connection pool. All systems are operating normally. A full post-mortem will be published within 48 hours."

## 4. Post-Mortem and Review
Within 48 hours of any P1 incident, the Incident Commander must lead a blameless post-mortem meeting:
- Document the timeline of events.
- Identify the root cause.
- Create action items to prevent recurrence.
- Publish a customer-facing summary to enterprise clients.
"""
}

# Write text/md files
for filepath, content in files_data.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Generated {filepath}")

# Generate PDF
generate_sla_pdf()
print("All 15 KB documents generated successfully.")
