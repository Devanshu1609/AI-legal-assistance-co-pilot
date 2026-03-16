import os
from dotenv import load_dotenv
from google.generativeai import configure, ChatSession
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import init_chat_model
from tools.web_search_tool import web_search
from config import TEMPERATURE, MAX_NEW_TOKENS

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

# Configure Gemini API key
configure(api_key=api_key)

# Use Gemini model
# chat_model = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",     # or "gemini-1.5-pro"
#     temperature=TEMPERATURE,
#     max_output_tokens=MAX_NEW_TOKENS
# )

chat_model = init_chat_model("google_genai:gemini-2.5-flash-lite")
print(chat_model)
tools_list = [web_search]

# Equivalent of bind_tools
llm_with_tools = chat_model.bind_tools(tools_list)
print(llm_with_tools)