# Tech Context: LeetCode Problem Analyzer & Tutor

## 1. Core Technologies

*   **Backend Language:** Python (Version 3.9+)
*   **Backend Framework:** FastAPI
*   **Frontend Approach (Finalized):**
    *   HTML5
    *   CSS3 with Materialize CSS framework.
    *   Vanilla JavaScript (ES6+) for DOM manipulation and API calls.
    *   `marked.js` for Markdown rendering.
*   **LLM:** Google Gemini 1.5 Pro (accessed via API).
    *   **Note:** The specific model name (`gemini-1.5-pro-latest`) was critical for functionality, as older models were not found.
*   **Problem Data Source:** LeetCode GraphQL API.
    *   `requests`: For making POST requests to the GraphQL endpoint.
    *   `BeautifulSoup4`: Used minimally to parse HTML embedded in the GraphQL JSON response.
*   **Data Serialization:** JSON for API request/response bodies and for the GraphQL payload.

## 2. Development Environment & Setup

*   **Python Environment Management:** `venv` is recommended. A `requirements.txt` file is provided.
*   **Code Editor/IDE:** VS Code.
*   **Version Control:** Git, with a `.gitignore` file to exclude unnecessary files (e.g., `.env`, `__pycache__`, `llm_cache.json`). The repository is hosted on GitHub.
*   **Backend Server:** Uvicorn, run via `python -m uvicorn`.
    *   **Note:** Using `python -m` was necessary to resolve PATH issues on the user's system.
*   **API Key Management:**
    *   LLM API keys are managed via a `.env` file in the `backend` directory.
    *   **Note:** A common setup issue was resolved by ensuring the file is named `.env`, not `.env.example`.

## 3. Technical Constraints & Considerations

*   **LeetCode GraphQL API:** While more stable than HTML scraping, changes to the GraphQL schema are still possible, though less frequent. This is the primary external dependency for data retrieval.
*   **LLM API Limitations:**
    *   **Rate Limits, Token Limits, Cost:** Standard API usage considerations apply.
*   **Output Variability & Prompt Engineering:** This remains a key challenge. The monolithic prompt has been broken down into smaller, more focused prompts for each API endpoint. This improves reliability but still requires careful engineering to ensure the LLM returns valid JSON that matches the Pydantic models for each specific section. A robust JSON parsing function was added to the backend to handle minor LLM inconsistencies.
*   **Caching (Updated):** The file-based LLM cache (`llm_cache.json`) has been **removed**. It has been replaced by a simple, in-memory dictionary in `main.py` that caches only the data from the `/api/scrape` endpoint for the duration of the server session. This prevents redundant calls to the LeetCode GraphQL API.
*   **Security:** The primary security concern is protecting the LLM API key in the `.env` file, which is handled by `.gitignore`.
*   **Chat Widget Handling:** Dynamic JavaScript is used to manage the chat widget's size and interactivity.

## 4. Key Dependencies (Final `requirements.txt` for backend)

```
fastapi
uvicorn[standard]
pydantic
requests
beautifulsoup4
google-generativeai
python-dotenv
asyncio
```

## 5. Tool Usage Patterns

*   **API Interaction:** Backend uses `google-generativeai` for the LLM and `requests` for the GraphQL API. Frontend uses the `fetch` API.
*   **Error Logging:** Basic logging via `print()` statements was used for debugging. For a production system, a more robust logging library should be implemented.
