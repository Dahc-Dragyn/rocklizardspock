# src/models.py

from pydantic import BaseModel, Field
from typing import Optional

# --- Game Related Models ---

class Score(BaseModel):
    """Represents the current game score."""
    wins: int
    losses: int
    ties: int

class PlayResponse(BaseModel):
    """Response model after playing a round of RPSLS."""
    wins: int
    losses: int
    ties: int
    player_move: str
    computer_move: str
    result: str
    commentary: Optional[str] # Yoda speaks only on computer wins, or provides defaults


# --- Chat Related Models ---

class ChatInput(BaseModel):
    """Request model for sending a message to the chat endpoint."""
    user_message: str = Field(
        ..., # Ellipsis makes the field required
        title="User Message",
        description="The text message sent by the user to chat with Yoda.",
        max_length=500 # Added validation: prevent excessively long inputs
    )

class ChatResponse(BaseModel):
    """Response model for receiving a message from the chat endpoint."""
    yoda_response: str

# --- Misc Models ---
# (No DadJokeResponse needed anymore as it's integrated into chat)