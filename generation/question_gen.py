import argparse
from .pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Exam Question Generator")
    parser.add_argument("input", help="Path to textbook PDF or text file")
    parser.add_argument("-o", "--output", default="questions.json", 
                        help="Output JSON file for questions")
    parser.add_argument("-q", "--questions-per-topic", type=int, 
                        help="Number of questions to generate per topic (if not provided, will ask interactively)")
    parser.add_argument("--review", action="store_true", 
                        help="Run manual review after generation")
    parser.add_argument("--skip-review", action="store_true", 
                        help="Skip manual review (for web interface)")
    
    args = parser.parse_args()
    
    # Run main pipeline
    skip_manual_review = args.skip_review
    run_pipeline(args.input, args.output, args.questions_per_topic, skip_manual_review)
    
    # Run review if requested
    if args.review:
        from .utils.manual_review import review_questions
        review_questions(args.output)

if __name__ == "__main__":
    main()

