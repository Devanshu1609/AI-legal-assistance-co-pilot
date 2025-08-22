import asyncio
import json
from agents.document_processor_agent import DocumentProcessorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.clause_explainer_agent import ClauseExplainerAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.report_generator_agent import ReportGeneratorAgent
from agents.supervisor_agent import SupervisorAgent
from graph.multi_agent_graph import MultiAgentGraph

# ✅ Set the file path manually here
DOCUMENT_PATH = "complex_contract.pdf"  # Change as needed

async def run_pipeline(document_path: str):
    """
    Runs the multi-agent pipeline and only displays the final report in a clean way.
    """

    # ✅ 1. Initialize all agents
    agents = {
        "document_processor_agent": DocumentProcessorAgent().create_agent(),
        "summarizer_agent": SummarizerAgent().create_agent(),
        "clause_explainer_agent": ClauseExplainerAgent().create_agent(),
        "risk_analysis_agent": RiskAnalysisAgent().create_agent(),
        "report_generator_agent": ReportGeneratorAgent().create_agent(),
        "supervisor": SupervisorAgent().create_agent(),
    }

    # ✅ 2. Build and compile the graph
    graph_builder = MultiAgentGraph(agents)
    graph_builder.build_graph()
    app = graph_builder.compile()

    print(f"\n🚀 Starting Multi-Agent Workflow for: {document_path}\n")
    result = await app.ainvoke({"messages": [("user", document_path)]})

    print("\n✅ Workflow Completed.")
    print("\n📌 Extracting Final Report (REPORT_GENERATOR_AGENT)...\n")

    # ✅ 3. Find REPORT_GENERATOR_AGENT output
    final_report = None
    for msg in result.get("messages", []):
        if hasattr(msg, "name") and msg.name == "report_generator_agent":
            try:
                final_report = json.loads(msg.content)
            except json.JSONDecodeError:
                print("⚠ Could not parse report as JSON.")
                final_report = {"raw_output": msg.content}
            break

    if not final_report:
        print("❌ REPORT_GENERATOR_AGENT output not found.")
        return

    # ✅ 4. Pretty print final report
    print("🔹 Final Report Summary")
    print("=" * 90)
    print(f"📄 File: {final_report.get('file_name', 'N/A')}")
    print(f"📌 Overall Risk: {final_report.get('overall_risk_level', 'N/A').upper()} "
          f"(Score: {final_report.get('overall_risk_score', 'N/A')}/100)")
    print(f"📊 Total Risks Identified: {final_report.get('risks_count', 'N/A')}")
    print("\n✨ Key Highlights:")
    for i, highlight in enumerate(final_report.get("highlights", []), start=1):
        print(f"   {i}. {highlight}")

    print("\n📑 Report (Markdown Preview):")
    print("-" * 90)
    print(final_report.get("report_markdown", "No report content available."))
    print("=" * 90)

if __name__ == "__main__":
    asyncio.run(run_pipeline(DOCUMENT_PATH))
