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


def check_local_knowledge(query: str, context: str):
    """
    Decide if retrieved local context is enough.
    """

    prompt = f"""
You are a decision layer.

Determine whether the provided context contains enough information
to answer the user's question.

Rules:
- Reply ONLY Yes or No.

Question:
{query}

Context:
{context}
"""

    response = llm.invoke(prompt)

    return response.content.strip().lower() == "yes"


def get_web_context(query: str):
    """
    Search web using Tavily directly
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