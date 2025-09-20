import streamlit as st
import os
import json
from agents.question_answer_agent import QAAgent
from tempfile import NamedTemporaryFile
import shutil
import asyncio

os.environ["SQLITE_EXPERIMENTAL"] = "true"
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

from agents.document_processor_agent import DocumentProcessorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.clause_explainer_agent import ClauseExplainerAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.report_generator_agent import ReportGeneratorAgent
from agents.supervisor_agent import SupervisorAgent
from graph.multi_agent_graph import MultiAgentGraph

st.set_page_config(page_title="AI Legal Assistant", layout="wide")
st.title("📄 AI Legal Assistant - Multi-Agent Pipeline")

# ------------------------------
# In-memory storage
# ------------------------------
processed_docs = {}

# ------------------------------
# Run multi-agent pipeline
# ------------------------------
async def run_pipeline(document_path: str):
    agents = {
        "document_processor_agent": DocumentProcessorAgent().create_agent(),
        "summarizer_agent": SummarizerAgent().create_agent(),
        "clause_explainer_agent": ClauseExplainerAgent().create_agent(),
        "risk_analysis_agent": RiskAnalysisAgent().create_agent(),
        "report_generator_agent": ReportGeneratorAgent().create_agent(),
        "supervisor": SupervisorAgent().create_agent(),
    }

    graph_builder = MultiAgentGraph(agents)
    graph_builder.build_graph()
    app_graph = graph_builder.compile()

    result = await app_graph.ainvoke({"messages": [("user", document_path)]})

    # Extract REPORT_GENERATOR_AGENT output
    final_report = None
    for msg in result.get("messages", []):
        if hasattr(msg, "name") and msg.name == "report_generator_agent":
            try:
                final_report = json.loads(msg.content)
            except json.JSONDecodeError:
                final_report = {"raw_output": msg.content}
            break

    if not final_report:
        return None
    return final_report

# ------------------------------
# Upload section
# ------------------------------
st.header("1️⃣ Upload Document")
uploaded_file = st.file_uploader("Upload a legal document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        shutil.copyfileobj(uploaded_file, tmp_file)
        tmp_file_path = tmp_file.name

    with st.spinner("Processing document..."):
        final_report = asyncio.run(run_pipeline(tmp_file_path))

        if final_report:
            st.success("✅ Report generated successfully!")
            st.subheader("Generated Report:")
            st.json(final_report)

            # Initialize QAAgent
            qa_agent = QAAgent(doc_id=tmp_file_path, persist_directory="vector_store")

            # Store in memory
            processed_docs[uploaded_file.name] = {
                "report": final_report,
                "qa_agent": qa_agent,
                "file_path": tmp_file_path
            }
        else:
            st.error("❌ Failed to generate report.")

# ------------------------------
# Ask questions
# ------------------------------
st.header("2️⃣ Ask Questions About Uploaded Document")
if processed_docs:
    selected_file = st.selectbox("Select a processed document", list(processed_docs.keys()))
    question = st.text_input("Enter your question:")

    if st.button("Ask"):
        if question.strip() == "":
            st.warning("Please enter a question.")
        else:
            qa_agent = processed_docs[selected_file]["qa_agent"]
            answer = qa_agent.answer(question)
            st.subheader("Answer:")
            st.write(answer)
else:
    st.info("Upload a document first to enable Q&A.")
