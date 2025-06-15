import uvicorn
import sys
import os
import logging
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl

# Add the project root to the Python path to allow absolute imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from app.models import (
    AnalyzeRequest, ChatRequest, ScrapedProblem,
    AnalysisSection, ExplanationSection, SolutionSection,
    ResourcesSection, SimilarProblemsSection, ChatResponse
)
from app.scraper import scrape_leetcode_problem
from app.llm_service import (
    generate_problem_analysis,
    generate_explanation,
    generate_solutions,
    generate_resources,
    generate_similar_problems,
    generate_chat_response
)

# --- App and CORS Configuration ---
app = FastAPI(
    title="LeetCode Problem Analyzer & Tutor API",
    description="API for analyzing LeetCode problems, providing solutions, and offering chat support.",
    version="1.0.0",
)

origins = [
    "http://localhost", "http://localhost:8000",
    "http://127.0.0.1", "http://127.0.0.1:8000",
    "null",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory Cache for Scraped Data ---
scraped_data_cache = {}

# --- API Endpoints ---

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the LeetCode Problem Analyzer & Tutor API!"}

@app.post("/api/scrape", response_model=ScrapedProblem, tags=["Problem Data"])
async def scrape_problem(url_request: dict):
    """
    Scrapes a LeetCode problem from a URL and caches the result.
    This is the first call the frontend should make.
    """
    url = url_request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")

    if url in scraped_data_cache:
        return scraped_data_cache[url]
    
    try:
        scraped_data = scrape_leetcode_problem(url)
        scraped_data_cache[url] = scraped_data
        return scraped_data
    except Exception as e:
        logging.error(f"Error scraping problem: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape problem: {e}")

@app.post("/api/analysis", response_model=AnalysisSection, tags=["Analysis Components"])
async def get_analysis(request: AnalyzeRequest):
    try:
        return await generate_problem_analysis(request.problem)
    except Exception as e:
        logging.error(f"Error getting analysis: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/explanation", response_model=ExplanationSection, tags=["Analysis Components"])
async def get_explanation(request: AnalyzeRequest):
    try:
        return await generate_explanation(request.problem)
    except Exception as e:
        logging.error(f"Error getting explanation: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/solutions", response_model=SolutionSection, tags=["Analysis Components"])
async def get_solutions(request: AnalyzeRequest):
    try:
        return await generate_solutions(request.problem)
    except Exception as e:
        logging.error(f"Error getting solutions: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resources", response_model=ResourcesSection, tags=["Analysis Components"])
async def get_resources(request: AnalyzeRequest):
    try:
        return await generate_resources(request.problem)
    except Exception as e:
        logging.error(f"Error getting resources: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/similar-problems", response_model=SimilarProblemsSection, tags=["Analysis Components"])
async def get_similar_problems(request: AnalyzeRequest):
    try:
        return await generate_similar_problems(request.problem)
    except Exception as e:
        logging.error(f"Error getting similar problems: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    try:
        return await generate_chat_response(
            problem_context=request.problem_context,
            chat_history=request.chat_history,
            user_message=request.user_message
        )
    except Exception as e:
        logging.error(f"Error in chat: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("To run the backend server, navigate to the 'backend' directory and use:")
    print("python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
