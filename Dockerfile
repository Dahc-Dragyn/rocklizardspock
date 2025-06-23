# Dockerfile

# 1. Use an official Python runtime as a parent image
# Using python 3.11 slim variant for a smaller image size
FROM python:3.11-slim

# 2. Set environment variables
# Prevents Python from buffering stdout and stderr, ensuring logs appear in Cloud Run
ENV PYTHONUNBUFFERED=1
# Set the port the application will listen on (Cloud Run expects 8080 by default)
ENV PORT=8080
# Inform Uvicorn (via main.py) which host to bind to
ENV HOST=0.0.0.0
# Set the working directory in the container
WORKDIR /app

# 3. Install system dependencies (if any)
# Add any build-essential or other packages if needed by your dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements file and install Python dependencies
# Copy requirements first to leverage Docker cache
COPY requirements.txt .
# Install dependencies - use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code into the container
# This includes src/, static/, templates/, images/, main.py
COPY . .

# 6. Expose the port the app runs on
# This informs Docker that the container listens on this port
EXPOSE 8080

# 7. Define the command to run the application
# Use the main.py script which is configured to run uvicorn
# and respects the PORT and HOST environment variables.
# WORKERS can be set via Cloud Run environment variables if needed (defaults to 1 in main.py).
CMD ["python", "main.py"]
