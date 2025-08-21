import os
from typing import Any, Dict, List
from agents import function_tool
import tritonclient.http as httpclient
import numpy as np
import json


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
def job_search_tool(query: str, k: int) -> List[Dict[str, Any]]:
    """
    Search for job openings related to the given query.

    This function queries the job search backend to retrieve up to ``k`` 
    job postings that are most relevant to the provided search query. 

    Args:
        query (str): The user's search query (e.g., job title, skills, or keywords).
        k (int): The maximum number of job results to return.

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

    Example:
        >>> job_search_tool("machine learning engineer", 1)
        [
            {
                "title": "AIML-Sr. Machine Learning Engineer, Measurement",
                "url": "https://jobs.apple.com/en-us/details/200580040/aiml-sr-machine-learning-engineer-measurement?team=SFTWR",
                "job": {
                    "job_id": "200580040",
                    "title": "AIML-Sr. Machine Learning Engineer, Measurement",
                    "company": "Apple Inc.",
                    "description": "In this role, the individual is expected to lead and grow...",
                    "summary": "Apple Intelligence is on the lookout for an experienced...",
                    "location": "Seattle, Washington, United States",
                    "city": "Seattle",
                    "state": "Washington",
                    "country": "United States",
                    "work_arrangement": "remote",
                    "publish_date": "2025-02-27",
                    "job_type": "full_time",
                    "experience_level": "senior_level",
                    "salary_min": 201300.0,
                    "salary_max": 367400.0,
                    "salary_currency": "USD",
                    "required_skills": ["leadership", "PyTorch", "TensorFlow", "Python"],
                    "minimum_qualifications": [
                        "Bachelor’s degree in Computer Science...",
                        "5+ years of experience in machine learning..."
                    ],
                    "preferred_qualifications": [
                        "Master’s or PhD in STEM.",
                        "Experience with distributed systems..."
                    ],
                    "application_url": "https://jobs.apple.com/app/en-us/apply/200580040",
                    "source_platform": "jobs.apple.com"
                },
                "score": 0.79991716
            }
        ]
    """
    results = SEARCHER.search(query=query, k=k)
    return results

