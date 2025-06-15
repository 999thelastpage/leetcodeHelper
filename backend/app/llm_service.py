import os
import json
import asyncio
import hashlib
import re
import google.generativeai as genai
from dotenv import load_dotenv
from app.models import (
    ScrapedProblem,
    AnalysisSection,
    ExplanationSection,
    SolutionSection,
    ResourcesSection,
    SimilarProblemsSection,
    ChatResponse
)

# --- Environment and API Configuration ---

# Construct the path to the .env file located in the 'backend' directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Configure the Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # Get model name from environment or use a default
    model_name = os.getenv("GEMINI_MODEL_NAME", 'gemini-1.5-pro-latest')
    model = genai.GenerativeModel(model_name)
    print(f"Successfully configured Gemini model: {model_name}")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    model = None

# --- Caching Configuration ---
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# --- Helper Functions ---

def _get_base_prompt(problem: ScrapedProblem) -> str:
    """Creates the common base prompt with the problem details."""
    return f"""
    You are a world-class LeetCode tutor and expert programmer.
    Here is the LeetCode problem we are analyzing:

    **Problem Title:** {problem.title}
    **Problem Tags:** {', '.join(problem.tags) if problem.tags else 'N/A'}
    **Problem Description:**
    {problem.description}

    **Examples:**
    {problem.examples}

    **Constraints:**
    {problem.constraints}

    ---
    """

async def _call_llm(prompt: str) -> dict:
    """
    Generic asynchronous function to call the LLM, parse the JSON response,
    and handle file-based caching.
    """
    if not model:
        raise Exception("Gemini model is not configured. Check API key.")

    # Create a unique, stable cache key from the prompt
    cache_key = hashlib.md5(prompt.encode('utf-8')).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

    # Check if a cached response exists
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Cache read failed for {cache_file}. Error: {e}. Refetching.")

    # If not cached, call the LLM
    try:
        response = await model.generate_content_async(prompt)
        text = response.text
        
        # Use regex to find the JSON block
        match = re.search(r'```json\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
        if not match:
             # Fallback for non-fenced JSON
            match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)

        if not match:
            raise ValueError("Could not find a JSON object or list in the LLM response.")

        json_str = match.group(1)
        data = json.loads(json_str)

        # Save the successful response to the cache
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Cache write failed for {cache_file}. Error: {e}")

        return data
    except Exception as e:
        print(f"LLM call failed. Error: {e}")
        raise Exception(f"Failed to get or parse LLM response: {e}")

# --- Granular LLM Generation Functions ---

async def generate_problem_analysis(problem: ScrapedProblem) -> AnalysisSection:
    """Generates just the high-level analysis of the problem."""
    prompt = _get_base_prompt(problem) + """
    Based on the problem details, provide a concise, high-level analysis as a single string.
    What is the core challenge? What data structures or algorithms might be relevant?

    Your entire response must be a single, valid JSON object with one key "analysis", and its value must be a string.
    Do not include any other text, explanations, or markdown formatting outside of the JSON object.
    """
    data = await _call_llm(prompt)
    return AnalysisSection(**data)

async def generate_explanation(problem: ScrapedProblem) -> ExplanationSection:
    """Generates the detailed, in-depth explanation of the solution."""
    prompt = _get_base_prompt(problem) + """
    Provide an extremely detailed, in-depth walkthrough of the optimal solution. This is the most important section.
    The response should be a single, long string formatted using Markdown for readability.

    Use markdown-style headers for structure, for example:
    ## Pattern Analysis
    ... text ...
    
    ## Intuition
    ... text ...

    ## Algorithm
    ... text ...

    ## Complexity Analysis
    ... text ...

    Your entire response must be a single, valid JSON object with one key: "explanation". The value for "explanation" must be the single string containing the full walkthrough. Do not nest another JSON object inside the string.
    Do not include any other text, explanations, or markdown formatting outside of the JSON object.
    """
    data = await _call_llm(prompt)
    return ExplanationSection(**data)

async def generate_solutions(problem: ScrapedProblem) -> SolutionSection:
    """Generates the well-commented solutions in multiple languages."""
    prompt = _get_base_prompt(problem) + """
    Provide well-commented, optimal solutions in Python, Java, and C++.
    For each solution, add detailed comments explaining *why* the code works, not just *what* it does.

    Your entire response must be a single, valid JSON object containing three string keys: "python", "java", and "cpp".
    Do NOT nest it inside another object.
    Do not include any other text, explanations, or markdown formatting outside of the JSON object.
    """
    data = await _call_llm(prompt)
    # Manually construct the nested structure expected by the Pydantic model
    return SolutionSection(solution=data)

async def generate_resources(problem: ScrapedProblem) -> ResourcesSection:
    """Generates a list of high-quality, obscure learning resources."""
    prompt = _get_base_prompt(problem) + """
    Find 5 external resources for this problem. They should be high-quality but from more obscure or hard-to-find sources that a typical user might miss (e.g., university lecture notes, deep-dive blog posts, specific sections of academic papers). Avoid obvious links like GeeksforGeeks.

    For each resource, provide its title, URL, and a reason. The reason should explain how the resource is useful, what it talks about, and why a user should go through it.

    Your entire response must be a single, valid JSON list of objects. Each object should have "title", "url", and "reason" keys.
    Do NOT nest it inside another object. The response should start with `[` and end with `]`.
    Do not include any other text, explanations, or markdown formatting outside of the JSON list.
    """
    data = await _call_llm(prompt)
    # Manually construct the nested structure expected by the Pydantic model
    return ResourcesSection(resources=data)

async def generate_similar_problems(problem: ScrapedProblem) -> SimilarProblemsSection:
    """Generates a list of similar problems, categorized by difficulty."""
    prompt = _get_base_prompt(problem) + """
    Provide a list of similar LeetCode problems, categorized by difficulty.
    For each problem, provide its title, URL, and a "reason" explaining why it's a good problem to solve for practice.

    Your entire response must be a single, valid JSON object containing three keys: "easy", "medium", and "hard".
    Each key should hold a list of problem objects (with "title", "url", and "reason").
    Do NOT nest it inside another object.
    Do not include any other text, explanations, or markdown formatting outside of the JSON object.
    """
    data = await _call_llm(prompt)
    # Manually construct the nested structure expected by the Pydantic model
    return SimilarProblemsSection(similar_problems=data)


# --- Chat Function ---

async def generate_chat_response(problem_context: str, chat_history: list, user_message: str) -> ChatResponse:
    """
    Generates a chat response from the LLM based on the conversation history.
    """
    if not model:
        raise Exception("Gemini model is not configured. Check API key.")

    history_for_llm = [
        {"role": "user", "parts": [f"Here is the problem we are discussing:\n{problem_context}"]},
        {"role": "model", "parts": ["Understood. I am ready to answer your questions about this problem."]}
    ]
    for message in chat_history:
        role = "user" if message['role'] == 'user' else "model"
        history_for_llm.append({"role": role, "parts": [message['content']]})

    chat_session = model.start_chat(history=history_for_llm)
    
    try:
        response = await chat_session.send_message_async(user_message)
        llm_reply = response.text
        # Request Markdown formatting in the chat response
        return ChatResponse(llm_reply=llm_reply)
    except Exception as e:
        raise Exception(f"Failed to get chat response from LLM: {e}")
