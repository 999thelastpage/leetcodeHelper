import requests
import json
from bs4 import BeautifulSoup
from app.models import ScrapedProblem

def get_problem_slug(url: str) -> str:
    """Extracts the problem's title slug from its URL."""
    parts = url.strip('/').split('/')
    return parts[-1]

def scrape_leetcode_problem(url: str) -> ScrapedProblem:
    """
    Fetches LeetCode problem details using its GraphQL API.
    This is more robust than HTML scraping.

    Args:
        url: The URL of the LeetCode problem.

    Returns:
        A ScrapedProblem object containing the problem details.
        
    Raises:
        Exception: If the API call fails or the response is invalid.
    """
    slug = get_problem_slug(url)
    graphql_url = "https://leetcode.com/graphql"
    
    query = """
    query questionData($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
            title
            content
            topicTags {
                name
            }
        }
    }
    """
    
    variables = {
        "titleSlug": slug
    }
    
    payload = {
        "query": query,
        "variables": variables
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Referer': url,
    }

    try:
        response = requests.post(graphql_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL API returned errors: {data['errors']}")

        question_data = data.get("data", {}).get("question")
        if not question_data:
            raise Exception("Could not find question data in GraphQL response.")

        # The 'content' is HTML, so we use BeautifulSoup to extract text parts.
        soup = BeautifulSoup(question_data.get("content", ""), 'html.parser')
        full_text = soup.get_text('\n', strip=True)

        # Heuristics to separate description, examples, and constraints from the text
        description = ""
        examples = ""
        constraints = ""
        try:
            if "Example 1:" in full_text:
                description = full_text.split("Example 1:")[0].strip()
                examples_and_constraints = full_text.split("Example 1:")[1]
                
                if "Constraints:" in examples_and_constraints:
                    examples = "Example 1:" + examples_and_constraints.split("Constraints:")[0].strip()
                    constraints = "Constraints:" + examples_and_constraints.split("Constraints:")[1].strip()
                else:
                    examples = "Example 1:" + examples_and_constraints.strip()
            else:
                description = full_text
        except Exception:
            description = full_text
            examples = "Could not parse examples from content."
            constraints = "Could not parse constraints from content."

        tags = [tag['name'] for tag in question_data.get("topicTags", [])]

        return ScrapedProblem(
            title=question_data.get("title", "Title not found"),
            description=description,
            examples=examples,
            constraints=constraints,
            tags=tags if tags else None
        )

    except requests.RequestException as e:
        raise Exception(f"Failed to call LeetCode GraphQL API: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while processing the GraphQL response: {e}")


if __name__ == '__main__':
    # Example usage for testing
    test_url = "https://leetcode.com/problems/two-sum/"
    try:
        problem_data = scrape_leetcode_problem(test_url)
        print("--- GRAPHQL API DATA ---")
        print(f"Title: {problem_data.title}")
        print(f"\nDescription:\n{problem_data.description}")
        print(f"\nExamples:\n{problem_data.examples}")
        print(f"\nConstraints:\n{problem_data.constraints}")
        print(f"\nTags: {problem_data.tags}")
    except Exception as e:
        print(f"An error occurred: {e}")
