# agents/supervisor_agent.py
from tools.handoff_tool import create_handoff_tool
from langgraph.prebuilt import create_react_agent

class SupervisorAgent:
    def __init__(self, model="openai:gpt-4.1", agents=[]):
        self.model = model
        self.agents = agents  # list of descriptors with .name (snake_case) and .description

    def create_agent(self):
        tools = []
        tool_lines = []
        for a in self.agents:
            tools.append(create_handoff_tool(
                agent_name=a.name,
                description=f"Assign task to {a.name}. {getattr(a, 'description', '')}"
            ))
            tool_lines.append(f"- `{a.name}` → call tool `transfer_to_{a.name}`: {getattr(a, 'description', '')}")

        prompt = (
             "You are the SupervisorAgent. Your ONLY job is to delegate tasks to the correct specialized agent.\n\n"
        "AVAILABLE AGENTS:\n"
        "- DocumentProcessorAgent: Extracts and processes text from documents.\n"
        "- SummarizerAgent: Summarizes extracted text into easy-to-read language.\n"
        "- ClauseExplainerAgent: Explains complex clauses and legal jargon.\n"
        "- RiskAnalysisAgent: Identifies risks (legal, financial, compliance) and mitigation strategies.\n"
        "- ReportGeneratorAgent: Combines all analysis into a structured final report.\n\n"
        "RULES:\n"
        "- ALWAYS delegate tasks sequentially.\n"
        "- NEVER attempt to do the task yourself.\n"
        "- YOU MUST call ONLY ONE transfer_to_* tool in each response.\n"
        "- Do NOT call multiple tools at once. Wait for the result of one agent before moving to the next.\n\n"
        "After completing all required steps, return the final report or end the process.\n"
        )

        return create_react_agent(
            model=self.model,
            tools=tools,
            prompt=prompt,
            name="supervisor"
        )
