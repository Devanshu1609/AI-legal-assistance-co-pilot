# agents/supervisor_agent.py
from langgraph.prebuilt import create_react_agent

class SupervisorAgent:
    def __init__(self, model="openai:gpt-4.1"):
        self.model = model
        self.name = "supervisor"
        self.description = (
            "Supervisor agent controls workflow execution. It decides the next agent "
            "based on the current state, results, and conversation context."
        )

    def create_agent(self):
        return create_react_agent(
            model=self.model,
            tools=[],  # Supervisor does not use external tools, only decides routing
            prompt=(
                "You are the Supervisor Agent for a legal document analysis workflow.\n"
                "Your job: decide which agent to call next based on the state and previous results.\n\n"
                "### AVAILABLE AGENTS:\n"
                "- document_processor_agent: Ingest and extract text from documents.\n"
                "- summarizer_agent: Summarize and simplify extracted text.\n"
                "- clause_explainer_agent: Explain individual clauses in detail.\n"
                "- risk_analysis_agent: Perform risk/compliance analysis.\n"
                "- report_generator_agent: Generate a final report based on all processed data.\n"
                "- end: Finish the workflow.\n\n"
                "### DECISION RULES:\n"
                "1. If the document is not yet processed, choose document_processor_agent.\n"
                "2. If text is processed but summary is missing, choose summarizer_agent.\n"
                "3. If summary exists but clauses are not explained, choose clause_explainer_agent.\n"
                "4. If clauses are explained but risk analysis not done, choose risk_analysis_agent.\n"
                "5. If all above are done, choose report_generator_agent.\n"
                "6. If everything is complete, choose end.\n\n"
                "### RESPONSE FORMAT:\n"
                "Return STRICT JSON ONLY:\n"
                "{\n"
                "  \"next_agent\": \"<one_of: document_processor_agent | summarizer_agent | clause_explainer_agent | risk_analysis_agent | report_generator_agent | end>\",\n"
                "  \"reason\": \"<short explanation of why you chose this agent>\"\n"
                "}\n\n"
                "NEVER return any text outside JSON.\n"
                "If you are unsure, choose 'end' with reason 'unclear state'.\n"
            ),
            name=self.name
        )
