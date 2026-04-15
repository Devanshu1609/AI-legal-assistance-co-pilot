from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from models.chat_model import llm_with_tools, chat_model
from state.agent_state import AgentState
from config import CLAUSE_EXPLAINER_PATH

def explain_clause(preferred_mode: Literal["chat_model", "tools"] = "chat_model"):

    def clause_explainer(state: AgentState) -> AgentState:
        try:
            template = open(CLAUSE_EXPLAINER_PATH).read()
        except FileNotFoundError:
            raise ValueError(f"Prompt file missing at {CLAUSE_EXPLAINER_PATH}")

        prompt_template = PromptTemplate(
            input_variables=["extracted_text"],
            template=template,
        )

        # IMPORTANT: always get a usable final text
        # Tools can run, but final result must always include market_analysis
        chain = prompt_template | chat_model

        print("Invoking Clause Explainer...")
        response = chain.invoke({"extracted_text": state["extracted_text"]})
        print("Clause Explainer completed.")

        return {
            "clause_explanation": response.content,
            "messages": [HumanMessage(state["extracted_text"]), response],
        }

    return clause_explainer
