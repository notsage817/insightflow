from __future__ import annotations
from agents import Agent

from models.agent import AgentRunResultContext
from services.tools import job_search_tool


job_search_agent = Agent[AgentRunResultContext](
    name="Job Search Agent",
    handoff_description="Specialist that searches for jobs and return the top matches.",
    instructions=(
        "You help users search job openings. "
        "Ask clarifying questions if the query is vague. "
        "Use the job_search_tool to fetch results. "
        "After calling the tool, append search query to context.search_queries. "
        "Then present the results as a Markdown-formatted list. "
        "Each job should be shown as a bullet point in the format: "
        "* <id> | [<title>](<url>) | <location> | <publish_date>. "
        "If publish_date is missing, omit it. "
        "Be factual; if no results, say so and suggest query tweaks."
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
        "- If the user is asking to tailor/modify a resume for a SPECIFIC job from recent results (e.g., 'modify my resume for JOB#102'), "
        "HAND OFF to Resume Modifier Agent.\n"
        "- Otherwise, answer as a helpful assistant (general chat), without calling tools or handoffs.\n\n"
        "# Important\n"
        "When handing off, provide a concise summary of the user request (context) to help the next agent. "
        "If needed, ask a brief clarifying question before choosing the agent.\n"
    ),
    # Router can delegate via handoffs:
    handoffs=[job_search_agent, job_followup_agent],
)
