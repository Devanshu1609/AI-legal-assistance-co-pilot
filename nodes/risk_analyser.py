from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Literal
from state.agent_state import AgentState
from models.chat_model import llm_with_tools,chat_model
from config import RISK_ANALYSER_PATH

def analyze_risk(preferred_mode: Literal["chat_model","tools"]="chat_model" ):
    def risk_analyzation(state: AgentState):
        """
        analyzes competition and provide insights.
        """
        try:
            template = open(RISK_ANALYSER_PATH).read()
        except FileNotFoundError:
            raise ValueError(f"Prompt file not found at {RISK_ANALYSER_PATH}. Please check the path and try again.")

        try:
            # Create a prompt template for the risk analysis
            prompt_template = PromptTemplate(
                input_variables=["extracted_text", "summary" , "clause_explanation"],
                template=template,
            )
            if preferred_mode == "chat_model":
                chain = prompt_template | chat_model
            else:
                chain = prompt_template | llm_with_tools
            response=chain.invoke({"extracted_text":state["extracted_text"],"summary":state["summary"],"clause_explanation":state["clause_explanation"]})
            if hasattr(response,"tool_calls") and response.tool_calls:
                return {"messages": [response]}
            else:
                return {"risk_analysis":response.content,"messages": [response.content]}
        except Exception as e:
            raise ValueError(f"Error analyzing risk : {e}")
    return risk_analyzation