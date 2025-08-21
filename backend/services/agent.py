from __future__ import annotations
import asyncio
from typing import List, Dict, Any, Optional
import os
import json
import numpy as np
from dataclasses import dataclass
from agents import Agent
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from services.tools import job_search_tool

# Context setting up
@dataclass
class AppContext:
    last_jobs: List[Dict[str, Any]]
    user_resume_text: Optional[str] = None
    tool_results: Dict[str, Any] = None


job_search_agent = Agent[AppContext](
    name="Job Search Agent",
    handoff_description="Specialist that searches for jobs and return the top matches.",
    instructions=(
        "You help users search job openings. "
        "Ask clarifying questions if the query is vague. "
        "Use the job_search_tool to fetch results. "
        "After calling the tool, store the returned results into the context as `last_jobs`. "
        "Then present the results as a Markdown-formatted list. "
        "Each job should be shown as a bullet point in the format: "
        "* <id> | [<title>](<url>) | <location> | <publish_date>. "
        "If publish_date is missing, omit it. "
        "Be factual; if no results, say so and suggest query tweaks."
    ),
    tools=[job_search_tool],
)

# # --- Resume Modifier Agent ---
# resume_modifier_agent = Agent[AppContext](
#     name="Resume Modifier Agent",
#     handoff_description="Tailors a user's resume to a specific retrieved job and produces a PDF.",
#     instructions=(
#         "You tailor the user's resume to a SINGLE job from the last search results.\n"
#         "Rules:\n"
#         "1) If the user didn't specify a job ID that exists in context.last_jobs, ask them to pick one.\n"
#         "2) Use context.user_resume_text as the starting resume. If it's empty, ask the user to upload/paste it.\n"
#         "3) Extract the key requirements from the chosen job posting and rewrite the resume to highlight aligned skills and outcomes.\n"
#         "4) Keep truthful—DO NOT invent experience. Rephrase, reorder, and quantify existing items; add ATS-friendly keywords only if supported by the resume.\n"
#         "5) After you finish the tailored text, call resume_pdf_generator(modified_resume_markdown) to create a PDF. Then return the file path to the user.\n"
#         "Output style: short objective (optional), skills/tech stack, experience (bullets with quantified impact), education, and relevant projects.\n"
#     ),
#     tools=[assistant.resume_pdf_generator],
# )

# --- Router / Orchestrator Agent ---
ROUTER_AGENT = Agent[AppContext](
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
    handoffs=[job_search_agent],
)
