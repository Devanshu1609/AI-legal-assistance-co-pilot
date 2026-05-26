"""Main evaluation orchestrator for legal assistant."""

import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np

from evaluation.metrics import (
    LatencyTracker,
    HallucinationDetector,
    QualityMetrics,
    RetrievalMetrics,
    RAGPipelineEvaluator
)

class LegalAssistantEvaluator:
    """Main evaluation orchestrator for your legal assistant"""
    
    def __init__(self, output_dir: str = "evaluations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.latency_tracker = LatencyTracker()
        self.hallucination_detector = HallucinationDetector()
        self.rag_evaluator = RAGPipelineEvaluator()
        
        self.logger = self._setup_logger()
        self.eval_results: List[Dict] = []
    
    def _setup_logger(self):
        logger = logging.getLogger("LegalAssistantEvaluator")
        # Clear existing handlers
        logger.handlers = []
        
        handler = logging.FileHandler(
            self.output_dir / "evaluation.log"
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    def evaluate_document_processing(
        self,
        file_path: str,
        processing_time: float,
        extracted_text: str,
        expected_content: str = ""
    ) -> Dict[str, Any]:
        """Evaluate document processing stage"""
        
        text_quality = 0.0
        if expected_content:
            text_quality = QualityMetrics.text_similarity(
                extracted_text,
                expected_content
            )
        
        result = {
            "stage": "document_processing",
            "latency_ms": float(processing_time * 1000),
            "text_length": len(extracted_text),
            "text_quality": text_quality
        }
        
        self.eval_results.append(result)
        return result
    
    def evaluate_summarization(
        self,
        generated_summary: str,
        reference_summary: str,
        source_document: str,
        latency: float
    ) -> Dict[str, Any]:
        """Evaluate summarizer agent"""
        
        hallucination_check = self.hallucination_detector.detect_named_entity_hallucinations(
            generated_summary,
            source_document
        )
        
        quality_metrics = QualityMetrics.rouge_score(
            generated_summary,
            reference_summary
        )
        
        result = {
            "stage": "summarization",
            "latency_ms": float(latency * 1000),
            "hallucination": hallucination_check,
            "quality": quality_metrics,
            "hallucination_rate": float(hallucination_check["hallucination_rate"]),
            "status": "PASS" if hallucination_check["hallucination_rate"] < 0.05 else "FAIL"
        }
        
        self.eval_results.append(result)
        return result
    
    def evaluate_risk_analysis(
        self,
        predicted_risks: List[Dict],
        ground_truth_risks: List[Dict],
        latency: float
    ) -> Dict[str, Any]:
        """Evaluate risk analysis agent"""
        
        pred_ids = set([r.get('id') for r in predicted_risks])
        true_ids = set([r.get('id') for r in ground_truth_risks])
        
        tp = len(pred_ids & true_ids)
        fp = len(pred_ids - true_ids)
        fn = len(true_ids - pred_ids)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        result = {
            "stage": "risk_analysis",
            "latency_ms": float(latency * 1000),
            "metrics": {
                "precision": float(precision),
                "recall": float(recall),
                "f1_score": float(f1),
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn
            },
            "status": "PASS" if f1 > 0.75 else "FAIL"
        }
        
        self.eval_results.append(result)
        return result
    
    def evaluate_qa_pipeline(
        self,
        query: str,
        retrieved_chunks: List[str],
        answer: str,
        ground_truth_answer: str = "",
        latency: float = 0,
        retrieval_latency: float = 0
    ) -> Dict[str, Any]:
        """Evaluate Q&A agent (full RAG pipeline)"""
        
        retrieved_context = " ".join(retrieved_chunks)
        
        rag_metrics = self.rag_evaluator.evaluate_full_rag_pipeline(
            query,
            retrieved_context,
            answer,
            ground_truth_answer
        )
        
        result = {
            "stage": "qa_pipeline",
            "total_latency_ms": float(latency * 1000),
            "retrieval_latency_ms": float(retrieval_latency * 1000),
            "generation_latency_ms": float((latency - retrieval_latency) * 1000),
            "rag_metrics": rag_metrics,
            "status": "PASS" if rag_metrics.get("faithfulness", 0) > 0.5 else "FAIL"
        }
        
        self.eval_results.append(result)
        return result
    
    def run_full_evaluation(
        self,
        test_cases: List[Dict]
    ) -> Dict[str, Any]:
        """Run complete evaluation suite on test cases"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(test_cases),
            "stages": {},
            "summary": {}
        }
        
        for stage in ["document_processing", "summarization", "risk_analysis", "qa_pipeline"]:
            results["stages"][stage] = []
        
        # Run evaluations
        for test_case in test_cases:
            self.logger.info(f"Evaluating: {test_case.get('name', 'Unknown')}")
            
            if "document_processing" in test_case:
                results["stages"]["document_processing"].append(
                    self.evaluate_document_processing(**test_case["document_processing"])
                )
            
            if "summarization" in test_case:
                results["stages"]["summarization"].append(
                    self.evaluate_summarization(**test_case["summarization"])
                )
            
            if "risk_analysis" in test_case:
                results["stages"]["risk_analysis"].append(
                    self.evaluate_risk_analysis(**test_case["risk_analysis"])
                )
            
            if "qa_pipeline" in test_case:
                results["stages"]["qa_pipeline"].append(
                    self.evaluate_qa_pipeline(**test_case["qa_pipeline"])
                )
        
        # Calculate summary statistics
        results["summary"] = self._calculate_summary(results["stages"])
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _calculate_summary(self, stages: Dict) -> Dict[str, Any]:
        """Calculate overall statistics"""
        summary = {}
        
        for stage_name, stage_results in stages.items():
            if not stage_results:
                continue
            
            latencies = [r.get("latency_ms", 0) for r in stage_results]
            pass_count = sum(1 for r in stage_results if r.get("status") == "PASS")
            
            summary[stage_name] = {
                "avg_latency_ms": float(np.mean(latencies)) if latencies else 0,
                "p95_latency_ms": float(np.percentile(latencies, 95)) if latencies else 0,
                "pass_rate": float(pass_count / len(stage_results)) if stage_results else 0,
                "test_count": len(stage_results)
            }
        
        return summary
    
    def _save_results(self, results: Dict):
        """Save evaluation results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"eval_results_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Results saved to {output_file}")
        print(f"✅ Evaluation complete. Results: {output_file}")
    
    def print_summary(self, results: Dict):
        """Print evaluation summary to console"""
        print("\n" + "="*70)
        print("EVALUATION SUMMARY")
        print("="*70)
        
        for stage, metrics in results["summary"].items():
            print(f"\n📊 {stage.upper()}")
            print(f"   Average Latency: {metrics.get('avg_latency_ms', 0):.2f}ms")
            print(f"   P95 Latency: {metrics.get('p95_latency_ms', 0):.2f}ms")
            print(f"   Pass Rate: {metrics.get('pass_rate', 0)*100:.1f}%")
            print(f"   Test Count: {metrics.get('test_count', 0)}")
        
        print("\n" + "="*70)
