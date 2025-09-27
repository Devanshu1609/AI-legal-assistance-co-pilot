# agents/question_answer_agent.py
import os
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools.analysis_storage_tool import AnalysisStorageTool


class QAAgent:
    """
    Robust retrieval-augmented QA that:
    - Doesn't rely on an exact metadata filter at retriever construction time.
    - Filters retrieved chunks in Python by checking several plausible metadata keys
      (doc_id, source, file_name) and matching basename/filename/id variants.
    - Falls back to corpus-wide top results with a clear warning if no match is found.
    """

    def __init__(
        self,
        model: str = "gpt-4.1",
        persist_directory: str = "vector_store",
        doc_id: Optional[str] = None,
        k: int = 6,
        temperature: float = 0.0,
    ):
        self.model_name = model
        self.doc_id = doc_id
        self.k = k
        self.temperature = temperature

        # LLM
        self.llm = ChatOpenAI(model=model, temperature=temperature)

        # Vector store (shared with earlier agents)
        self.analysis_tool = AnalysisStorageTool(persist_directory)
        if not hasattr(self.analysis_tool, "vs") or self.analysis_tool.vs is None:
            raise RuntimeError(
                "AnalysisStorageTool did not expose a vector store (vs). "
                "Ensure tools/analysis_storage_tool.py initializes `self.vs`."
            )

        # Create a retriever WITHOUT a strict metadata filter to allow flexible filtering
        search_kwargs: Dict[str, Any] = {"k": self.k}
        self.retriever = self.analysis_tool.vs.as_retriever(search_kwargs=search_kwargs)

        # Simple in-memory conversation
        self.history: List[Any] = []  # list of HumanMessage/AIMessage

    @property
    def _system_prompt(self) -> str:
        return (
            "You are LegalQA, a careful assistant answering questions strictly from the provided CONTEXT.\n"
            "Rules:\n"
            "1) Only use information found in CONTEXT; do not invent facts.\n"
            "2) If the answer isn't in CONTEXT, say you don't know and suggest where to look (e.g., key clause names).\n"
            "3) Be concise, precise, and explain in plain language. Include clause names/sections if visible.\n"
            "4) If multiple interpretations exist, list them.\n"
            "5) If numbers (fees/penalties/dates) are asked, quote them exactly as in CONTEXT.\n"
            "6) If a follow-up depends on earlier answers, keep them consistent with prior messages."
        )

    def _format_context(self, docs: List[Any]) -> str:
        lines = []
        for i, d in enumerate(docs, start=1):
            meta = getattr(d, "metadata", {}) or {}
            src = meta.get("source") or meta.get("file_name") or meta.get("doc_id") or "unknown"
            page = meta.get("page")
            head = f"[C{i}] source={src}" + (f" page={page}" if page is not None else "")
            text = getattr(d, "page_content", "") or ""
            lines.append(f"{head}\n{text}")
        return "\n\n".join(lines) if lines else "(no context retrieved)"

    def _messages(self, question: str, context: str) -> List[Any]:
        msgs: List[Any] = [SystemMessage(content=self._system_prompt)]
        msgs.extend(self.history)
        user_block = (
            f"CONTEXT (use for answer):\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "Answer using ONLY the CONTEXT above. If not answerable, say you don't know."
        )
        msgs.append(HumanMessage(content=user_block))
        return msgs

    def _normalize_doc_ids(self, raw_id: str) -> set:
        """Return a set of plausible identifiers derived from the provided doc_id/path."""
        out = set()
        if not raw_id:
            return out
        out.add(raw_id)
        bn = os.path.basename(raw_id)
        out.add(bn)
        name_no_ext = os.path.splitext(bn)[0]
        out.add(name_no_ext)
        return out

    def _doc_matches(self, metadata: dict) -> bool:
        """Return True if metadata looks like it belongs to self.doc_id."""
        if not self.doc_id:
            return True
        candidates = self._normalize_doc_ids(self.doc_id)
        # check a few common metadata keys that different loaders use
        for key in ("doc_id", "source", "file_name", "source_id", "source_filename"):
            val = metadata.get(key)
            if not val:
                continue
            # metadata sometimes stores lists
            if isinstance(val, (list, tuple)):
                vals = [str(v) for v in val]
            else:
                vals = [str(val)]
            for v in vals:
                for c in candidates:
                    if c and c in v:
                        return True
        return False

    def answer(self, question: str) -> str:
        """
        Retrieve top-k chunks, filter them to the requested document (if any),
        answer with citations where relevant, update conversation history, and return the text answer.
        """
        try:
            docs = self.retriever.get_relevant_documents(question)
        except Exception as e:
            # Soft fallback: answer without retrieval (but warn)
            warn = (
                "⚠ Retrieval is unavailable; answering without document grounding. "
                "Results may be incomplete.\n"
            )
            msgs = [
                SystemMessage(content=self._system_prompt),
                *self.history,
                HumanMessage(
                    content=f"{warn}\nQUESTION: {question}\n\nIf uncertain, say you don't know."
                ),
            ]
            ai = self.llm.invoke(msgs)
            self.history.extend([HumanMessage(content=question), AIMessage(content=ai.content)])
            return ai.content

        # If a doc_id was supplied, filter retrieved docs to that document (flexible matching)
        warning_text = ""
        if self.doc_id:
            filtered = [d for d in docs if self._doc_matches(getattr(d, "metadata", {}) or {})]
            if filtered:
                docs = filtered
            else:
                # No matching chunks found for the given doc_id — fall back to top results but warn
                warning_text = (
                    "⚠ I couldn't find chunks that clearly belong to the requested document ID. "
                    "Answering from the top relevant chunks across the corpus; results may be unrelated.\n\n"
                )

        context = self._format_context(docs)
        if warning_text:
            context = warning_text + context

        msgs = self._messages(question, context)
        ai = self.llm.invoke(msgs)

        # Update memory
        self.history.extend([HumanMessage(content=question), AIMessage(content=ai.content)])

        return ai.content
