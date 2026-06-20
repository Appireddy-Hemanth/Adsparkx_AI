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