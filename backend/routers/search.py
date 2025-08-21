import logging
import numpy as np
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from models.chat import (
    ChatRequest, ChatResponse, Conversation, Message, MessageRole, 
    ModelProvider, ModelInfo, FileUploadResponse
)
from services.conversation import conversation_manager
from services.llm import llm_service
from services.file_processor import file_processor
from pydantic import BaseModel, Field
import tritonclient.http as httpclient


# Request body model for the search query
class SearchRequest(BaseModel):
    text_to_embed: List[str] 
    es_query:Optional[Dict[str, Any]]
    k: int

# Response body model for the search results
class SearchResponse(BaseModel):
    results: str
    message: str

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/search", response_model=SearchResponse, summary="Perform a search using an inference model")
async def perform_search(request: SearchRequest):
    try:
        # Initialize the Inference Server Client
        # Adjust the URL to your actual Triton Inference Server address if different
        client = httpclient.InferenceServerClient(url="ensemble-model:8000")

        # Prepare the input data for the inference server
        # Ensure that `text_to_embed` is always a list for the numpy conversion
        # The first input (Query) expects [batch_size, sequence_length], so [1,1] for a single query.
        query_input = np.asarray([request.text_to_embed], dtype=object)

        # The ElasticsearchQuery expects [1] (batch size of 1) and bytes data
        es_query_input = np.array([json.dumps(request.es_query).encode('utf-8')], dtype=object)

        # The K input expects [1] (batch size of 1) and int32 data
        k_input = np.array([request.k], dtype=np.int32)

        inputs = [
            httpclient.InferInput("Query", [1,1], "BYTES"),
            httpclient.InferInput("ElasticsearchQuery", [1], "BYTES"),
            httpclient.InferInput("K", [1], "INT32")
        ]

        inputs[0].set_data_from_numpy(query_input)
        inputs[1].set_data_from_numpy(es_query_input)
        inputs[2].set_data_from_numpy(k_input)

        # Make the inference call to the 'searcher' model
        # You might need to add headers if your Triton server requires them
        response = client.infer(model_name='searcher', inputs=inputs)

        # Extract the 'Responses' output from the inference server's response
        raw_responses = response.as_numpy('Responses')

        if raw_responses is None:
            raise HTTPException(
                status_code=500,
                detail="Inference server did not return 'Responses' output or output was empty."
            )
        return SearchResponse(results=raw_responses[0], message="Search successful")

    except Exception as e:
        # Catch any errors during the process (e.g., network issues, Triton server errors)
        raise HTTPException(status_code=500, detail=f"Error communicating with inference server: {str(e)}")
