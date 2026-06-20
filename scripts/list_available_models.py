import os
import google.generativeai as genai
from src.config.settings import settings

print("Configuring genai with key...")
genai.configure(api_key=settings.gemini_api_key)

print("Listing models...")
try:
    models = genai.list_models()
    for m in models:
        print(f"Model: {m.name} | Supported methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Failed to list models: {e}")
