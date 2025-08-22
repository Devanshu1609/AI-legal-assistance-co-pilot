# graph/multi_agent_graph.py
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import AIMessage
import re

def _to_snake(name: str) -> str:
    # CamelCase or mixed → snake_case
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.replace("__", "_").lower()

class MultiAgentGraph:
    def __init__(self, agents: dict):
        self.agents = agents
        self.graph = StateGraph(MessagesState)

    def build_graph(self):
        for name, agent in self.agents.items():
            self.graph.add_node(name, agent)

        for name in self.agents.keys():
            if name != "supervisor":
                self.graph.add_edge(name, "supervisor")

        self.graph.add_edge(START, "supervisor")

        self.graph.add_conditional_edges(
            "supervisor",
            self.decide_next,
            {
                "document_processor_agent": "document_processor_agent",
                "summarizer_agent": "summarizer_agent",
                "clause_explainer_agent": "clause_explainer_agent",
                "risk_analysis_agent": "risk_analysis_agent",
                "report_generator_agent": "report_generator_agent",
                "end": END,
            }
        )

    def decide_next(self, state: MessagesState) -> str:
        last = state["messages"][-1]

        # Preferred path: use real tool call name
        if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
            tool_name = last.tool_calls[0]["name"]
            if tool_name.startswith("transfer_to_"):
                agent_name = tool_name.replace("transfer_to_", "")
                agent_name = _to_snake(agent_name)
                if agent_name in self.agents:
                    print(f"[Supervisor → {agent_name}] (tool)")
                    return agent_name

        # Fallback: parse plain text like "transfer_to_DocumentProcessorAgent"
        if isinstance(last, AIMessage):
            content = (last.content or "").strip()
            m = re.search(r"transfer_to_([A-Za-z0-9_]+)", content)
            if m:
                agent_name = _to_snake(m.group(1))
                if agent_name in self.agents:
                    print(f"[Supervisor → {agent_name}] (parsed text)")
                    return agent_name

        print("[Supervisor → END] No valid agent found.")
        return "end"

    def compile(self):
        return self.graph.compile()
