# agents/qa_agent.py
from __future__ import annotations

from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools.analysis_storage_tool import AnalysisStorageTool


class QAAgent:
    """
    Conversational, retrieval-augmented QA over your legal document.
    - Uses the existing Chroma vector store from AnalysisStorageTool.
    - Filters retrieval to the current doc_id (path/identifier) when provided.
    - Maintains lightweight in-memory chat history.
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

        # Prefer current document via metadata filter if provided
        search_kwargs: Dict[str, Any] = {"k": self.k}
        if self.doc_id:
            # Most Chroma loaders in LangChain store the doc path under metadata["doc_id"]
            # If your tool uses a different key, adjust here.
            search_kwargs["filter"] = {"doc_id": self.doc_id}

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
        """
        Build a readable context block with lightweight citations.
        Each chunk is labeled [C1], [C2], ... and includes any useful metadata.
        """
        lines = []
        for i, d in enumerate(docs, start=1):
            meta = d.metadata or {}
            src = meta.get("source") or meta.get("file_name") or meta.get("doc_id") or "unknown"
            page = meta.get("page")  # if your loader stored page numbers
            head = f"[C{i}] source={src}" + (f" page={page}" if page is not None else "")
            text = d.page_content or ""
            lines.append(f"{head}\n{text}")
        return "\n\n".join(lines) if lines else "(no context retrieved)"

    def _messages(self, question: str, context: str) -> List[Any]:
        # System + (optional) history + current user turn (with context attached)
        msgs: List[Any] = [SystemMessage(content=self._system_prompt)]

        # Thread history (kept small—LLMs have token limits; truncate if desired)
        msgs.extend(self.history)

        user_block = (
            f"CONTEXT (use for answer):\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "Answer using ONLY the CONTEXT above. If not answerable, say you don't know."
        )
        msgs.append(HumanMessage(content=user_block))
        return msgs

    def answer(self, question: str) -> str:
        """
        Retrieve top-k chunks, answer with citations where relevant,
        update conversation history, and return the text answer.
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

        # Build context window
        context = self._format_context(docs)
        msgs = self._messages(question, context)

        # Invoke LLM
        ai = self.llm.invoke(msgs)

        # Update memory
        self.history.extend([HumanMessage(content=question), AIMessage(content=ai.content)])

        return ai.content
