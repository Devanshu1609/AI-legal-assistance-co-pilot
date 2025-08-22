# main.py
import os
import json
from dotenv import load_dotenv

# Tools (for direct ingestion)
from tools.document_processor import DocumentProcessorTools

# Agents
from agents.summarizer_agent import SummarizerAgent
from agents.clause_explainer_agent import ClauseExplainerAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.report_generator_agent import ReportGeneratorAgent

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "Set OPENAI_API_KEY in your environment."

# --- Local file for testing (change if needed) ---
TEST_FILE_PATH = r"C:\Users\Devanshu Kumar singh\codebase\AI-legal-assistance-co-pilot\sample_contract.pdf"
PERSIST_DIR = "vector_store"


def get_last_ai_content(invoke_result) -> str:
    """
    Helper: extract the last AI message content from a create_react_agent .invoke() result.
    """
    msgs = invoke_result.get("messages", [])
    for msg in reversed(msgs):
        # LangGraph messages usually have .type == "ai"
        mtype = getattr(msg, "type", getattr(msg, "role", "ai"))
        if mtype in ("ai", "assistant"):
            content = getattr(msg, "content", None)
            if content:
                return content
    return ""


def run_agent(agent_runnable, user_content: str) -> str:
    """
    Helper: uniformly call any create_react_agent runnable with a user message and get AI content.
    """
    result = agent_runnable.invoke({"messages": [("user", user_content)]})
    return get_last_ai_content(result)


if __name__ == "__main__":
    print("[INFO] Initializing direct pipeline (no Supervisor/Q&A)...")

    # --- 1) Ingest document & extract text (direct tool call; no LLM) ---
    if not os.path.exists(TEST_FILE_PATH):
        raise FileNotFoundError(f"File not found: {TEST_FILE_PATH}")

    print("[INFO] Ingesting & extracting text...")
    dp_tools = DocumentProcessorTools(persist_directory=PERSIST_DIR)
    ingest = dp_tools.process_document(TEST_FILE_PATH)

    if "error" in ingest:
        raise RuntimeError(ingest["error"])

    file_name = ingest.get("file_name") or os.path.basename(TEST_FILE_PATH)
    vector_db_path = ingest.get("vector_db_path", PERSIST_DIR)
    extracted_text = ingest.get("extracted_text", "").strip()

    if not extracted_text:
        raise RuntimeError("No text extracted from the document.")

    # --- 2) Initialize agents (create_ract_agent runnables) ---
    print("[INFO] Initializing analysis agents...")
    summarizer = SummarizerAgent().create_agent()
    clause_explainer = ClauseExplainerAgent().create_agent()
    risk_analyzer = RiskAnalysisAgent().create_agent()
    report_generator = ReportGeneratorAgent().create_agent()

    # --- 3) Summarize ---
    print("[INFO] Running summarizer...")
    summary_raw = run_agent(summarizer, extracted_text)
    try:
        summary_json = json.loads(summary_raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"Summarizer returned non-JSON:\n{summary_raw}")

    # --- 4) Clauses (can use either raw text or summary; we pass raw text) ---
    print("[INFO] Explaining complex clauses...")
    clauses_raw = run_agent(clause_explainer, extracted_text)
    try:
        clauses_json = json.loads(clauses_raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"Clause explainer returned non-JSON:\n{clauses_raw}")

    # --- 5) Risk analysis (feed a structured JSON bundle as input) ---
    print("[INFO] Running risk analysis...")
    risk_input = {
        "extracted_text": extracted_text,
        "summary": summary_json.get("summary", ""),
        "simplified_clauses": clauses_json.get("simplified_clauses", []),
    }
    risk_raw = run_agent(risk_analyzer, json.dumps(risk_input))
    try:
        risk_json = json.loads(risk_raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"Risk analysis returned non-JSON:\n{risk_raw}")

    # --- 6) Report generation (compose all parts; agent expects a JSON blob string) ---
    print("[INFO] Generating final report...")
    report_input = {
        "file_name": file_name,
        "vector_db_path": vector_db_path,
        "extracted_text": "",  # not necessary to include full text in the report input
        "summary": summary_json.get("summary", ""),
        "key_points": summary_json.get("key_points", []),
        "detailed_explanation": summary_json.get("detailed_explanation", ""),
        "simplified_clauses": clauses_json.get("simplified_clauses", []),
        "risk_assessment": risk_json,
    }
    report_raw = run_agent(report_generator, json.dumps(report_input))
    try:
        report_json = json.loads(report_raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"Report generator returned non-JSON:\n{report_raw}")

    # --- 7) Print final Markdown report ---
    print("\n=== Final Report (Markdown) ===\n")
    print(report_json.get("report_markdown", ""))

    # Also show quick summary line items
    print("\n=== Highlights ===")
    for h in report_json.get("highlights", []):
        print(f"- {h}")

    print("\n=== Meta ===")
    print(f"File: {report_json.get('file_name', file_name)}")
    print(f"Overall Risk: {report_json.get('overall_risk_level', 'unknown')} "
          f"({report_json.get('overall_risk_score', 0)}/100)")
    print(f"Risks Count: {report_json.get('risks_count', 0)}")
