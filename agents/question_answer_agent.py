import os
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools.analysis_storage_tool import AnalysisStorageTool


class QAAgent:
    def __init__(
        self,
        model: str = "gpt-4.1",
        persist_directory: str = "vector_store",
        doc_id: Optional[str] = None,
        k: int = 6,
        temperature: float = 0.0,
        max_history: int = 6,  # only keep last N interactions
    ):
        self.model_name = model
        self.doc_id = doc_id
        self.k = k
        self.temperature = temperature
        self.max_history = max_history

        # LLM
        self.llm = ChatOpenAI(model=model, temperature=temperature)

        # Vector store (shared with earlier agents)
        self.analysis_tool = AnalysisStorageTool(persist_directory)
        if not hasattr(self.analysis_tool, "vs") or self.analysis_tool.vs is None:
            raise RuntimeError("AnalysisStorageTool did not expose a vector store (vs).")

        search_kwargs: Dict[str, Any] = {"k": self.k}
        self.retriever = self.analysis_tool.vs.as_retriever(search_kwargs=search_kwargs)

        # Simple in-memory conversation
        self.history: List[Any] = []

        # Cache normalized doc_ids
        self._doc_id_candidates = self._normalize_doc_ids(doc_id)

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
        if not docs:
            return "(no context retrieved)"
        return "\n\n".join(
            f"[C{i+1}] source={d.metadata.get('source') or d.metadata.get('file_name') or d.metadata.get('doc_id') or 'unknown'}"
            + (f" page={d.metadata.get('page')}" if d.metadata.get('page') else "")
            + f"\n{d.page_content or ''}"
            for i, d in enumerate(docs)
        )

    def _messages(self, question: str, context: str) -> List[Any]:
        msgs: List[Any] = [SystemMessage(content=self._system_prompt)]
        # Keep only last `max_history` messages
        if self.history:
            msgs.extend(self.history[-self.max_history:])
        user_block = (
            f"CONTEXT (use for answer):\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "Answer using ONLY the CONTEXT above. If not answerable, say you don't know."
        )
        msgs.append(HumanMessage(content=user_block))
        return msgs

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

    def answer(self, question: str) -> str:
        try:
            docs = self.retriever.get_relevant_documents(question)
        except Exception:
            # Soft fallback
            warning = "⚠ Retrieval unavailable; answering without document grounding.\n"
            msgs = [
                SystemMessage(content=self._system_prompt),
                *self.history[-self.max_history:],
                HumanMessage(content=f"{warning}QUESTION: {question}\nIf uncertain, say you don't know."),
            ]
            ai = self.llm.invoke(msgs)
            self.history.extend([HumanMessage(content=question), AIMessage(content=ai.content)])
            return ai.content

        # Filter by doc_id if provided
        warning_text = ""
        if self.doc_id:
            filtered = [d for d in docs if self._doc_matches(d.metadata or {})]
            if filtered:
                docs = filtered
            else:
                warning_text = (
                    "⚠ No chunks match the requested document ID. Answering from top relevant chunks; results may be unrelated.\n\n"
                )

        context = self._format_context(docs)
        if warning_text:
            context = warning_text + context

        msgs = self._messages(question, context)
        ai = self.llm.invoke(msgs)

        # Update history and keep only last `max_history` messages
        self.history.extend([HumanMessage(content=question), AIMessage(content=ai.content)])
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2 :]

        return ai.content
