from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory


class QnAAgent:
    def __init__(self, vectorstore, model="gpt-4o-mini", temperature=0, name="QnAAgent"):
        """
        Agent for answering user questions about the document, summary, or report.

        Args:
            vectorstore: Vector database containing embeddings of the document/summary/report
            model: Language model to use
            temperature: Controls creativity (0 = factual, >0 = more creative)
            name: Agent identifier
        """
        self.name = name
        self.vectorstore = vectorstore
        self.model = model
        self.temperature = temperature

        # Retriever from vectorstore
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

        # Conversation memory (so user can ask follow-up questions naturally)
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # QnA chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model=model, temperature=temperature),
            retriever=retriever,
            memory=memory,
            return_source_documents=True
        )

    def run(self, query: str) -> dict:
        """
        Runs the QnA agent on a user query.

        Args:
            query: User's question

        Returns:
            dict with 'answer' and 'sources'
        """
        response = self.qa_chain({"question": query})

        # Extract answer safely (different LC versions use "answer" or "result")
        answer = response.get("answer") or response.get("result", "No answer generated.")

        # Collect sources
        sources = []
        for doc in response.get("source_documents", []):
            src = doc.metadata.get("source") or doc.metadata.get("file_path") or "Unknown"
            page = doc.metadata.get("page")
            if page is not None:
                src += f" (page {page})"
            sources.append(src)

        unique_sources = list(set(sources))

        return {"answer": answer, "sources": unique_sources}
