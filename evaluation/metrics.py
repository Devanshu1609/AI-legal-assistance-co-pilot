"""Core evaluation metrics for LLM and RAG pipeline."""

import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Callable
from functools import wraps
from pathlib import Path
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================================
# 1. LATENCY MEASUREMENT SYSTEM
# ============================================================================

@dataclass
class LatencyMetrics:
    """Store latency measurements"""
    operation: str
    start_time: float
    end_time: float
    duration_ms: float
    tokens_processed: int = 0
    
    def __post_init__(self):
        self.duration_ms = (self.end_time - self.start_time) * 1000

class LatencyTracker:
    """Track latency across all operations"""
    
    def __init__(self, log_dir: str = "logs"):
        self.metrics: List[LatencyMetrics] = []
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        logger = logging.getLogger("LatencyTracker")
        handler = logging.FileHandler(self.log_dir / "latency.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    def measure(self, operation_name: str):
        """Decorator to measure latency of any function"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()
                
                metric = LatencyMetrics(
                    operation=operation_name,
                    start_time=start,
                    end_time=end
                )
                
                self.metrics.append(metric)
                self.logger.info(
                    f"{operation_name}: {metric.duration_ms:.2f}ms"
                )
                
                return result
            return wrapper
        return decorator
    
    def get_statistics(self) -> Dict[str, float]:
        """Get latency statistics"""
        if not self.metrics:
            return {}
        
        durations = [m.duration_ms for m in self.metrics]
        
        return {
            "min_ms": float(min(durations)),
            "max_ms": float(max(durations)),
            "mean_ms": float(np.mean(durations)),
            "median_ms": float(np.median(durations)),
            "p95_ms": float(np.percentile(durations, 95)),
            "p99_ms": float(np.percentile(durations, 99)),
            "total_calls": len(self.metrics)
        }
    
    def get_by_operation(self) -> Dict[str, Dict[str, float]]:
        """Get latency stats grouped by operation"""
        operations = {}
        
        for metric in self.metrics:
            if metric.operation not in operations:
                operations[metric.operation] = []
            operations[metric.operation].append(metric.duration_ms)
        
        stats = {}
        for op_name, durations in operations.items():
            stats[op_name] = {
                "mean_ms": float(np.mean(durations)),
                "p95_ms": float(np.percentile(durations, 95)),
                "p99_ms": float(np.percentile(durations, 99)),
                "count": len(durations)
            }
        
        return stats

# ============================================================================
# 2. QUALITY METRICS (Accuracy, Hallucinations, ROUGE/BLEU)
# ============================================================================

class HallucinationDetector:
    """Detect and measure hallucinations in LLM outputs"""
    
    def __init__(self):
        self.hallucinations: List[Dict] = []
    
    def detect_named_entity_hallucinations(
        self,
        generated_text: str,
        source_document: str
    ) -> Dict[str, Any]:
        """Simple hallucination detection using entity matching"""
        gen_entities = self._extract_entities(generated_text)
        src_entities = self._extract_entities(source_document)
        
        hallucinated = [e for e in gen_entities if e not in src_entities]
        
        hallucination_rate = len(hallucinated) / len(gen_entities) if gen_entities else 0
        
        return {
            "hallucination_rate": float(hallucination_rate),
            "hallucinated_entities": hallucinated,
            "generated_entities_count": len(gen_entities),
            "severity": "CRITICAL" if hallucination_rate > 0.05 else "OK"
        }
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract proper nouns as entities"""
        import re
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return entities
    
    def semantic_consistency_check(
        self,
        answer: str,
        context: str
    ) -> float:
        """Check semantic consistency between answer and context"""
        from difflib import SequenceMatcher
        
        similarity = SequenceMatcher(None, answer, context).ratio()
        return min(float(similarity), 1.0)

class QualityMetrics:
    """Calculate standard NLP quality metrics"""
    
    @staticmethod
    def rouge_score(
        generated: str,
        reference: str
    ) -> Dict[str, float]:
        """ROUGE: Overlap between generated and reference text"""
        try:
            from rouge_score import rouge_scorer
            
            scorer = rouge_scorer.RougeScorer(
                ['rouge1', 'rougeL'],
                use_stemmer=True
            )
            scores = scorer.score(reference, generated)
            
            return {
                "rouge1_precision": float(scores['rouge1'].precision),
                "rouge1_recall": float(scores['rouge1'].recall),
                "rouge1_fmeasure": float(scores['rouge1'].fmeasure),
                "rougeL_fmeasure": float(scores['rougeL'].fmeasure),
            }
        except ImportError:
            return {"error": "rouge_score not installed"}
    
    @staticmethod
    def bleu_score(
        generated: str,
        reference: str
    ) -> float:
        """BLEU: N-gram precision between generated and reference"""
        try:
            from nltk.translate.bleu_score import sentence_bleu
            from nltk.tokenize import word_tokenize
            
            ref_tokens = word_tokenize(reference.lower())
            gen_tokens = word_tokenize(generated.lower())
            
            bleu = sentence_bleu(
                [ref_tokens],
                gen_tokens,
                weights=(0.5, 0.5)
            )
            
            return float(bleu)
        except ImportError:
            return 0.0
    
    @staticmethod
    def text_similarity(
        text1: str,
        text2: str
    ) -> float:
        """Compute text similarity (simple overlap-based)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1 & words2)
        union = len(words1 | words2)
        
        return float(overlap / union) if union > 0 else 0.0

# ============================================================================
# 3. RAG PIPELINE EVALUATION
# ============================================================================

class RetrievalMetrics:
    """Evaluate retrieval quality (ChromaDB/Vector Search)"""
    
    @staticmethod
    def hit_rate(
        retrieved_chunk_ids: List[str],
        relevant_chunk_ids: List[str],
        k: int = 5
    ) -> float:
        """Hit Rate: % of queries where top-k contains relevant doc"""
        retrieved_top_k = set(retrieved_chunk_ids[:k])
        relevant_set = set(relevant_chunk_ids)
        
        hits = len(retrieved_top_k & relevant_set)
        
        return float(hits / len(relevant_set)) if relevant_set else 0.0
    
    @staticmethod
    def mean_reciprocal_rank(
        retrieved_chunk_ids: List[str],
        relevant_chunk_ids: List[str],
        k: int = 5
    ) -> float:
        """MRR: Average inverse rank of first relevant item"""
        relevant_set = set(relevant_chunk_ids)
        
        for rank, chunk_id in enumerate(retrieved_chunk_ids[:k], 1):
            if chunk_id in relevant_set:
                return float(1.0 / rank)
        
        return 0.0
    
    @staticmethod
    def ndcg(
        retrieved_chunk_ids: List[str],
        relevant_chunk_ids: List[str],
        k: int = 5
    ) -> float:
        """NDCG: Normalized Discounted Cumulative Gain"""
        relevant_set = set(relevant_chunk_ids)
        
        dcg = 0.0
        for i, chunk_id in enumerate(retrieved_chunk_ids[:k], 1):
            relevance = 1 if chunk_id in relevant_set else 0
            dcg += relevance / np.log2(i + 1)
        
        ideal_dcg = sum([
            1.0 / np.log2(i + 1)
            for i in range(min(k, len(relevant_set)))
        ])
        
        ndcg = dcg / ideal_dcg if ideal_dcg > 0 else 0.0
        
        return float(ndcg)

class RAGPipelineEvaluator:
    """End-to-end RAG pipeline evaluation"""
    
    def __init__(self):
        self.results: List[Dict] = []
    
    def evaluate_retrieval_latency(
        self,
        retrieval_times: List[float]
    ) -> Dict[str, float]:
        """Measure retrieval (ChromaDB) latency"""
        return {
            "avg_retrieval_latency_ms": float(np.mean(retrieval_times)),
            "p95_latency_ms": float(np.percentile(retrieval_times, 95)),
            "p99_latency_ms": float(np.percentile(retrieval_times, 99)),
            "qps": float(1000 / np.mean(retrieval_times)) if retrieval_times else 0
        }
    
    def evaluate_faithfulness(
        self,
        answer: str,
        retrieved_context: str
    ) -> float:
        """Faithfulness: Is answer grounded in retrieved context?"""
        return QualityMetrics.text_similarity(answer, retrieved_context)
    
    def evaluate_answer_relevance(
        self,
        query: str,
        answer: str
    ) -> float:
        """Answer Relevance: Does answer address the query?"""
        return QualityMetrics.text_similarity(query, answer)
    
    def evaluate_full_rag_pipeline(
        self,
        query: str,
        retrieved_context: str,
        answer: str,
        ground_truth_answer: str = ""
    ) -> Dict[str, float]:
        """Complete RAG evaluation with all metrics"""
        
        metrics = {
            "faithfulness": self.evaluate_faithfulness(answer, retrieved_context),
            "answer_relevance": self.evaluate_answer_relevance(query, answer),
        }
        
        if ground_truth_answer:
            metrics["answer_similarity_to_gt"] = QualityMetrics.text_similarity(
                answer,
                ground_truth_answer
            )
            rouge = QualityMetrics.rouge_score(answer, ground_truth_answer)
            if "rougeL_fmeasure" in rouge:
                metrics["rouge_l"] = rouge["rougeL_fmeasure"]
            metrics["bleu"] = QualityMetrics.bleu_score(answer, ground_truth_answer)
        
        return metrics
