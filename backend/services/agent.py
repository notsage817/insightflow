from __future__ import annotations
import asyncio
from typing import List, Dict, Any, Optional
import os
import json
import numpy as np
from dataclasses import dataclass
from agents import Agent, Runner, function_tool, handoff, RunContext
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

# Context setting up
@dataclass
class AppContext:
    last_jobs: List[Dict[str, Any]]
    user_resume_text: Optional[str] = None
    tool_results: Dict[str, Any] = None


class resumeAssistant():
    def __init__(self, server = None):
        self.server = server
    
    def search(self, query: str, k:int) -> List[Dict[str, Any]]:
        client=httpclient.InferenceServerClient(url=self.server)

        inputs=[
            httpclient.InferInput("Query", [1,1], "BYTES"),
            httpclient.InferInput("ElasticsearchQuery", [1], "BYTES"),
            httpclient.InferInput("K",[1],"INT32")
        ]
        es_query = {}

        inputs[0].set_data_from_numpy(np.asarray([query], dtype=object))
        inputs[1].set_data_from_numpy(np.array([json.dumps(es_query).encode('utf-8')], dtype=object))
        inputs[2].set_data_from_numpy(np.array([k], dtype=np.int32))

        response=client.infer(model_name='searcher', inputs=inputs)
        results_tensor = response.as_numpy("Responses")
        results = [json.loads(r) for r in results_tensor]
        
        return results

    @staticmethod
    def _write_pdf(path: str, text: str):
        # Simple PDF via reportlab

        c = canvas.Canvas(path, pagesize=LETTER)
        width, height = LETTER
        x, y = 50, height - 50
        for line in text.splitlines():
            c.drawString(x, y, line[:120])  # naive wrap
            y -= 14
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()

    @function_tool
    def job_search_tool(self, query: str):
        """
        Search for job openings related to the user's query.
        Returns a list of strings in format of dictionary
        """
        results = self.search(query)
        # derive simple IDs; in practice, use stable IDs from your system
        return results

    @function_tool
    def resume_pdf_generator(self, modified_resume_markdown: str, filename: str = "tailored_resume.pdf") -> Dict[str, str]:
        """
        Convert the agent's modified resume (markdown or plain text) into a PDF file and return a path.
        """
        # You can add markdown->text rendering if you like; here we'll just write plain text.
        path = os.path.abspath(filename)
        self._write_pdf(path, modified_resume_markdown)
        return {"pdf_path": path}

# --- Job Search Agent ---
server = "ensemble-model:8000"
assistant = resumeAssistant(server)

job_search_agent = Agent[AppContext](
    name="Job Search Agent",
    handoff_description="Specialist that searches for jobs and return the top matches.",
    instructions=(
        "You help users search job openings. "
        "Ask clarifying questions if the query is vague. "
        "Use the job_search_tool to fetch results. "
        "After calling the tool, store the returned results into the context as `last_jobs`. "
        "Then present a concise, numbered list of matches with IDs (e.g., JOB#101) and brief rationale. "
        "Be factual; if no results, say so and suggest query tweaks."
    ),
    tools=[assistant.job_search_tool],
    # After the tool call, we capture results into context via a lifecycle hook:
    on_tool_result = lambda ctx, tool_name, args_json, response: (
    # Parse the tensor into Python dicts
    setattr(ctx, "last_jobs", response),
    # Save structured results for later tool calls
    setattr(ctx, "tool_results", {
            **getattr(ctx, "tool_results", {}),
            tool_name: response
        }
    )
)
)

# --- Resume Modifier Agent ---
resume_modifier_agent = Agent[AppContext](
    name="Resume Modifier Agent",
    handoff_description="Tailors a user's resume to a specific retrieved job and produces a PDF.",
    instructions=(
        "You tailor the user's resume to a SINGLE job from the last search results.\n"
        "Rules:\n"
        "1) If the user didn't specify a job ID that exists in context.last_jobs, ask them to pick one.\n"
        "2) Use context.user_resume_text as the starting resume. If it's empty, ask the user to upload/paste it.\n"
        "3) Extract the key requirements from the chosen job posting and rewrite the resume to highlight aligned skills and outcomes.\n"
        "4) Keep truthful—DO NOT invent experience. Rephrase, reorder, and quantify existing items; add ATS-friendly keywords only if supported by the resume.\n"
        "5) After you finish the tailored text, call resume_pdf_generator(modified_resume_markdown) to create a PDF. Then return the file path to the user.\n"
        "Output style: short objective (optional), skills/tech stack, experience (bullets with quantified impact), education, and relevant projects.\n"
    ),
    tools=[assistant.resume_pdf_generator],
)

# --- Router / Orchestrator Agent ---
router_agent = Agent[AppContext](
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
    handoffs=[job_search_agent, resume_modifier_agent],
)

# =========================
# Running the app
# =========================

async def run_conversation(messages: List[str], user_resume_text: Optional[str] = None):
    """
    messages: a list of user messages forming the conversation; we start at the router every time.
    user_resume_text: the user's uploaded resume as text.
    """
    ctx = AppContext(last_jobs=[], user_resume_text=user_resume_text)

    # Use streaming in a UI; here we keep it simple.
    result = await Runner.run(router_agent, messages, context=ctx)

    # The result contains the final message + trace; you can inspect handoffs, tool calls, etc.
    print("----- FINAL OUTPUT -----")
    print(result.final_output)

    # If a PDF was generated, you could parse the tool results to extract its path:
    # for ev in result.events: print(ev)

if __name__ == "__main__":

    # Example 1: user asks to search jobs
    convo1 = ["Hi! I'm looking for machine learning roles that use LLMs."]
    asyncio.run(run_conversation(convo1))


    # Example 2: user asks to tailor resume to a retrieved job (after they saw results)
    # user_resume = """Eddy Wang
    #                 Summary: Software engineer with 5+ years in search & retrieval...
    #                 Skills: Python, Elasticsearch, Triton, RAG, LLM tool use
    #                 Experience:
    #                 - Built BM25 + vector hybrid retrieval that improved P@10 by 18%...
    #                 Projects:
    #                 - Resume-tailor: tool that aligns resumes to JDs with ATS keywords...
    #                 """
    # convo2 = ["Can you tailor my resume for JOB#102 and make a PDF?"]
    # asyncio.run(run_conversation(convo2, user_resume_text=user_resume))
