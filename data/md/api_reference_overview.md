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