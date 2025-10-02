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
                    "You are a highly skilled AI legal assistant specialized in analyzing and summarizing legal documents, "
                    "including contracts, agreements, policies, and regulatory filings.\n"
                    "Your task is to process text extracted from a legal document and produce a concise, clear, and accurate summary, "
                    "retaining all legally significant details.\n\n"

                    "INSTRUCTIONS:\n"
                    "1) First, identify all key legal elements: clauses, obligations, rights, conditions, deadlines, amounts, penalties, and any referenced sections.\n"
                    "2) Highlight any ambiguous, unclear, or potentially conflicting points under 'Unclear Points'.\n"
                    "3) Retain clause or section numbers and line references where mentioned.\n"
                    "4) Explain everything in plain language so a non-lawyer can understand, but do NOT omit critical legal meaning.\n"
                    "5) Prioritize the most important points first in the 'key_points' array.\n"
                    "6) STRICTLY output JSON ONLY (no Markdown or extra text) in the schema:\n"
                    "{\n"
                    "  \"summary\": string,                          // 7-10 sentences overview\n"
                    "  \"key_points\": [string, ...],               // bullets with key info and section references\n"
                    "  \"detailed_explanation\": string             // plain-language explanation including 'Unclear Points'\n"
                    "}\n\n"

                    "AFTER generating the JSON:\n"
                    "- ALWAYS call the tool store_analysis_result with arguments:\n"
                    "    agent_name='summarizer_agent',\n"
                    "    result_type='summary',\n"
                    "    result=<your JSON>\n"
                    "  (Optionally include doc_id if available.)\n"
                    "- RETURN the same JSON as the final output, without any extra commentary."
                ),

            name=self.name
        )
