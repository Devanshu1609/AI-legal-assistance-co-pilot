import os
from tavily import TavilyClient
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=500,
)

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def check_local_knowledge(query: str, context):
    """
    Validates whether the provided context contains sufficient information
    to answer the user's query without requiring external knowledge.
    """

    if isinstance(context, list):
        context = "\n\n".join(
            [doc.page_content for doc in context]
        )

    # Enhanced prompt with better evaluation criteria
    prompt = f"""
You are a retrieval validation agent for an AI Legal Document Assistant.

Your job is to determine whether the provided document context contains enough information to answer the user's question WITHOUT requiring external knowledge.

IMPORTANT:
- Return ONLY one word: YES or NO.
- Do NOT explain your answer.
- Do NOT return any additional text.

Decision Rules:

Return YES if:
1. The context contains information that directly or partially answers the question.
2. The context comes from the same uploaded document being queried.
3. The context contains headings, clauses, parties, purpose, definitions, obligations, timelines, sections, or other information that can reasonably answer the question.
4. The user is asking for:
   - a summary
   - an overview
   - an explanation of the document
   - what the document is about
   - key points of the document
   - main clauses or sections
   In these cases, partial context is usually sufficient. Prefer YES unless the retrieved context is completely unrelated.
5. The context contains enough evidence to generate a useful answer, even if:
   - some fields are blank,
   - some pages are missing,
   - the document contains "See attached",
   - the retrieved chunks are fragmented.

Return NO only if:
1. The retrieved context is unrelated to the question.
2. The answer requires information that does not exist in the retrieved context.
3. The user asks for a specific fact, clause, amount, date, obligation, or legal provision that is absent from the context.
4. The retrieved chunks are too short or irrelevant to provide any meaningful answer.
5. External information is genuinely required because the document context does not contain sufficient evidence.

Important Guidelines:
- For document summary or overview questions, strongly prefer YES.
- For uploaded document questions, assume the retrieved context belongs to the same document unless clearly unrelated.
- Do NOT reject context merely because it is incomplete or fragmented.
- If a reasonable answer can be produced from the provided context, return YES.

Question:
{query}

Retrieved Context:
{context}

Answer (YES or NO only):
"""

    response = llm.invoke(prompt)
    return response.content.strip().lower() == "yes"


def get_web_context(query: str):
    """
    Search web using Tavily directly for external context.
    Used when local document context is insufficient.
    """

    response = tavily.search(
        query=query,
        max_results=5
    )

    results = response.get("results", [])

    context = "\n\n".join(
        result.get("content", "")
        for result in results
    )

    return context

