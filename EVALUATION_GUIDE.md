# 📊 Evaluation Framework Guide

## Quick Start

### 1. Run Sample Evaluation

```bash
python run_evaluation.py
```

This will:
- Run evaluation on 2 sample test cases
- Generate detailed metrics for each stage
- Save results to `evaluations/eval_results_*.json`
- Print summary to console

### 2. Integrate with Your Server

```bash
# Replace your current main.py
cp main_with_evaluation.py main.py

# Start server
uvicorn main:app --reload
```

Now every API call includes automatic evaluation metrics!

### 3. Test the Endpoints

**Upload document:**
```bash
curl -X POST -F "file=@test_docs/contract.pdf" \
  http://localhost:8000/upload-document
```

Response includes:
```json
{
  "metrics": {
    "file_save_ms": 45.32,
    "document_processing_ms": 1234.56,
    "graph_execution_ms": 5678.90,
    "total_latency_ms": 6958.78,
    "text_length": 25000,
    "chunk_count": 45
  }
}
```

**Ask question:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"What are termination terms?", "file_name":"contract.pdf"}' \
  http://localhost:8000/ask-question
```

Response includes RAG metrics:
```json
{
  "metrics": {
    "retrieval_latency_ms": 45.23,
    "generation_latency_ms": 234.56,
    "total_latency_ms": 279.79,
    "rag_evaluation": {
      "faithfulness": 0.87,
      "answer_relevance": 0.92,
      "rouge_l": 0.75
    }
  }
}
```

**Get metrics:**
```bash
curl http://localhost:8000/metrics
```

## Metrics Explained

### Latency Metrics

| Metric | Meaning | Target |
|--------|---------|--------|
| `file_save_ms` | Time to save uploaded file | < 100ms |
| `document_processing_ms` | Time to extract text and chunks | < 3000ms |
| `graph_execution_ms` | Time for multi-agent pipeline | < 10000ms |
| `retrieval_latency_ms` | Time to search vector DB | < 100ms |
| `generation_latency_ms` | Time for LLM to generate response | < 2000ms |

### Quality Metrics

| Metric | Meaning | Target | Range |
|--------|---------|--------|-------|
| `hallucination_rate` | % of false statements | < 0.05 | 0-1 |
| `rouge_l` | Text overlap with reference | > 0.6 | 0-1 |
| `bleu` | N-gram precision | > 0.3 | 0-1 |
| `faithfulness` | Answer grounded in context | > 0.75 | 0-1 |
| `answer_relevance` | Answer addresses query | > 0.75 | 0-1 |

### RAG Pipeline Metrics

| Metric | Meaning | Target |
|--------|---------|--------|
| `hit_rate@5` | % queries with relevant result in top-5 | > 0.85 |
| `mrr` | Mean reciprocal rank | > 0.8 |
| `ndcg@5` | Ranking quality | > 0.75 |
| `faithfulness` | Answer grounded in retrieved context | > 0.8 |

## Creating Custom Test Cases

### Example Test Case

```python
from evaluation.test_cases import create_sample_test_cases

test_case = {
    "name": "Your Test Name",
    "document_processing": {
        "file_path": "path/to/file.pdf",
        "processing_time": 2.5,  # seconds
        "extracted_text": "Full text of document...",
        "expected_content": "Expected content..."
    },
    "summarization": {
        "generated_summary": "Generated summary...",
        "reference_summary": "Reference summary...",
        "source_document": "Original document...",
        "latency": 3.2  # seconds
    },
    "risk_analysis": {
        "predicted_risks": [{"id": "R1", "category": "Legal"}],
        "ground_truth_risks": [{"id": "R1", "category": "Legal"}],
        "latency": 2.8  # seconds
    },
    "qa_pipeline": {
        "query": "Your question?",
        "retrieved_chunks": ["Chunk 1", "Chunk 2"],
        "answer": "Generated answer",
        "ground_truth_answer": "Reference answer",
        "latency": 1.5,  # seconds
        "retrieval_latency": 0.3  # seconds
    }
}
```

## Using Evaluation in Code

```python
from evaluation.evaluator import LegalAssistantEvaluator

# Create evaluator
evaluator = LegalAssistantEvaluator(output_dir="my_evaluations")

# Evaluate document processing
result = evaluator.evaluate_document_processing(
    file_path="doc.pdf",
    processing_time=2.5,
    extracted_text="Your extracted text",
    expected_content="Expected content"
)

# Evaluate summarization
result = evaluator.evaluate_summarization(
    generated_summary="Generated...",
    reference_summary="Reference...",
    source_document="Source...",
    latency=3.2
)

# Evaluate risk analysis
result = evaluator.evaluate_risk_analysis(
    predicted_risks=[{"id": "R1"}],
    ground_truth_risks=[{"id": "R1"}],
    latency=2.8
)

# Evaluate Q&A pipeline
result = evaluator.evaluate_qa_pipeline(
    query="Question?",
    retrieved_chunks=["Chunk 1"],
    answer="Answer",
    ground_truth_answer="Reference answer",
    latency=1.5,
    retrieval_latency=0.3
)
```

## Understanding Results

### Evaluation Results File

Each evaluation generates a JSON file like:

```json
{
  "timestamp": "2025-01-15T10:30:45.123456",
  "total_tests": 2,
  "stages": {
    "document_processing": [
      {
        "stage": "document_processing",
        "latency_ms": 2500.0,
        "text_length": 25000,
        "text_quality": 0.95
      }
    ],
    "summarization": [...],
    "risk_analysis": [...],
    "qa_pipeline": [...]
  },
  "summary": {
    "document_processing": {
      "avg_latency_ms": 2500.0,
      "p95_latency_ms": 2500.0,
      "pass_rate": 1.0,
      "test_count": 1
    },
    "summarization": {...},
    "risk_analysis": {...},
    "qa_pipeline": {...}
  }
}
```

## Performance Targets

### For Your Legal Assistant

```
✅ GOOD Performance:
  - Document processing: < 5 seconds
  - Summarization: < 5 seconds
  - Risk analysis: < 4 seconds
  - Q&A response: < 2 seconds
  - Hallucination rate: < 2%
  - Retrieval hit rate: > 85%
  - Faithfulness: > 80%

⚠️  WARNING Performance:
  - Document processing: 5-15 seconds
  - Hallucination rate: 2-5%
  - Retrieval hit rate: 70-85%

❌ BAD Performance:
  - Document processing: > 15 seconds
  - Hallucination rate: > 5%
  - Retrieval hit rate: < 70%
  - Faithfulness: < 60%
```

## Next Steps

1. **Integrate evaluation into CI/CD**: Add evaluation to your test pipeline
2. **Monitor production**: Track metrics over time
3. **Create baselines**: Establish performance baselines
4. **Test variations**: A/B test different models/prompts
5. **Optimize bottlenecks**: Focus on low-performing stages

## Troubleshooting

### Imports not working

```bash
# Make sure evaluation package is importable
ls evaluation/
# Should show: __init__.py, metrics.py, evaluator.py, test_cases.py
```

### Missing dependencies

```bash
# Install optional evaluation dependencies
pip install rouge-score nltk sentence-transformers scikit-learn
```

### Results not saving

```bash
# Check permissions
ls -la evaluations/
# Should be writable by your user
```

## Questions?

Refer to the inline documentation in:
- `evaluation/metrics.py` - Core metrics
- `evaluation/evaluator.py` - Main orchestrator
- `evaluation/test_cases.py` - Test data
