# src/services.py

import logging
import random
import json
from typing import Optional, Union, Literal # Keep Optional

# Caching import for joke fetching
from fastapi_cache.decorator import cache

# HTTP client for joke fetching, Gemini client for AI
# Imported here to be used by service functions
from .utils import http_client, gemini_model
# Models for structuring return types or internal use
from .models import Score, PlayResponse # Keep Score, PlayResponse
# HTTP exception type for error handling during joke fetch
import httpx

# --- Constants ---
# JOKE_FETCH_FAILED and JokeFetchStatus are no longer needed for chat response logic
# JOKE_FETCH_FAILED: Literal["JOKE_FETCH_FAILED"] = "JOKE_FETCH_FAILED"
# JokeFetchStatus = Literal["JOKE_FETCH_FAILED"]

# --- Exceptions ---
class ServiceError(Exception):
    """Base class for service-related errors within this module."""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)

class DadJokeAPIError(ServiceError):
    """Custom exception for Dad Joke API errors during fetch."""
    pass

# --- State Management (In-Memory) ---
score_storage = {"score": {"wins": 0, "losses": 0, "ties": 0}}

# --- Internal Helper Functions ---

def _get_score_data() -> dict:
    """Internal function to safely access score data."""
    return score_storage.get("score", {"wins": 0, "losses": 0, "ties": 0}).copy()

def _update_score_data(new_score_dict: dict):
    """Internal function to safely update score data."""
    score_storage["score"] = new_score_dict
    logging.info(f"Score updated in memory: {new_score_dict}")

def pick_computer_move() -> str:
    """Randomly picks the computer's move (internal game logic)."""
    moves = ['rock', 'paper', 'scissors', 'lizard', 'spock']
    return random.choice(moves)

def determine_winner(player_move: str, computer_move: str) -> str:
    """Determines the winner of the game (internal game logic)."""
    if player_move == computer_move:
        return 'Tie.'
    elif (
        (player_move == 'scissors' and (computer_move == 'paper' or computer_move == 'lizard')) or
        (player_move == 'paper' and (computer_move == 'rock' or computer_move == 'spock')) or
        (player_move == 'rock' and (computer_move == 'lizard' or computer_move == 'scissors')) or
        (player_move == 'lizard' and (computer_move == 'spock' or computer_move == 'paper')) or
        (player_move == 'spock' and (computer_move == 'scissors' or computer_move == 'rock'))
    ):
        return 'You win.'
    else:
        return 'You lose.'

@cache(expire=5) # Keep cache on the actual fetching function
async def _fetch_dad_joke_from_api() -> str:
    """
    Internal helper to fetch a dad joke asynchronously using httpx.
    Raises DadJokeAPIError on failure. Caches the result.
    """
    url = "https://icanhazdadjoke.com/"
    headers = {'Accept': 'application/json'}
    logging.info("Attempting to fetch dad joke from API (or cache)...")
    try:
        response = await http_client.get(url, headers=headers)
        response.raise_for_status() # Check for 4xx/5xx errors
        joke_data = response.json()
        joke = joke_data.get('joke')
        if not joke:
             raise DadJokeAPIError("API returned valid response but no joke text found.")
        logging.info("Dad joke fetched successfully.")
        return joke
    except httpx.TimeoutException as e:
        logging.error(f"Dad joke API request timed out: {e}")
        raise DadJokeAPIError(f"Request timed out: {e}")
    except httpx.RequestError as e:
        logging.error(f"Dad joke API request failed: {e}")
        raise DadJokeAPIError(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON response from Dad Joke API: {e}")
        raise DadJokeAPIError(f"Failed to decode JSON response: {e}")
    except DadJokeAPIError as e:
        logging.error(f"DadJokeAPIError during fetch: {e.detail}")
        raise

async def _get_yoda_commentary(player_move: str, computer_move: str, score: Score) -> Optional[str]:
    """
    Internal helper to get Yoda's commentary on his win via Gemini API.
    Returns the commentary string or None if fetching fails.
    """
    prompt = f"""You are Yoda from Star Wars. You just won a round of Rock Paper Scissors Lizard Spock against a player.
    Comment on your victory in 1-2 short sentences, using your characteristic speech pattern (object-subject-verb, wise/cryptic sayings). Be a bit smug about winning.

    Round Details:
    - Player played: {player_move}
    - You (Computer) played: {computer_move} (You won!)
    - Current Score: Player Wins={score.wins}, Your Wins (Losses)={score.losses}, Ties={score.ties}

    Speak your comment on this victory, you will:"""
    try:
        logging.info(f"Calling Gemini API for Yoda commentary (Player: {player_move}, Computer: {computer_move})")
        response = await gemini_model.generate_content_async(prompt)
        commentary = response.text.strip()
        if not commentary:
             if response.prompt_feedback and response.prompt_feedback.block_reason:
                 logging.warning(f"Yoda commentary blocked: {response.prompt_feedback.block_reason}")
                 return "Blocked by the Force, my words are. Hmm."
             else:
                 logging.warning("Gemini returned empty Yoda commentary.")
                 return None
        return commentary
    except Exception as e:
        logging.error(f"Error getting Yoda commentary from Gemini: {e}")
        return None

# --- SIMPLIFIED: Removed joke_info parameter and related logic ---
async def _get_yoda_chat_response(user_message: str) -> Optional[str]:
    """
    Internal helper to get Yoda's chat response via Gemini API for normal conversation.
    Returns the chat response string or None if fetching fails.
    """
    # Only the normal conversation prompt is needed now
    prompt = f"""You are Yoda from Star Wars. Respond to the user's message below.
Speak ONLY in your characteristic style (object-subject-verb order is common, use wise/cryptic sayings, short sentences). Keep your responses relatively brief (1-3 sentences maximum). Do NOT break character.

User says: "{user_message}"

Your response as Yoda (normal conversation):"""

    logging.debug(f"Generated full prompt for Gemini chat:\n{prompt}") # Log the final prompt

    try:
        logging.info(f"Calling Gemini API for Yoda chat response.")
        response = await gemini_model.generate_content_async(prompt) # Use the simplified prompt
        yoda_response = response.text.strip()
        if not yoda_response:
             if response.prompt_feedback and response.prompt_feedback.block_reason:
                 logging.warning(f"Yoda chat response blocked: {response.prompt_feedback.block_reason}")
                 return "Meditating on this, I am. Clouded, the answer is."
             else:
                 logging.warning("Gemini returned empty Yoda chat response.")
                 return None
        return yoda_response
    except Exception as e:
        logging.error(f"Error getting Yoda chat response from Gemini: {e}")
        return None

# --- Public Service Functions (Called by routes.py) ---

def get_current_score_service() -> Score:
    """Service function to retrieve the current score."""
    score_data = _get_score_data()
    return Score(**score_data)

async def handle_play_round(player_move: str) -> PlayResponse:
    """
    Service function to handle all logic for a game round.
    Returns a PlayResponse model containing all results.
    """
    # (This function's logic remains unchanged)
    computer_move = pick_computer_move()
    result = determine_winner(player_move, computer_move)

    current_score_data = _get_score_data()
    current_score_model = Score(**current_score_data)
    if result == 'You win.':
        current_score_data['wins'] += 1
    elif result == 'You lose.':
        current_score_data['losses'] += 1
    elif result == 'Tie.':
        current_score_data['ties'] += 1
    _update_score_data(current_score_data)

    commentary: Optional[str] = None
    if result == 'You lose.':
        logging.info("Player lost. Fetching Yoda commentary...")
        commentary = await _get_yoda_commentary(
            player_move=player_move,
            computer_move=computer_move,
            score=current_score_model
        )
        if commentary is None:
            commentary = "Victorious, I am... comment, the Force blocks. Hmm."
    elif result == 'You win.':
        commentary = f"Strong with {player_move}, you are. Defeated me, you have. Impressive."
    else:
        commentary = f"Both chose {player_move}. A tie, it is. Balanced, the Force remains."

    return PlayResponse(
        wins=current_score_data['wins'],
        losses=current_score_data['losses'],
        ties=current_score_data['ties'],
        player_move=player_move,
        computer_move=computer_move,
        result=result,
        commentary=commentary
    )

# --- MODIFIED handle_chat function ---
async def handle_chat(user_message: str) -> str:
    """
    Service function to handle incoming chat messages.
    If a joke is requested, fetches and returns the joke directly.
    Otherwise, gets Yoda's response via Gemini.
    Returns the response string.
    """
    logging.info(f"Handling chat message in service: {user_message}")
    user_message_lower = user_message.lower()
    # Keywords to detect joke requests
    joke_keywords = [" joke", " funny", " laugh", " humor", " tell me a"]
    is_joke_request = any(keyword in user_message_lower for keyword in joke_keywords)

    # --- BRANCHING LOGIC ---
    if is_joke_request:
        # Handle joke request directly
        logging.info("Joke request detected in handle_chat.")
        try:
            # Attempt to fetch the joke
            fetched_joke = await _fetch_dad_joke_from_api()
            logging.info(f"Dad joke fetched successfully: '{fetched_joke}'")
            # Return the joke text directly
            return fetched_joke
        except DadJokeAPIError as e:
            # Handle fetch failure
            logging.warning(f"Failed to fetch dad joke for chat request: {e.detail}")
            # Return a specific failure message
            return "Find a joke, I could not. Clouded, the source is. Hmm."
        except Exception as e:
            # Handle any other unexpected error during fetch
            logging.error(f"Unexpected error fetching dad joke: {e}")
            return "Disturbance in the Force, there is. Fetch the joke, I could not."
    else:
        # Handle normal chat request via Gemini/Yoda
        logging.info("Normal chat message. Calling _get_yoda_chat_response.")
        # Call the simplified chat response function (no joke_info needed)
        yoda_response = await _get_yoda_chat_response(user_message=user_message)

        # Provide a generic fallback if the Gemini chat call failed
        if yoda_response is None:
            yoda_response = "Meditating, I am. Speak later, we can. Hmm."

        logging.info(f"Returning Yoda response from service: {yoda_response}")
        return yoda_response
