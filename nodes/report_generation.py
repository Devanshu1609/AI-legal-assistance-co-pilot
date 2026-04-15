from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Literal
from state.agent_state import AgentState
from models.chat_model import llm_with_tools
from config import REPORT_GENERATOR_PATH
from config import TEMPERATURE, MAX_NEW_TOKENS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import init_chat_model


chat_model = init_chat_model("google_genai:gemini-2.5-flash")
lite_chat_model = init_chat_model("google_genai:gemini-2.5-flash-lite")

def report_generation(preferred_mode: Literal["chat_model","tools"]="chat_model" ):
    def report_generation(state: AgentState):
        """
        generates a report based on the analysis.
        """
        try:
            template = open(REPORT_GENERATOR_PATH).read()
        except FileNotFoundError:
            raise ValueError(f"Prompt file not found at {REPORT_GENERATOR_PATH}. Please check the path and try again.")

        try:
            # Create a prompt template for the report generation
            prompt_template = PromptTemplate(
                input_variables=["extracted_text", "summary" , "clause_explanation","risk_analysis"],
                template=template,
            )
            if preferred_mode == "chat_model":
                chain = prompt_template | chat_model
            else:
                chain = prompt_template | llm_with_tools
            response=chain.invoke({"extracted_text":state["extracted_text"],"summary":state["summary"],"clause_explanation":state["clause_explanation"],"risk_analysis":state["risk_analysis"]})
            print("Report generated:", response.content)
            if hasattr(response,"tool_calls") and response.tool_calls:
                return {"messages": [response]}
            else:
                return {"report":response.content,"messages": [response.content]}
        except Exception as e:
            raise ValueError(f"Error generating report : {e}")
    return report_generation