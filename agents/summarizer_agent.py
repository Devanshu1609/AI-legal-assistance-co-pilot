# agents/summarizer_agent.py
from langgraph.prebuilt import create_react_agent
from tools.analysis_storage_tool import AnalysisStorageTool

class SummarizerAgent:
    def __init__(self, model: str = "openai:gpt-4.1", persist_directory: str = "vector_store"):
        self.model = model
        self.tools = AnalysisStorageTool(persist_directory).get_tools()
        self.name = "summarizer_agent"
        self.description = "Summarizes extracted document text; highlights key points and explains content in plain language."

    def create_agent(self):
        return create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=(
                "You are an expert in summarizing and simplifying legal documents.\n"
                "You will receive text extracted from a legal document.\n"
                "Your job is to create a clear, descursive, and plain-language summary "
                "while keeping all critical legal details intact.\n\n"
                "INSTRUCTIONS:\n"
                "1) Identify key clauses, obligations, rights, important dates, amounts, and penalties.\n"
                "2) Explain them in plain language so a non-lawyer can understand.\n"
                "3) Retain any clause or section numbers if mentioned.\n"
                "4) If something is unclear or ambiguous, include it in the explanation as 'Unclear Points'.\n"
                "5) Produce STRICT JSON only (no markdown outside JSON) with the schema:\n"
                "{\n"
                "  \"summary\": string,                          // 3–5 sentences\n"
                "  \"key_points\": [string, ...],               // bullets of the most important info\n"
                "  \"detailed_explanation\": string             // plain-language explanation (can include 'Unclear Points')\n"
                "}\n\n"
                "AFTER you generate that JSON:\n"
                "- ALWAYS call the tool store_analysis_result with arguments:\n"
                "    agent_name='summarizer_agent',\n"
                "    result_type='summary',\n"
                "    result=<your JSON>\n"
                "  (Optionally include doc_id if provided in the user/system context.)\n"
                "- Then RETURN the same JSON as your final answer.\n"
            ),
            name=self.name
        )
