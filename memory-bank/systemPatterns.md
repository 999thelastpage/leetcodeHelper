# System Patterns: LeetCode Problem Analyzer & Tutor

## 1. High-Level Architecture

The system follows a client-server architecture. The key change is the move from a single backend analysis endpoint to a **parallel, multi-endpoint architecture**. The frontend first scrapes the problem data and then makes multiple, concurrent requests to the backend for each piece of the analysis.

graph TD
    subgraph "User Interaction"
        User[User] --> FE[Frontend UI]
    end

    subgraph "Application Services"
        FE -->|1. Scrape Request (URL)| ScrapeEP[/api/scrape]
        ScrapeEP -->|Problem Data| FE

        subgraph "Parallel LLM Calls"
            direction LR
            FE -->|2a. Analysis Request| AnalysisEP[/api/analysis]
            FE -->|2b. Explanation Request| ExplanationEP[/api/explanation]
            FE -->|2c. Solutions Request| SolutionsEP[/api/solutions]
            FE -->|2d. Resources Request| ResourcesEP[/api/resources]
            FE -->|2e. Similar Problems Request| SimilarEP[/api/similar-problems]
            FE -->|2f. Chat Request| ChatEP[/api/chat]
        end

        subgraph "Backend Services"
            ScrapeEP --> LC_API[LeetCode GraphQL API]
            AnalysisEP --> LLM_API[Gemini LLM API]
            ExplanationEP --> LLM_API
            SolutionsEP --> LLM_API
            ResourcesEP --> LLM_API
            SimilarEP --> LLM_API
            ChatEP --> LLM_API
        end

        AnalysisEP -->|Analysis Data| FE
        ExplanationEP -->|Explanation Data| FE
        SolutionsEP -->|Solutions Data| FE
        ResourcesEP -->|Resources Data| FE
        SimilarEP -->|Similar Problems Data| FE
        ChatEP -->|Chat Data| FE
    end

    subgraph "External Services"
        LC_API
        LLM_API
    end
```

## 2. Key Components and Responsibilities

### 2.1. Frontend

*   **Input Module:** Accepts LeetCode problem URL.
*   **API Client:**
    *   Handles the initial asynchronous request to `/api/scrape`.
    *   Upon receiving the scraped data, it triggers **multiple, parallel** `fetch` calls to the granular analysis endpoints (`/api/analysis`, `/api/explanation`, etc.) and the chat endpoint (`/api/chat`).
    *   Uses `Promise.allSettled` or a similar mechanism to handle responses as they arrive.
*   **Display Module:**
    *   Renders individual loading indicators for each content card.
    *   Populates each section of the UI **as its specific data arrives** (lazy loading).
    *   Includes a **retry mechanism** for each section, allowing users to re-fetch data for a specific component if it fails.
    *   Renders Markdown content in the "Detailed Explanation" section and the chat window.
*   **Chat Module:** Provides the floating, minimizable chat interface with Markdown rendering.

### 2.2. Backend (Python - FastAPI)

*   **API Endpoints (Refactored):**
    *   `POST /api/scrape`: Scrapes the problem data from LeetCode and returns it. Includes an in-memory cache to avoid re-scraping.
    *   `POST /api/analysis`: Generates and returns only the problem analysis.
    *   `POST /api/explanation`: Generates and returns only the detailed explanation.
    *   `POST /api/solutions`: Generates and returns only the code solutions.
    *   `POST /api/resources`: Generates and returns only the external resources.
    *   `POST /api/similar-problems`: Generates and returns only the similar problems.
    *   `POST /api/chat`: Handles chat interactions.
*   **LLM Interaction Service (Refactored):**
    *   Contains multiple, smaller `async` functions (e.g., `generate_explanation`, `generate_solutions`), each with a highly specific, targeted prompt.
    *   Prompts now request Markdown formatting for improved readability.
    *   No longer contains a monolithic `generate_analysis` function.
    *   Includes a robust JSON parsing helper (`_call_llm`) to handle potential malformed output from the LLM.
*   **Caching Service (Simplified):**
    *   The complex file-based LLM cache has been **removed**.
    *   A simple in-memory dictionary now caches the results of the `/api/scrape` call to prevent redundant GraphQL requests during a single session.
*   **LeetCode Data Service:** Unchanged. Uses the GraphQL API.

### 2.3. LLM (Gemini 1.5 Pro - via API)

*   **Core Logic Engine:** Still the core engine, but now its tasks are broken down into smaller, more focused prompts, making its output more reliable for each specific section.

## 3. Data Flow Example (Refactored Lazy-Loading Flow)

1.  User enters a LeetCode URL in the Frontend.
2.  Frontend shows loading indicators in all result cards.
3.  Frontend sends a single request to the Backend (`/api/scrape`).
4.  Backend scrapes the data (using its cache if available) and returns the `ScrapedProblem` object.
5.  Frontend receives the `ScrapedProblem` object. It immediately fires off **six parallel requests** to `/api/analysis`, `/api/explanation`, `/api/solutions`, `/api/resources`, `/api/similar-problems`, and `/api/chat`, each including the `ScrapedProblem` data in its body.
6.  As each of the six backend endpoints completes its specific LLM call, it returns its piece of data (e.g., `AnalysisSection`, `SolutionSection`, `ChatResponse`).
7.  As the Frontend receives each response, it **independently populates the corresponding section** in the UI and hides its loading indicator. If a request fails, it shows a retry icon for that specific section.

## 4. Key Design Considerations & Patterns

*   **Parallelism and Lazy Loading:** This is the new core pattern. It improves perceived performance and isolates failures, making the application more resilient.
*   **Granular API Design:** The backend now follows a more microservice-like approach, with single-responsibility endpoints.
*   **Robust Prompt Engineering:** Prompts are now smaller and more focused, but still require high specificity to ensure reliable JSON output.
*   **Asynchronous Operations:** All I/O operations (API calls to LeetCode and the LLM) are fully asynchronous.
*   **Client-Side Orchestration:** The frontend is now responsible for orchestrating the multiple calls required to build the full results page.
*   **Dynamic Chat Widget Handling:** JavaScript is used to dynamically adjust the height and overflow properties of the chat widget to ensure proper layout and interactivity.
