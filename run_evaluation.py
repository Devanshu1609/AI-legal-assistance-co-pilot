"""Run evaluation suite on test cases."""

from evaluation.evaluator import LegalAssistantEvaluator
from evaluation.test_cases import create_sample_test_cases

def main():
    """Run complete evaluation suite"""
    
    # Create evaluator
    evaluator = LegalAssistantEvaluator(output_dir="evaluations")
    
    # Create test cases
    test_cases = create_sample_test_cases()
    
    print("🚀 Starting evaluation suite...")
    print(f"📊 Running {len(test_cases)} test cases\n")
    
    # Run evaluation
    results = evaluator.run_full_evaluation(test_cases)
    
    # Print summary
    evaluator.print_summary(results)
    
    print("\n✅ Evaluation complete!")
    print(f"📁 Results saved to: evaluations/eval_results_*.json")

if __name__ == "__main__":
    main()
