# main.py (at the project root)

import uvicorn
import os
import logging

# Configure logging for the runner script itself (optional)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

if __name__ == "__main__":
    # --- Configuration for Uvicorn Server ---

    # Host address to bind the server to
    # '0.0.0.0' makes it accessible on your network, '127.0.0.1' only locally
    host = os.getenv("HOST", "0.0.0.0")

    # Port to run the server on
    # Use PORT environment variable (common in deployment platforms) or default to 8000
    try:
        port = int(os.getenv("PORT", "8000"))
    except ValueError:
        log.warning("Invalid PORT environment variable. Using default 8000.")
        port = 8000

    # Auto-reload for development
    # Set DEV_MODE=true or DEV_MODE=1 in your environment for auto-reload
    reload = os.getenv("DEV_MODE", "false").lower() in ("true", "1", "t")

    # Number of worker processes
    # Useful for production, typically set based on CPU cores
    # Set WORKERS=4 in your environment for 4 workers, defaults to 1
    try:
        workers = int(os.getenv("WORKERS", "1"))
        if workers < 1:
            workers = 1
    except ValueError:
        log.warning("Invalid WORKERS environment variable. Using default 1.")
        workers = 1

    log.info(f"Starting Uvicorn server:")
    log.info(f"  Host: {host}")
    log.info(f"  Port: {port}")
    log.info(f"  Reload: {reload}")
    log.info(f"  Workers: {workers}")
    log.info(f"  Application: src.routes:app") # The path to your FastAPI app instance

    # --- Run Uvicorn ---
    uvicorn.run(
        "src.routes:app", # Path to the app instance (module:variable)
        host=host,
        port=port,
        reload=reload,    # Enable auto-reload if reload is True
        workers=workers   # Set the number of worker processes
        # You can add other uvicorn options here if needed, e.g., log_level
        # log_level="info" # Uvicorn's logging level
    )