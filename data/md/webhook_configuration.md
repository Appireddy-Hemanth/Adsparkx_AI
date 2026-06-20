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