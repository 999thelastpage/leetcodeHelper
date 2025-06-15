from pydantic import BaseModel, HttpUrl
from typing import List, Optional

# --- API Request Models ---

class AnalyzeRequest(BaseModel):
    """
    Request model for the new granular endpoints.
    It will contain the scraped problem data.
    """
    problem: 'ScrapedProblem'

class ChatRequest(BaseModel):
    """
    Request model for the /api/chat endpoint.
    """
    problem_context: str
    chat_history: List[dict] # e.g., [{"role": "user", "content": "..."}, {"role": "llm", "content": "..."}]
    user_message: str


# --- API Response Models ---

class Resource(BaseModel):
    """
    Model for a single learning resource, now with a reason.
    """
    title: str
    url: HttpUrl
    reason: str

class SimilarProblem(BaseModel):
    """
    Model for a single similar problem, now including a reason.
    """
    title: str
    url: HttpUrl
    reason: str

class SimilarProblemsSet(BaseModel):
    """
    Model for the categorized set of similar problems.
    """
    easy: List[SimilarProblem]
    medium: List[SimilarProblem]
    hard: List[SimilarProblem]

class SolutionSet(BaseModel):
    """
    Model for the set of solutions in different languages.
    """
    python: str
    java: str
    cpp: str

# --- New Granular API Response Models ---

class AnalysisSection(BaseModel):
    analysis: str

class ExplanationSection(BaseModel):
    explanation: str

class SolutionSection(BaseModel):
    solution: SolutionSet

class ResourcesSection(BaseModel):
    resources: List[Resource]

class SimilarProblemsSection(BaseModel):
    similar_problems: SimilarProblemsSet


class ChatResponse(BaseModel):
    """
    Response model for the /api/chat endpoint.
    """
    llm_reply: str


# --- Internal Models ---

class ScrapedProblem(BaseModel):
    """
    Model for the data scraped from a LeetCode problem page.
    """
    title: str
    description: str
    examples: str
    constraints: str
    tags: Optional[List[str]] = None

# Pydantic v2 automatically handles forward references, so this is no longer needed.
# AnalyzeRequest.update_forward_refs(ScrapedProblem=ScrapedProblem)
