from typing import TypedDict, List, Optional
from pydantic import Field
from langchain_core.messages import BaseMessage

#State model for the agent
class AgentState(TypedDict):
    extracted_text: str
    summary: Optional[str]
    clause_explanation: Optional[str]
    risk_analysis: Optional[str]
    report: Optional[str]   
    messages: List[BaseMessage]