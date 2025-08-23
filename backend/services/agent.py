from __future__ import annotations
from agents import Agent

from models.agent import AgentRunResultContext
from services.tools import job_search_tool


job_search_agent = Agent[AgentRunResultContext](
    name="Job Search Agent",
    handoff_description="Specialist that searches for jobs and returns the top matches.",
    instructions=(
        "You help users search job openings.\n\n"
        "Use the user's written query and, if present, any uploaded file content (resume, skills list, etc.) "
        "to build a comprehensive search query. "
        "If no uploaded file exists, use only the user's query.\n\n"
        "Steps:\n"
        "1. If the request is vague, ask clarifying questions first.\n"
        "2. When ready, call `job_search_tool` with a query that combines:\n"
        "   - The user's explicit request.\n"
        "   - The uploaded file content, if available.\n"
        "3. The number of results to be returned, by default is 10, otherwise use the number user requested as k.\n"
        "4. After calling the tool, append the exact search query you used to `context.search_queries`.\n"
        "5. Present results as a Markdown-formatted list:\n"
        "   * <id> | [<title>](<url>) | <location> | <publish_date>\n"
        "   (omit publish_date if missing).\n\n"
        "Be factual: if no results, say so and suggest refinements to the query."
    ),
    tools=[job_search_tool],
)

job_followup_agent = Agent[AgentRunResultContext](
    name="Job Follow-up Agent",
    handoff_description="Answers follow-up questions about specific jobs from the last search.",
    instructions=(
        "You answer follow-up questions about jobs that were returned in the most recent search.\n\n"
        "How to proceed:\n"
        "1. Retrieve the last search query from `context.search_queries[-1]`.\n"
        "2. Get the search results for that query from `context.search_tool_results[search_query]`.\n"
        "3. Find the job that matches the job_id or title or other information mentioned in the user’s question.\n"
        "4. Provide answer for user's question based on matched job information\n\n"
        "If no job match found in the last search results, politely inform the user and suggest running a new search."
    ),
)


# --- Router / Orchestrator Agent ---
ROUTER_AGENT = Agent[AgentRunResultContext](
    name="Router",
    instructions=(
        "# Role\n"
        "You are the first agent in the conversation. Your job is to understand intent and decide:\n"
        "- If the user is asking about job search (e.g., 'find ML jobs', 'search roles in SF'), HAND OFF to Job Search Agent.\n"
        "- If the user is aksing a follow-up question about one of jobs in search tool result, HAND OFF to Job Follow-up Agent.\n"
        "- Otherwise, answer as a helpful assistant (general chat), without calling tools or handoffs.\n\n"
        "# Important\n"
        "When handing off, provide a concise summary of the user request (context) to help the next agent. "
        "If needed, ask a brief clarifying question before choosing the agent.\n"
    ),
    # Router can delegate via handoffs:
    handoffs=[job_search_agent, job_followup_agent],
)