import os
from typing import Any, Dict, List
from agents import RunContextWrapper, function_tool
import tritonclient.http as httpclient
import numpy as np
import json

from models.agent import AgentRunResultContext


TRITON_ENDPOINT_ENV = "TRITON_ENDPOINT"

class Searcher:
    def __init__(self, url: str):
        self.client=httpclient.InferenceServerClient(url=url)
    

    def search(self, query: str, k: int, es_query: str = {}) -> List[Dict[str, Any]]:
        inputs = [
            httpclient.InferInput("Query", [1, 1], "BYTES"),
            httpclient.InferInput("ElasticsearchQuery", [1], "BYTES"),
            httpclient.InferInput("K", [1], "INT32")
        ]

        inputs[0].set_data_from_numpy(np.asarray([[query]], dtype=object))
        inputs[1].set_data_from_numpy(np.array([json.dumps(es_query).encode('utf-8')], dtype=object))
        inputs[2].set_data_from_numpy(np.array([k], dtype=np.int32))

        response = self.client.infer(model_name='searcher', inputs=inputs)
        responses = response.as_numpy('Responses')

        results = [json.loads(f) for f in responses]
        return results
    
# Gloabl instance
SEARCHER = Searcher(url=os.getenv(TRITON_ENDPOINT_ENV))


# OpenAI function tool uses Python doc string to understand how to use the tool:
# https://openai.github.io/openai-agents-python/tools/#function-tools
@function_tool
def job_search_tool(wrapper: RunContextWrapper[AgentRunResultContext], query: str, k: int) -> List[Dict[str, Any]]:
    """
    Search for job openings related to the given query and store results in shared context.

    This function queries the job search backend to retrieve up to ``k`` 
    job postings that are most relevant to the provided search query. 

    In addition to returning results directly, this function also updates
    the shared run context ``wrapper.context.search_tool_results`` by
    mapping the input ``query`` string to the retrieved list of job postings.
    This allows other agents or tools to reuse the search results later
    without re-running the query.

    Args:
        wrapper (RunContextWrapper[AgentRunResultContext]): 
            Provides access to the shared run context object. The field
            ``wrapper.context.search_tool_results`` is updated with the results.
        query (str): 
            The user's search query (e.g., job title, skills, or keywords).
        k (int): 
            The maximum number of job results to return.

    Returns:
        List[Dict[str, Any]]: 
            A list of job posting results. Each result contains:
            
            - **title** (str): Job title.  
            - **url** (str): Direct URL to the job posting.  
            - **job** (dict): Detailed job information, which may include:  
                - **job_id** (str): Unique job identifier.  
                - **title** (str): Job title (duplicate of top-level title).  
                - **company** (str): Company name.  
                - **description** (str): Full job description text.  
                - **summary** (str): Short job summary.  
                - **location** (str): Human-readable job location.  
                - **city**, **state**, **country** (str): Structured location fields.  
                - **work_arrangement** (str): e.g., "remote", "onsite", "hybrid".  
                - **publish_date** (str): ISO date string for posting date.  
                - **job_type** (str): e.g., "full_time", "part_time".  
                - **experience_level** (str): e.g., "entry_level", "senior_level".  
                - **salary_min**, **salary_max** (float): Salary range (if available).  
                - **salary_currency** (str): Currency code (e.g., "USD").  
                - **required_skills** (List[str]): Essential skills required.  
                - **preferred_skills** (List[str]): Optional/nice-to-have skills.  
                - **minimum_qualifications** (List[str]): Required qualifications.  
                - **preferred_qualifications** (List[str]): Optional qualifications.  
                - **application_url** (str): URL for applying.  
                - **source_platform** (str): Source site/platform name.  
            - **score** (float): Relevance score from the search engine.

    Side Effects:
        Updates ``wrapper.context.search_tool_results`` with an entry:
        
        .. code-block:: python

            wrapper.context.search_tool_results[query] = <results>
        
        where ``<results>`` is the returned list of job postings.

    Example:
        >>> job_search_tool(wrapper, "machine learning engineer", 1)
        [
            {
                "title": "AIML-Sr. Machine Learning Engineer, Measurement",
                "url": "https://jobs.apple.com/en-us/details/200580040/...",
                "job": { ... },
                "score": 0.79991716
            }
        ]
    """
    results = SEARCHER.search(query=query, k=k)
    # Add query -> search results to local context for agents:
    # https://openai.github.io/openai-agents-python/context/#local-context
    wrapper.context.search_tool_results[query] = results
    return results
