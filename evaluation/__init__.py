"""Evaluation package for Legal Assistant."""

from evaluation.metrics import (
    LatencyTracker,
    HallucinationDetector,
    QualityMetrics,
    RetrievalMetrics,
    RAGPipelineEvaluator
)
from evaluation.evaluator import LegalAssistantEvaluator
from evaluation.test_cases import create_sample_test_cases

__all__ = [
    "LatencyTracker",
    "HallucinationDetector",
    "QualityMetrics",
    "RetrievalMetrics",
    "RAGPipelineEvaluator",
    "LegalAssistantEvaluator",
    "create_sample_test_cases"
]
