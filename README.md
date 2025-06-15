
![Screenshot 2025-06-15 175837](https://github.com/user-attachments/assets/aebcddee-cb4f-4725-a84a-ac05ae7faa65)

# LeetCode Problem Analyzer & Tutor

This web application serves as an AI-powered tutor to help users analyze and understand LeetCode problems. By providing a LeetCode problem URL, users can get a detailed analysis, multi-language solutions, curated learning resources, and suggestions for similar problems. The application also features an interactive chat to discuss the problem with an LLM.

## Key Features

*   **In-Depth Problem Analysis:** Get a clear breakdown of the problem's core concepts and optimal approach.
*   **Detailed Explanations:** A comprehensive walkthrough of the solution, including pattern analysis, intuition, and complexity analysis.
*   **Multi-Language Solutions:** View optimal, well-commented solutions in Python, Java, and C++.
*   **Curated Resources:** Access a list of high-quality, hard-to-find resources for deeper learning.
*   **Similar Problem Suggestions:** Receive recommendations for similar problems to solidify your understanding.
*   **Interactive Chat Tutor:** Ask clarifying questions and explore concepts in a floating chat window.
*   **Response Caching:** Saves LLM responses to a local cache to speed up subsequent requests for the same problem.

## Tech Stack

*   **Backend:** Python 3.9+ with FastAPI
*   **Frontend:** Vanilla HTML, Materialize CSS, and JavaScript
*   **LLM:** Google Gemini
*   **Data Source:** LeetCode's Public GraphQL API

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/999thelastpage/leetcodeHelper.git
cd leetcodeHelper
```

### 2. Set Up the Backend

**a. Create a Virtual Environment:**

It's highly recommended to use a virtual environment to manage Python dependencies.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**b. Install Dependencies:**

Install all the required Python packages from the `requirements.txt` file located in the `backend` directory.

```bash
pip install -r backend/requirements.txt
```

**c. Create the Environment File:**

You need to provide your Google Gemini API key.

1.  Navigate to the `backend` directory.
2.  Create a new file named `.env`.
3.  Add your API key to this file as follows:

    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    GEMINI_MODEL_NAME="gemini-2.0-flash"
    ```

    Replace `"YOUR_API_KEY_HERE"` with your actual Gemini API key.
    Replace `"gemini-2.0-flash"` with your choice of Gemini model.

## How to Run the Application

1.  **Start the Backend Server:**

    Make sure you are in the root directory of the project (`leetcodeHelper`) and your virtual environment is activated. Run the following command:

    ```bash
    python -m uvicorn backend.main:app --reload
    ```

    The backend server will start, typically at `http://127.0.0.1:8000`.

2.  **Open the Frontend:**

    Open the `frontend/index.html` file directly in your web browser. You can do this by right-clicking the file in your file explorer and selecting "Open with" your preferred browser.

3.  **Start Analyzing!**

    You can now paste a LeetCode problem URL into the input field and start using the application.
