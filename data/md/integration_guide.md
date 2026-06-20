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