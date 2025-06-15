# Project Brief: LeetCode Problem Analyzer & Tutor

## 1. Project Goal

To develop a web application that assists users in understanding and solving LeetCode problems. The application will leverage a Large Language Model (LLM), specifically Gemini Pro 2.5, to provide in-depth analysis, solutions, further learning resources, and interactive chat support.

## 2. Core Requirements

The web application must:

*   **Accept LeetCode Problem Input:** Allow users to input a LeetCode problem, likely via its URL.
*   **Problem Analysis:** Perform a deep analysis of the submitted LeetCode problem. This includes understanding the problem statement, constraints, and underlying concepts.
*   **Multi-Language Solution Generation:** Provide clear, step-by-step, and intuitive solutions in Python, Java, and C++.
*   **In-Depth Explanation:** Offer a detailed walkthrough of the solution, including pattern analysis, intuition, and complexity analysis.
*   **High-Quality Reference Curation:** Identify and present links to 5 obscure but high-quality external resources for further learning.
*   **Similar Problem Suggestion:** Recommend 3 additional LeetCode problems that are similar in concept.
*   **Interactive Chat:** Implement a floating, minimizable chat interface for users to discuss the problem with the LLM.
*   **Response Caching:** Cache LLM responses to improve performance and reduce API costs.
*   **LLM-Driven Logic:** All core analytical and content generation logic will be driven by the Gemini Pro 2.5 LLM.

## 3. Technical Stack (Initial Proposal)

*   **Backend:** Python with FastAPI.
*   **Frontend:** Vanilla HTML, Materialize CSS, and JavaScript.
*   **LLM:** Gemini 1.5 Pro (via API integration).
*   **Data Source:** LeetCode GraphQL API.
*   **Version Control:** Git, with the repository hosted on GitHub.

## 4. Key Success Metrics (To be refined)

*   User satisfaction with the quality of analysis and solutions.
*   Effectiveness of the suggested resources and similar problems.
*   Engagement with the interactive chat feature.
*   Ease of use and intuitive interface.

## 5. Scope Considerations

*   **Initial Focus:** Core features as listed above.
*   **Future Enhancements (Out of initial scope):** User accounts, progress tracking, code execution/testing, support for multiple LLMs.
