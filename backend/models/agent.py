from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentRunResultContext:
    search_tool_results: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    search_queries: List[str] = field(default_factory=list)
    user_uploaded_files: List[str] = field(default_factory=list)
