"""LiteLLM wrapper for LLM interactions."""

import os
from typing import List, Dict, Any, Optional, AsyncGenerator

from litellm import acompletion


async def get_llm_response(
    model: str,
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> AsyncGenerator:
    """
    Get a streaming response from the LLM.
    
    Args:
        model: Model identifier (e.g., "gemini/gemini-2.0-flash")
        messages: List of message dicts with role and content
        tools: Optional list of tool schemas
        **kwargs: Additional args passed to litellm
    
    Returns:
        Async generator yielding response chunks
    """
    # Ensure API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    
    call_kwargs = {
        "model": model,
        "messages": messages,
        "stream": True,
        **kwargs
    }
    
    if tools:
        call_kwargs["tools"] = tools
    
    response = await acompletion(**call_kwargs)
    return response
