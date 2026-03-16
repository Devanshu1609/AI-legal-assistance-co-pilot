from langchain_core.prompts import PromptTemplate
from typing import Literal
from state.agent_state import AgentState
from models.chat_model import chat_model, llm_with_tools
from config import SUMMARIZER_PATH

def summarize(preferred_mode: Literal["chat_model","tools"]="chat_model"):

    def summarizer_agent(state: AgentState) -> AgentState:
        try:
            template = open(SUMMARIZER_PATH).read()
        except FileNotFoundError:
            raise ValueError(f"Prompt file missing at {SUMMARIZER_PATH}")

        prompt_template = PromptTemplate(
            input_variables=["extracted_text"],
            template=template,
        )

        chain = prompt_template | (chat_model if preferred_mode=="chat_model" else llm_with_tools)

        response = chain.invoke({
            "extracted_text": state["extracted_text"]
        })

        return {
            "summary": response.content,
            "messages": [response],
        }

    return summarizer_agent
