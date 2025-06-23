# src/utils.py

import os
import logging
import httpx
import google.generativeai as genai
# Removed: from dotenv import load_dotenv (No longer needed)
from slowapi import Limiter
from slowapi.util import get_remote_address

# --- Configuration Loading ---

# Removed: load_dotenv() call (No longer needed for deployment)

# Fetch the Google API key directly from environment variables set by the platform
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logging.error("FATAL ERROR: GOOGLE_API_KEY environment variable not set in deployment environment.")
    # For a real application, you might want a more graceful shutdown
    # or a mechanism to prevent starting without the key.
    raise ValueError("GOOGLE_API_KEY is missing. Please ensure it is set in your deployment environment variables.")

# Define the Gemini model name to use
# Using gemini-2.0-flash-lite-001 based on user preference [2025-03-17]
GEMINI_MODEL_NAME = "gemini-2.0-flash-lite-001"

# --- Client Initialization ---

# Initialize the shared httpx client for making async HTTP requests
# Used by services.py for fetching dad jokes
# Set a default timeout (can be overridden per request if needed)
http_client = httpx.AsyncClient(timeout=10.0)
logging.info("Initialized shared httpx.AsyncClient.")

# Configure and initialize the Google Generative AI model client
# Used by services.py for Yoda commentary and chat
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Consider adding safety settings globally here if desired,
    # matching or complementing any settings applied during calls
    # safety_settings = [...]
    gemini_model = genai.GenerativeModel(
        GEMINI_MODEL_NAME#,
        # safety_settings=safety_settings
        )
    logging.info(f"Initialized Google Generative AI client with model: {GEMINI_MODEL_NAME}")
except Exception as e:
    logging.error(f"FATAL ERROR: Failed to initialize Google Generative AI client: {e}")
    # Again, handle fatal errors appropriately for your deployment strategy
    raise

# --- Rate Limiter Initialization ---

# Initialize the rate limiter instance
# It uses the client's remote address (IP address) as the default key
# The state and exception handler are configured in routes.py
limiter = Limiter(key_func=get_remote_address)
logging.info("Initialized slowapi Limiter.")

# --- Other Utilities (Optional) ---
# Add any other shared utility functions or constants below if needed
# E.g., def format_timestamp(dt): ...