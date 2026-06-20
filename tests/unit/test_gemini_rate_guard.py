import pytest
import time
from unittest.mock import patch, MagicMock
from src.utils.gemini_client import RateLimitedGeminiClient

class TestGeminiRateGuard:

    def test_exponential_backoff_on_429(self):
        """Client retries with exponential back-off on rate limit errors."""
        client = RateLimitedGeminiClient("gemini-2.5-flash-lite", api_key="test")
        client._request_timestamps.clear()
        call_times = []
        
        def mock_generate(*args, **kwargs):
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("429 RESOURCE_EXHAUSTED")
            return MagicMock(text="Success")

        with patch.object(client.model, "generate_content", side_effect=mock_generate):
            with patch("time.sleep") as mock_sleep:  # Mock sleep so tests run instantly!
                result = client.generate("test prompt")
                assert result == "Success"
                assert len(call_times) == 3
                assert mock_sleep.call_count == 2
                # Verify sleep called with exponential times: 1.0, 2.0
                mock_sleep.assert_any_call(1.0)
                mock_sleep.assert_any_call(2.0)

    def test_rpm_limiter_enforces_window(self):
        """RPM limiter does not exceed 15 RPM for flash-lite."""
        client = RateLimitedGeminiClient("gemini-2.5-flash-lite", api_key="test")
        # Pre-fill the window with 15 timestamps from 2 seconds ago
        now = time.time()
        client._request_timestamps.clear()
        for _ in range(15):
            client._request_timestamps.append(now - 58) # 15 requests, 58s ago — still in window
            
        with patch.object(client.model, "generate_content", return_value=MagicMock(text="ok")):
            with patch("time.sleep") as mock_sleep:
                client.generate("test")
                assert mock_sleep.called
                # Sleep time should be roughly: window (60) - (now - oldest_timestamp (58)) = ~2.0 seconds + 0.1
                args, _ = mock_sleep.call_args
                assert args[0] >= 1.5

    def test_raises_on_quota_exhaustion_after_max_retries(self):
        """After MAX_RETRIES 429s, raises RuntimeError with helpful message."""
        client = RateLimitedGeminiClient("gemini-2.5-flash", api_key="test")
        with patch.object(client.model, "generate_content",
                          side_effect=Exception("429 RESOURCE_EXHAUSTED")):
            with patch("time.sleep"):
                with pytest.raises(RuntimeError, match="quota exhausted"):
                    client.generate("test")

    def test_daily_call_counter_increments(self):
        """Daily call counter increments on each successful call."""
        client = RateLimitedGeminiClient("gemini-2.5-flash-lite", api_key="test")
        # Reset counter for clean test environment
        client._daily_count = 0
        with patch.object(client.model, "generate_content", return_value=MagicMock(text="ok")):
            client.generate("test 1")
            client.generate("test 2")
            assert client._daily_count == 2
