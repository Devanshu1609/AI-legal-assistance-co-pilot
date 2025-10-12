import os
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from tools.analysis_storage_tool import AnalysisStorageTool
from tools.document_processor import DocumentProcessorTools


class QAAgent:
    """
    Legal Question-Answering Agent that:
    - Retrieves both raw document chunks and AI-generated analyses (summary, risk, clauses)
    - Synthesizes context intelligently
    - Answers legal questions with citations and reasoning
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        persist_directory: str = "vector_store",
        doc_id: Optional[str] = None,
        k: int = 6,
        temperature: float = 0.2,
        max_history: int = 6,
    ):
        self.model_name = model
        self.doc_id = doc_id
        self.k = k
        self.temperature = temperature
        self.max_history = max_history

        # ---------------- LLM ----------------
        self.llm = ChatOpenAI(model=model, temperature=temperature)

        # ---------------- Vector Stores ----------------
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # 1️⃣ From Analysis Results (summaries, risks, clauses)
        self.analysis_tool = AnalysisStorageTool(persist_directory)
        self.analysis_vs = self.analysis_tool.vs

        # 2️⃣ From Original Documents
        self.doc_vs = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )

        # -------------- Retriever Setup --------------
        self.analysis_retriever = self.analysis_vs.as_retriever(search_kwargs={"k": k})
        self.doc_retriever = self.doc_vs.as_retriever(search_kwargs={"k": k})

        # Conversation memory
        self.history: List[Any] = []
        self._doc_id_candidates = self._normalize_doc_ids(doc_id)

    # ============================================================
    #                         PROMPTS
    # ============================================================
    @property
    def _system_prompt(self) -> str:
        return (
            "You are LegalQA, an expert AI assistant specialized in analyzing legal documents.\n"
            "Use the provided CONTEXT (which may include raw document text, summaries, clauses, and risk analyses)\n"
            "to answer the user's question accurately and transparently.\n\n"
            "Guidelines:\n"
            "1. Use only the facts present in CONTEXT — do NOT fabricate information.\n"
            "2. If the answer isn't clearly supported, say 'The document does not specify'.\n"
            "3. When referencing a clause or summary, prefix with [C1], [R2], etc. for traceability.\n"
            "4. Prefer summaries and clauses for direct answers, but quote the raw document text for precision.\n"
            "5. Keep tone: professional, clear, and legally accurate.\n"
            "6. If user’s query is about obligations, penalties, or risks — prioritize 'risk_analysis' context.\n"
        )

    # ============================================================
    #                    CONTEXT FORMATTING
    # ============================================================
    def _format_context(self, label: str, docs: List[Any]) -> str:
        if not docs:
            return f"({label}: no context)\n"
        formatted = []
        for i, d in enumerate(docs):
            meta = d.metadata or {}
            src = (
                meta.get("source")
                or meta.get("file_name")
                or meta.get("doc_id")
                or "unknown"
            )
            doc_type = meta.get("type", "raw")
            formatted.append(
                f"[{label}{i+1}] ({doc_type}, src={src})\n{d.page_content.strip()}\n"
            )
        return "\n".join(formatted)

    def _normalize_doc_ids(self, raw_id: Optional[str]) -> set:
        if not raw_id:
            return set()
        bn = os.path.basename(raw_id)
        return {raw_id, bn, os.path.splitext(bn)[0]}

    def _doc_matches(self, metadata: dict) -> bool:
        if not self.doc_id or not self._doc_id_candidates:
            return True
        for key in ("doc_id", "source", "file_name", "source_id", "source_filename"):
            val = metadata.get(key)
            if not val:
                continue
            vals = val if isinstance(val, (list, tuple)) else [val]
            if any(cand in str(v) for cand in self._doc_id_candidates for v in vals):
                return True
        return False

    # ============================================================
    #                       MAIN ANSWER LOGIC
    # ============================================================
    def answer(self, question: str) -> str:
        """
        Retrieve relevant analyses + raw text and synthesize an answer.
        """

        # Step 1️⃣ — Retrieve analysis-based context
        try:
            analysis_docs = self.analysis_retriever.get_relevant_documents(question)
        except Exception as e:
            analysis_docs = []
            print(f"[WARN] Analysis retrieval failed: {e}")

        # Step 2️⃣ — Retrieve raw document context
        try:
            raw_docs = self.doc_retriever.get_relevant_documents(question)
        except Exception as e:
            raw_docs = []
            print(f"[WARN] Document retrieval failed: {e}")

        # Step 3️⃣ — Filter by doc_id if applicable
        if self.doc_id:
            analysis_docs = [d for d in analysis_docs if self._doc_matches(d.metadata)]
            raw_docs = [d for d in raw_docs if self._doc_matches(d.metadata)]

        # Step 4️⃣ — Format context
        analysis_context = self._format_context("A", analysis_docs)
        raw_context = self._format_context("D", raw_docs)
        context_combined = (
            f"--- ANALYSIS CONTEXT ---\n{analysis_context}\n\n"
            f"--- RAW DOCUMENT CONTEXT ---\n{raw_context}"
        )

        # Step 5️⃣ — Build messages
        messages = [
            SystemMessage(content=self._system_prompt),
            *self.history[-self.max_history:],
            HumanMessage(
                content=f"CONTEXT:\n{context_combined}\n\nQUESTION: {question}\n"
                        "Now provide a concise, well-cited legal answer."
            ),
        ]

        # Step 6️⃣ — LLM response
        ai = self.llm.invoke(messages)

        # Step 7️⃣ — Update conversation history
        self.history.extend([HumanMessage(content=question), AIMessage(content=ai.content)])
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]

        # Step 8️⃣ — Return structured answer
        return (
            ai.content.strip()
        )
