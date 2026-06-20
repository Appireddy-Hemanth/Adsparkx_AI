import time
import asyncio
from collections import deque
from datetime import datetime, timezone
import google.generativeai as genai
from src.utils.logger import logger

class RateLimitedGeminiClient:
    RPM_LIMITS = {
        "gemini-2.5-flash": 10,
        "gemini-2.5-flash-lite": 15,
        "models/text-embedding-004": 1500,
        "models/gemini-embedding-2": 1500,
    }
    MAX_RETRIES = 4
    BASE_BACKOFF = 1.0

    # Global shared state across client instances for accurate tracking
    _shared_timestamps = {}
    _shared_daily_counts = {}

    def __init__(self, model_name: str, api_key: str):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # Initialize shared deque for this model if not exists
        if model_name not in RateLimitedGeminiClient._shared_timestamps:
            RateLimitedGeminiClient._shared_timestamps[model_name] = deque()
        if model_name not in RateLimitedGeminiClient._shared_daily_counts:
            RateLimitedGeminiClient._shared_daily_counts[model_name] = 0

        self._day_start = datetime.now(timezone.utc).date()

    @property
    def _request_timestamps(self):
        return RateLimitedGeminiClient._shared_timestamps[self.model_name]

    @property
    def _daily_count(self):
        # Reset count if the day has changed (midnight UTC/Pacific, here we reset on day change in UTC)
        now_date = datetime.now(timezone.utc).date()
        if now_date != self._day_start:
            RateLimitedGeminiClient._shared_daily_counts[self.model_name] = 0
            self._day_start = now_date
        return RateLimitedGeminiClient._shared_daily_counts[self.model_name]

    @_daily_count.setter
    def _daily_count(self, value):
        RateLimitedGeminiClient._shared_daily_counts[self.model_name] = value

    def _enforce_rpm(self):
        now = time.time()
        window = 60.0
        rpm_limit = self.RPM_LIMITS.get(self.model_name, 10)
        
        # Remove timestamps older than 60s
        while self._request_timestamps and now - self._request_timestamps[0] > window:
            self._request_timestamps.popleft()
            
        if len(self._request_timestamps) >= rpm_limit:
            sleep_time = window - (now - self._request_timestamps[0]) + 0.1
            if sleep_time > 0:
                logger.warning(f"[RATE LIMIT] RPM limit hit for {self.model_name}. Sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
                # Recalculate now after sleeping
                now = time.time()
                while self._request_timestamps and now - self._request_timestamps[0] > window:
                    self._request_timestamps.popleft()

        self._request_timestamps.append(time.time())

    def generate(self, prompt: str, **kwargs) -> str:
        # Check daily limit (e.g. 1500 calls max on free tier per day)
        if self._daily_count >= 1500:
            raise RuntimeError(
                "Gemini API daily quota exhausted. Resets at midnight Pacific Time. "
                "Consider upgrading to Tier 1 for 1,000 RPD / 150 RPM."
            )

        for attempt in range(self.MAX_RETRIES):
            try:
                self._enforce_rpm()
                response = self.model.generate_content(prompt, **kwargs)
                self._daily_count += 1
                return response.text
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                    backoff = self.BASE_BACKOFF * (2 ** attempt)
                    logger.warning(f"[429] Rate limited. Retry {attempt+1}/{self.MAX_RETRIES} in {backoff}s. Error: {e}")
                    time.sleep(backoff)
                    if attempt == self.MAX_RETRIES - 1:
                        raise RuntimeError(
                            "Gemini API daily quota exhausted. Resets at midnight Pacific Time. "
                            "Consider upgrading to Tier 1 for 1,000 RPD / 150 RPM."
                        ) from e
                else:
                    raise
