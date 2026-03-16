from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import ToolMessage
from state.agent_state import AgentState

from nodes.summarizer import summarize
from nodes.clause_explainer import explain_clause
from nodes.risk_analyser import analyze_risk
from nodes.report_generation import report_generation
from tools.web_search_tool import web_search


def router(state: AgentState) -> str:
    messages = state.get("messages", [])
    last_msg = messages[-1] if messages else None

    pending = None
    for key in ["idea_analysis","market_analysis", "competition_analysis", "risk_assessment","swot_analysis"]:
        if state.get(key) is None:
            pending = key
            break

    if isinstance(last_msg, ToolMessage) and last_msg.content == "tool_failed":
        if pending == "summarize":
            return "summarize_fallback"
        if pending == "explain_clause":
            return "explain_clause_fallback"
        if pending == "analyze_risk":
            return "analyze_risk_fallback"
        if pending == "report_generation":
            return "report_generation_fallback"
        
    if pending == "summarize":
        return "summarize"
    if pending == "explain_clause":
        return "explain_clause"
    if pending == "analyze_risk":
        return "analyze_risk"
    if pending == "report_generation":
        return "report_generation"



def build_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("summarize", summarize("chat_model"))
    graph_builder.add_node("explain_clause", explain_clause("chat_model"))
    graph_builder.add_node("analyze_risk", analyze_risk("chat_model"))
    graph_builder.add_node("report_generation", report_generation("chat_model"))

    graph_builder.add_node("summarize_fallback", summarize("chat_model"))
    graph_builder.add_node("explain_clause_fallback", explain_clause("chat_model"))
    graph_builder.add_node("analyze_risk_fallback", analyze_risk("chat_model"))
    graph_builder.add_node("report_generation_fallback", report_generation("chat_model"))

    graph_builder.add_node("tools", ToolNode(tools=[web_search]))

    graph_builder.set_entry_point("summarize")

    graph_builder.add_conditional_edges(
        "summarize",
        tools_condition,
        {"tools": "tools", "__end__": "explain_clause"}
    )

    graph_builder.add_conditional_edges(
        "explain_clause",
        tools_condition,
        {"tools": "tools", "__end__": "analyze_risk"}
    )

    graph_builder.add_conditional_edges(
        "analyze_risk",
        tools_condition,
        {"tools": "tools", "__end__": "report_generation"}
    )

    graph_builder.add_conditional_edges("tools", router)

    graph_builder.add_edge("summarize_fallback", "explain_clause")
    graph_builder.add_edge("explain_clause_fallback", "analyze_risk")
    graph_builder.add_edge("analyze_risk_fallback", "report_generation")
    graph_builder.add_edge("report_generation_fallback", END)

    graph_builder.add_edge("report_generation", END)

    # ✔ No config here
    graph = graph_builder.compile()

    return graph
