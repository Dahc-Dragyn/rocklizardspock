// static/script.js

// Wait for the HTML DOM to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {

    // --- Get DOM Element References ---
    // Scoreboard
    const scoreWinsEl = document.getElementById('score-wins');
    const scoreLossesEl = document.getElementById('score-losses');
    const scoreTiesEl = document.getElementById('score-ties');

    // Game Elements
    const gameControlsEl = document.getElementById('game-controls'); // Container for buttons
    const moveButtons = document.querySelectorAll('.move-button'); // All move buttons
    const resultsDisplayEl = document.getElementById('results-display');
    const playerChoiceImgEl = document.getElementById('player-choice-img');
    const computerChoiceImgEl = document.getElementById('computer-choice-img');
    const resultTextEl = document.getElementById('result-text');
    const commentaryTextEl = document.getElementById('commentary-text');
    const gameLoadingEl = document.getElementById('game-loading');
    const gameErrorEl = document.getElementById('game-error');

    // Chat Elements
    const chatHistoryEl = document.getElementById('chat-history');
    const chatFormEl = document.getElementById('chat-form');
    const chatInputEl = document.getElementById('chat-input');
    const chatSendButtonEl = document.getElementById('chat-send-button');
    const chatLoadingEl = document.getElementById('chat-loading');
    const chatErrorEl = document.getElementById('chat-error');

    // Rules Elements
    const rulesToggleBtn = document.getElementById('rules-toggle-button');
    const rulesContentEl = document.getElementById('rules-content');
    const rulesCloseBtn = document.getElementById('rules-close-button'); // Optional close button

    // API Base URL (using the prefix we defined in routes.py)
    const API_BASE_URL = '/api/v1';

    // --- Helper Functions ---

    /** Capitalizes the first letter of a string */
    function capitalizeFirstLetter(string) {
        if (!string) return '';
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    /** Scrolls chat history to the bottom */
    function scrollChatToBottom() {
        chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
    }

     /** Shows a loading indicator and hides the corresponding error */
    function showLoading(loadingEl, errorEl) {
        if (loadingEl) loadingEl.style.display = 'block';
        if (errorEl) errorEl.style.display = 'none'; // Hide error when loading starts
    }

    /** Hides a loading indicator */
    function hideLoading(loadingEl) {
        if (loadingEl) loadingEl.style.display = 'none';
    }

    /** Displays an error message */
    function displayError(errorEl, message) {
        if (errorEl) {
            errorEl.textContent = `Error: ${message || 'An unknown error occurred.'}`;
            errorEl.style.display = 'block';
        }
    }

    /** Clears results display elements */
    function clearResultsDisplay() {
        playerChoiceImgEl.style.display = 'none';
        playerChoiceImgEl.src = '';
        playerChoiceImgEl.alt = '';
        computerChoiceImgEl.style.display = 'none';
        computerChoiceImgEl.src = '';
        computerChoiceImgEl.alt = '';
        resultTextEl.textContent = '';
        resultTextEl.className = 'result-text status-text'; // Reset classes
        commentaryTextEl.textContent = '';
        gameErrorEl.style.display = 'none'; // Hide previous errors
    }

    // --- Scoreboard Functions ---

    /** Updates the scoreboard display */
    function updateScoreboard(wins, losses, ties) {
        scoreWinsEl.textContent = wins;
        scoreLossesEl.textContent = losses;
        scoreTiesEl.textContent = ties;
    }

    /** Fetches the initial score from the backend */
    async function fetchInitialScore() {
        try {
            const response = await fetch(`${API_BASE_URL}/score`);
            if (!response.ok) {
                // Log error but don't block UI for this non-critical fetch
                console.error(`HTTP error fetching score: ${response.status}`);
                return;
            }
            const scoreData = await response.json();
            updateScoreboard(scoreData.wins, scoreData.losses, scoreData.ties);
        } catch (error) {
            console.error('Network error fetching initial score:', error);
            // Optionally display a subtle error somewhere if needed
        }
    }

    // --- Game Functions ---

    /** Displays the results of a game round */
    function displayResults(playerMove, computerMove, result, commentary) {
        clearResultsDisplay(); // Clear previous results first

        const playerImgFile = capitalizeFirstLetter(playerMove) + '.jpg';
        const computerImgFile = capitalizeFirstLetter(computerMove) + '.jpg';

        playerChoiceImgEl.src = `/images/${playerImgFile}`;
        playerChoiceImgEl.alt = `Player chose ${playerMove}`;
        playerChoiceImgEl.style.display = 'block';

        computerChoiceImgEl.src = `/images/${computerImgFile}`;
        computerChoiceImgEl.alt = `Yoda chose ${computerMove}`;
        computerChoiceImgEl.style.display = 'block';

        resultTextEl.textContent = result;
        // Add class based on result for styling
        if (result.toLowerCase().includes('win')) {
            resultTextEl.classList.add('status-win');
        } else if (result.toLowerCase().includes('lose')) {
            resultTextEl.classList.add('status-loss');
        } else {
            resultTextEl.classList.add('status-tie');
        }

        commentaryTextEl.textContent = commentary || ''; // Display commentary or empty string
    }

    /** Handles the API call when a player makes a move */
    async function playGame(move) {
        console.log(`Player chose: ${move}`);
        showLoading(gameLoadingEl, gameErrorEl);
        clearResultsDisplay(); // Clear previous results while loading

        try {
            const response = await fetch(`${API_BASE_URL}/play/${move}`, {
                method: 'POST',
                headers: {
                    // No 'Content-Type' needed for GET or path param POSTs like this
                }
            });

            if (!response.ok) {
                 // Try to get error message from API response if possible
                let errorMsg = `API Error: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.detail || errorData.message || errorMsg;
                } catch (e) { /* Ignore if response is not JSON */ }
                throw new Error(errorMsg); // Throw to be caught by catch block
            }

            const data = await response.json(); // Should be PlayResponse model

            // Update UI with results
            displayResults(data.player_move, data.computer_move, data.result, data.commentary);
            updateScoreboard(data.wins, data.losses, data.ties);

        } catch (error) {
            console.error('Error playing game:', error);
            displayError(gameErrorEl, error.message || 'Could not connect to the game server.');
            // Clear results display on error to avoid showing stale data
            clearResultsDisplay();
        } finally {
            hideLoading(gameLoadingEl);
        }
    }

    /** Handles clicks on the move buttons */
    function handleMoveClick(event) {
        // Find the button that was clicked, even if the click was on the image inside it
        const button = event.target.closest('.move-button');
        if (!button) return; // Exit if click wasn't on a button or its child

        const move = button.dataset.move; // Get move from data-move attribute
        if (move) {
            playGame(move);
        } else {
            console.error('Move button clicked, but data-move attribute not found.');
        }
    }

    // --- Chat Functions ---

    /** Adds a message to the chat history display */
    function addChatMessage(message, sender) {
        const messageEl = document.createElement('div');
        messageEl.classList.add('chat-message');
        messageEl.classList.add(sender === 'user' ? 'user-message' : 'yoda-message');
        messageEl.textContent = message; // Use textContent to prevent HTML injection
        chatHistoryEl.appendChild(messageEl);
        scrollChatToBottom(); // Scroll down to show the new message
    }

    /** Handles the API call to send a chat message */
    async function sendChatMessage(message) {
        showLoading(chatLoadingEl, chatErrorEl);
        chatInputEl.disabled = true;
        chatSendButtonEl.disabled = true;

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json' // Indicate we expect JSON back
                },
                body: JSON.stringify({ user_message: message })
            });

             if (!response.ok) {
                let errorMsg = `API Error: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.detail || errorData.message || errorMsg;
                } catch (e) { /* Ignore if response is not JSON */ }
                throw new Error(errorMsg);
            }

            const data = await response.json(); // Should be ChatResponse model
            addChatMessage(data.yoda_response, 'yoda');

        } catch (error) {
            console.error('Error sending chat message:', error);
            displayError(chatErrorEl, error.message || 'Could not send message.');
            // Optionally add an error message to the chat history as well
            // addChatMessage(`Error: ${error.message || 'Could not send message.'}`, 'error');
        } finally {
            hideLoading(chatLoadingEl);
            chatInputEl.disabled = false;
            chatSendButtonEl.disabled = false;
            chatInputEl.focus(); // Return focus to input after sending
        }
    }

    /** Handles the chat form submission */
    function handleChatSubmit(event) {
        event.preventDefault(); // Prevent default page reload on form submission
        const userMessage = chatInputEl.value.trim();

        if (!userMessage) {
            return; // Don't send empty messages
        }

        addChatMessage(userMessage, 'user'); // Display user's message immediately
        chatInputEl.value = ''; // Clear the input field
        sendChatMessage(userMessage); // Send the message to the backend
    }

    // --- Rules Functions ---

    /** Toggles the visibility of the rules content using a CSS class */
    function toggleRules() {
    // Toggle a class like 'is-visible' on the rules content element
    // classList.toggle returns true if the class was added, false if removed
    const rulesAreNowVisible = rulesContentEl.classList.toggle('is-visible');

    // Update button text and ARIA attribute based on the new state
    if (rulesAreNowVisible) {
        rulesToggleBtn.textContent = 'Hide Rules';
        rulesToggleBtn.setAttribute('aria-expanded', 'true');
        // Optional: you could add focus management here for accessibility
        // e.g., rulesContentEl.focus(); // (Requires tabindex="-1" on the div)
    } else {
        rulesToggleBtn.textContent = 'Show Rules';
        rulesToggleBtn.setAttribute('aria-expanded', 'false');
    }
}


    // --- Event Listeners Setup ---

    // Add one listener to the container for game buttons (Event Delegation)
    if (gameControlsEl) {
        gameControlsEl.addEventListener('click', handleMoveClick);
    } else {
         console.error("Game controls container not found!");
    }

    // Listener for chat form submission
    if (chatFormEl) {
        chatFormEl.addEventListener('submit', handleChatSubmit);
    } else {
        console.error("Chat form not found!");
    }

    // Listener for rules toggle button
    if (rulesToggleBtn) {
        rulesToggleBtn.addEventListener('click', toggleRules);
    } else {
        console.error("Rules toggle button not found!");
    }

    // Listener for optional rules close button
    if (rulesCloseBtn) {
        rulesCloseBtn.addEventListener('click', toggleRules); // Can reuse the toggle function
    }

    // --- Initial Setup ---
    fetchInitialScore(); // Load initial score when the page loads
    console.log("AIYoda Frontend Initialized!");

}); // End DOMContentLoaded