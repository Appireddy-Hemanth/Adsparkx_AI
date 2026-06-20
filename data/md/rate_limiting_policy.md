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