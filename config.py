import os

# URL
BASE_URL = "http://localhost:8000/"
# chat model
REPO_ID = "openai/gpt-oss-120b"     #"deepseek-ai/DeepSeek-V3-0324"
TEMPERATURE = 0.7
MAX_NEW_TOKENS = 512

# Prompts paths
SUMMARIZER_PATH = os.path.join("prompts","summarizer.txt")
CLAUSE_EXPLAINER_PATH = os.path.join("prompts","clause_explainer.txt")
RISK_ANALYSER_PATH = os.path.join("prompts","risk_analyser.txt")
REPORT_GENERATOR_PATH = os.path.join("prompts","report_generator.txt")

# Graph
REPORTS_PATH = "reports"
GRAPH_VISUALIZATION_PATH = os.path.join(REPORTS_PATH,"graph.png")

ANALYSIS_LIST=["market_analysis","competition_analysis","risk_assessment","swot_analysis","idea_analysis"]