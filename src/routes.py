# src/routes.py

import logging
from typing import Literal
import os

# FastAPI and related imports
from fastapi import FastAPI, Request, status, Depends, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware # <--- IMPORT THIS

# Rate Limiting imports
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Caching imports
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# External library imports (for exception handling)
import httpx

# Project-specific imports
from .models import Score, PlayResponse, ChatInput, ChatResponse
from .services import (
    get_current_score_service,
    handle_play_round,
    handle_chat,
    DadJokeAPIError
)
from .utils import limiter, http_client

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AIYoda API",
    description="Play Rock Paper Scissors Lizard Spock & Chat with Yoda (Ask for jokes!)"
)

# --- ADD PROXY HEADERS MIDDLEWARE ---
# This tells FastAPI to trust headers like X-Forwarded-Proto (set by Cloud Run)
# to determine if the original request was HTTPS.
# Set trusted_hosts to '*' for Cloud Run, or be more specific if needed.
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
logging.info("Added ProxyHeadersMiddleware.")
# ------------------------------------

# --- Static File & Template Configuration ---
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logging.info("Mounted static directory at /static")
except RuntimeError as e:
    logging.warning(f"Could not mount static directory (might already be mounted, or path issue): {e}")

try:
    app.mount("/images", StaticFiles(directory="images"), name="images")
    logging.info("Mounted images directory at /images")
except RuntimeError as e:
    logging.warning(f"Could not mount images directory (might already be mounted, or path issue): {e}")

templates = Jinja2Templates(directory="templates")
logging.info("Configured Jinja2Templates.")

# --- Rate Limiter Setup ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Exception Handlers ---
@app.exception_handler(DadJokeAPIError)
async def dad_joke_api_exception_handler(request: Request, exc: DadJokeAPIError):
    logging.error(f"Caught Dad Joke API error in handler: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"message": f"The Dad Joke service is currently unavailable: {exc.detail}"},
    )

@app.exception_handler(httpx.RequestError)
async def httpx_request_exception_handler(request: Request, exc: httpx.RequestError):
    logging.error(f"Caught HTTP request error in handler: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"message": f"Failed to connect to an external service: {exc.__class__.__name__}"},
    )

# --- Lifespan Events (Startup & Shutdown) ---
@app.on_event("startup")
async def startup_event():
    logging.info("Application startup...")
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    logging.info("FastAPI Cache initialized with InMemoryBackend.")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Application shutdown...")
    await http_client.aclose()
    logging.info("HTTPX client closed.")

# --- Frontend Endpoint ---
@app.get("/", response_class=HTMLResponse, tags=["Frontend"], include_in_schema=False)
async def read_index(request: Request):
    logging.info("Serving index.html")
    # The middleware should ensure request.url.scheme is 'https' now
    logging.info(f"Request scheme: {request.url.scheme}")
    return templates.TemplateResponse("index.html", {"request": request})

# --- API Endpoints (Backend Logic) ---

# Create an APIRouter instance for API endpoints
api_router_v1 = APIRouter()

@api_router_v1.get("/score", response_model=Score, tags=["Game API"])
@limiter.limit("60/minute")
async def get_score(request: Request):
    score_data = get_current_score_service()
    return score_data

@api_router_v1.post("/play/{player_move}", response_model=PlayResponse, tags=["Game API"])
@limiter.limit("15/minute")
async def play_game(
    player_move: Literal['rock', 'paper', 'scissors', 'lizard', 'spock'],
    request: Request
):
    play_data = await handle_play_round(player_move)
    return play_data

@api_router_v1.post("/chat", response_model=ChatResponse, tags=["Chat API"])
@limiter.limit("15/minute")
async def chat_with_yoda(
    chat_input: ChatInput,
    request: Request
):
    response_text = await handle_chat(chat_input.user_message)
    return ChatResponse(yoda_response=response_text)

# Include the API router in the main app with a prefix
app.include_router(api_router_v1, prefix="/api/v1")
logging.info("Included API router at /api/v1")