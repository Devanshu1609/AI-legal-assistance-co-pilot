# agents/clause_explainer_agent.py
from langgraph.prebuilt import create_react_agent
from tools.analysis_storage_tool import AnalysisStorageTool

class ClauseExplainerAgent:
    def __init__(self, model: str = "openai:gpt-4.1", persist_directory: str = "vector_store"):
        self.model = model
        self.tools = AnalysisStorageTool(persist_directory).get_tools()
        self.name = "clause_explainer_agent"
        self.description = "Explains complex clauses and jargon in simple language with short, accurate explanations."

    def create_agent(self):
        return create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=(
                "You are ClauseExplainerAgent, an expert AI for simplifying complex legal or technical clauses.\n\n"
                "INPUT:\n"
                "- You will receive raw extracted text or a summary. Identify sentences/phrases/clauses that are complex.\n\n"
                "OUTPUT (STRICT JSON ONLY):\n"
                "{\n"
                "  \"simplified_clauses\": [\n"
                "     {\n"
                "       \"original_clause\": string,               // exact text snippet\n"
                "       \"simplified_explanation\": string        // short, plain-language explanation\n"
                "     },\n"
                "     ...\n"
                "  ]\n"
                "}\n\n"
                "RULES:\n"
                "- Keep explanations short, accurate, and easy to understand.\n"
                "- Do not speculate; only simplify what is explicitly present in the input.\n"
                "- If no complex clauses are found, return {\"simplified_clauses\": []}.\n\n"
                "AFTER you generate that JSON:\n"
                "- ALWAYS call store_analysis_result with:\n"
                "    agent_name='clause_explainer_agent',\n"
                "    result_type='clauses',\n"
                "    result=<your JSON>\n"
                "  (Optionally include doc_id if provided.)\n"
                "- Then RETURN the same JSON as your final answer.\n"
            ),
            name=self.name
        )
