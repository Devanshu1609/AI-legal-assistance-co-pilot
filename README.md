# 📄 AI Legal Document Assistant

### 💡 Overview  
The **AI Legal Document Assistant** is an intelligent multi-agent system designed to **analyze, summarize, and interact with legal documents**.  
It automates the process of reviewing complex contracts and agreements using multiple AI agents that collaborate to extract insights, detect risks, and answer user questions in real-time.

With a **REACT + VITE based modern frontend**, it offers a user-friendly experience for uploading legal documents, viewing comprehensive reports, and chatting with the AI about specific clauses or risks — just like interacting with a professional legal co-pilot.

---

## 🚀 Features

✅ **Document Understanding**  
- Automatically processes and reads legal PDFs or DOCX files.  
- Extracts key clauses and entities for further analysis.

✅ **Summarization**  
- Generates concise summaries of lengthy legal agreements.  
- Highlights critical sections for quicker understanding.

✅ **Risk Analysis**  
- Detects potential legal, financial, or compliance risks.  
- Assigns an overall risk score and category (Low / Medium / High).

✅ **Clause Explanation**  
- Explains complex clauses in simple, human-readable language.

✅ **Report Generation**  
- Creates a detailed, formatted report with summaries, highlights, and risk insights.

✅ **Interactive Q&A Assistant**  
- Chat-like interface powered by a retrieval-augmented QA agent.  
- Ask contextual questions like “What are the termination terms?” or “Is there any confidentiality clause?”

---

## 🧠 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | REACT + VITE |
| **Backend** | FastAPI |
| **Agents Framework** | Custom Multi-Agent Architecture with Supervisor & Task Graph |
| **Vector Store** | ChromaDB |
| **Language Model** | OpenAI GPT model |

---

## 🧩 Architecture Overview

The system operates as a **multi-agent pipeline**, where each AI agent handles a specific responsibility and collaborates through a **Supervisor Agent** orchestrated via a **Multi-Agent Graph**.

### Agent Roles:
- **DocumentProcessorAgent** → Extracts and preprocesses text from legal documents.  
- **SummarizerAgent** → Generates structured summaries.  
- **ClauseExplainerAgent** → Explains legal clauses in simple terms.  
- **RiskAnalysisAgent** → Detects and quantifies potential risks.  
- **ReportGeneratorAgent** → Combines all insights into a final markdown report.  
- **QAAgent** → Enables interactive, context-aware Q&A.  
- **SupervisorAgent** → Manages communication and workflow among agents.

### 🧩 Workflow Graph
```
DocumentProcessorAgent → SummarizerAgent → ClauseExplainerAgent 
      → RiskAnalysisAgent → ReportGeneratorAgent → QAAgent
```

---

## 💻 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/ai-legal-document-assistant.git
cd ai-legal-document-assistant
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate       # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key
```

---

## 🧑‍💼 Example Use Cases

- Contract Review and Risk Summaries  
- Vendor or Service Agreement Analysis  
- Employment Agreement Breakdown  
- NDA or Confidentiality Clause Review  
- Legal Document Q&A Automation  

---

## 📦 Project Structure

```
ai-legal-document-assistant/
├── project/              # frontend code
│
├── agents/
│   ├── document_processor_agent.py
│   ├── summarizer_agent.py
│   ├── clause_explainer_agent.py
│   ├── risk_analysis_agent.py
│   ├── report_generator_agent.py
│   ├── question_answer_agent.py
│   └── supervisor_agent.py
│
├── graph/
│   └── multi_agent_graph.py
│
├── vector_store/
│
├── utils/
│
├── main.py                # Streamlit Frontend + Multi-Agent Runner
├── requirements.txt
└── README.md
```

---

## 🎨 UI Overview

**Step 1:** Upload your PDF or DOCX document  
**Step 2:** The AI automatically processes and generates a report  
**Step 3:** Interact with the chatbot-style assistant for legal insights  

*(You can later attach screenshots or GIFs of the UI here)*

---


## 🤝 Contributing

Contributions are welcome!  

1. Fork the repository  
2. Create a new branch (`feature/my-improvement`)  
3. Make your changes  
4. Submit a Pull Request 🚀

---

## ⚖️ License

This project is licensed under the **MIT License** — feel free to use and adapt it.

---

## ⭐ Acknowledgements
- [OpenAI](https://openai.com/) — for providing advanced language models  
- [LangChain](https://www.langchain.com/) — inspiration for agent orchestration  

---

Empowering professionals with AI-driven legal intelligence.
