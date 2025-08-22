# graph/multi_agent_graph.py
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import AIMessage
import json
import re

def _to_snake(name: str) -> str:
    """Convert CamelCase or mixed → snake_case"""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.replace("__", "_").lower()

class MultiAgentGraph:
    def __init__(self, agents: dict):
        """
        agents: dict where keys are agent names like:
        {
            "supervisor": supervisor_agent_instance,
            "document_processor_agent": agent_instance,
            ...
        }
        """
        self.agents = agents
        self.graph = StateGraph(MessagesState)

    def build_graph(self):
        # Add nodes for all agents
        for name, agent in self.agents.items():
            self.graph.add_node(name, agent)

        # Each specialized agent returns control to supervisor
        for name in self.agents.keys():
            if name != "supervisor":
                self.graph.add_edge(name, "supervisor")

        # Start → Supervisor
        self.graph.add_edge(START, "supervisor")

        # Conditional edges from Supervisor based on decision
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
        """
        Reads Supervisor's last message (must be strict JSON):
        {
          "next_agent": "<agent_name or END>",
          "reason": "<reason>"
        }
        """
        last_msg = state["messages"][-1]

        if isinstance(last_msg, AIMessage):
            content = (last_msg.content or "").strip()
            try:
                decision = json.loads(content)
                next_agent = decision.get("next_agent", "").strip()
                print(f"[Supervisor Decision] → {next_agent} | Reason: {decision.get('reason')}")
                return next_agent.lower() if next_agent else "end"
            except json.JSONDecodeError:
                print("[Error] Supervisor response not valid JSON. Ending workflow.")
                return "end"

        print("[Supervisor → END] No valid decision found.")
        return "end"

    def compile(self):
        return self.graph.compile()
