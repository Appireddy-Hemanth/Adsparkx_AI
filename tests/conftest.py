import pytest
import os
from src.config.settings import settings

@pytest.fixture(autouse=True)
def setup_test_env():
    # Make sure we have mock or test environment variables loaded if needed
    # But since settings already loads from .env, it's fine.
    # We can temporarily override things if needed.
    pass
