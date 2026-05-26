"""Sample test cases for evaluation framework."""

from typing import List, Dict

def create_sample_test_cases() -> List[Dict]:
    """Create sample test cases for evaluation"""
    
    test_cases = [
        {
            "name": "Employment Contract Review",
            "document_processing": {
                "file_path": "test_docs/employment_contract.pdf",
                "processing_time": 2.5,
                "extracted_text": """
                    EMPLOYMENT AGREEMENT
                    This Employment Agreement is entered into between Company ABC and John Doe.
                    Effective Date: January 1, 2025
                    Position: Senior Software Engineer
                    Salary: $150,000 per year
                    Benefits: Health insurance, 401k matching
                    Termination: 30 days notice required
                """,
                "expected_content": "EMPLOYMENT AGREEMENT between Company ABC and John Doe"
            },
            "summarization": {
                "generated_summary": """
                    Employment agreement for Senior Software Engineer position at Company ABC.
                    Salary: $150,000/year. Includes health insurance and 401k.
                    Requires 30 days notice for termination.
                """,
                "reference_summary": """
                    Contract between Company ABC and John Doe for Senior Engineer role.
                    Annual salary of $150,000 with benefits including health insurance 
                    and 401k matching. Termination requires 30-day notice.
                """,
                "source_document": "EMPLOYMENT AGREEMENT with Company ABC and John Doe",
                "latency": 3.2
            },
            "risk_analysis": {
                "predicted_risks": [
                    {"id": "R1", "category": "Legal", "severity": "medium"},
                    {"id": "R2", "category": "Financial", "severity": "low"},
                    {"id": "R3", "category": "Compliance", "severity": "high"},
                ],
                "ground_truth_risks": [
                    {"id": "R1", "category": "Legal", "severity": "medium"},
                    {"id": "R2", "category": "Financial", "severity": "low"},
                ],
                "latency": 2.8
            },
            "qa_pipeline": {
                "query": "What is the termination notice period?",
                "retrieved_chunks": [
                    "Termination: 30 days notice required",
                    "Employee must provide written notice",
                    "Company may terminate with cause immediately"
                ],
                "answer": "The termination requires 30 days notice.",
                "ground_truth_answer": "The employment agreement requires 30 days notice for termination.",
                "latency": 1.5,
                "retrieval_latency": 0.3
            }
        },
        {
            "name": "NDA Review",
            "document_processing": {
                "file_path": "test_docs/nda.pdf",
                "processing_time": 1.8,
                "extracted_text": """
                    NON-DISCLOSURE AGREEMENT
                    Confidentiality: All trade secrets must remain confidential
                    Duration: 5 years after termination
                    Exclusions: Public domain information
                """,
                "expected_content": "NON-DISCLOSURE AGREEMENT with confidentiality terms"
            },
            "summarization": {
                "generated_summary": """
                    NDA protecting trade secrets for 5 years post-termination.
                    Excludes public domain information.
                """,
                "reference_summary": """
                    Non-disclosure agreement requiring confidentiality of trade secrets
                    for 5 years after contract termination. Excludes public information.
                """,
                "source_document": "NON-DISCLOSURE AGREEMENT with confidentiality terms",
                "latency": 2.5
            },
            "risk_analysis": {
                "predicted_risks": [
                    {"id": "R1", "category": "Legal", "severity": "high"},
                ],
                "ground_truth_risks": [
                    {"id": "R1", "category": "Legal", "severity": "high"},
                ],
                "latency": 2.1
            },
            "qa_pipeline": {
                "query": "How long does confidentiality last?",
                "retrieved_chunks": [
                    "Duration: 5 years after termination",
                    "Confidentiality obligations extend post-employment"
                ],
                "answer": "Confidentiality lasts for 5 years after termination.",
                "ground_truth_answer": "The NDA requires confidentiality to be maintained for 5 years after the employment relationship ends.",
                "latency": 1.2,
                "retrieval_latency": 0.25
            }
        }
    ]
    
    return test_cases
