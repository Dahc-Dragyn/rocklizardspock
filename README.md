# rocklizardspock
FastAPI Project Boilerplate
This project serves as a robust starting point for a high-performance web application or API using the FastAPI framework. It includes a configurable server runner, essential dependencies for API development, caching, rate limiting, and templating.

The application is launched via a flexible main.py script that can be configured using environment variables, making it easy to switch between development and production settings.

Features
FastAPI Framework: For building modern, high-performance APIs with Python.
Configurable Uvicorn Server: main.py acts as a runner for the Uvicorn ASGI server with settings managed by environment variables.
Development Mode: Enable auto-reload for rapid development by setting DEV_MODE=true.
Production Ready: Configure multiple worker processes to handle concurrent requests efficiently.
Dependency Management: All required packages are listed in requirements.txt.
Caching: Includes fastapi-cache2 to cache responses and improve performance.
Rate Limiting: Includes slowapi to protect your endpoints from abuse.
Jinja2 Templating: Ready for serving HTML web pages from the backend.
Environment-based Configuration: Uses .env files for easy management of settings.
Installation
Follow these steps to get the project running on your local machine.

Clone the Repository

Bash

git clone <your-repository-url>
cd <your-repository-name>
Create and Activate a Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies.

On macOS/Linux:
Bash

python3 -m venv venv
source venv/bin/activate
On Windows:
Bash

python -m venv venv
.\venv\Scripts\activate
Install Dependencies
Install all the necessary packages from the requirements.txt file.

Bash

pip install -r requirements.txt
