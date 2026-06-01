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
You are a retrieval validator for a legal document analysis system.

Your task is to determine whether the provided document context contains 
sufficient information to answer the user's question accurately.

IMPORTANT: ONLY RETURN YES OR NO. Nothing else. DO NOT EXPLAIN YOUR ANSWER.

Evaluation Criteria:

Return YES if:
- The context contains explicit information that directly answers the question.
- For summary/overview questions: The context includes key sections like purpose, parties, scope, or terms that enable a meaningful summary.
- The context is from the same document being queried.
- There is enough textual evidence to formulate a complete answer.

Return NO if:
- Critical information is missing or incomplete (e.g., blank fields, "See attached").
- The context is heavily fragmented and lacks coherence.
- The answer would require inference beyond what's explicitly stated.
- The context is from a different document or unrelated to the query.
- For summary requests: The fragments don't provide enough overview information.

Question:
{query}

Context:
{context}
"""

    response = llm.invoke(prompt)
    print("VALIDATOR OUTPUT:")
    print(response.content)
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

