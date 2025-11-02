# src/evaluation/manual_review.py
import json

def review_questions(question_file):
    with open(question_file) as f:
        questions = json.load(f)
    
    for i, q in enumerate(questions):
        print(f"\n--- Question {i+1}/{len(questions)} ---")
        print(f"**{q['bloom']} ({q['marks']} marks)**")
        print(q['question'])
        print(f"*Keywords: {', '.join(q['keywords_used'])}*")
        
        action = input("[A]pprove [R]eject [E]dit: ").upper()
        if action == "A":
            q['approved'] = True
        elif action == "R":
            q['approved'] = False
        elif action == "E":
            q['approved'] = True
            q['feedback'] = input("Feedback: ")
        else:
            q['approved'] = False  # Default to reject for invalid input
    
    # Save updated questions back to file
    with open(question_file, "w") as f:
        json.dump(questions, f, indent=2)
    
    print(f"\n✅ Review completed. Updated {question_file}")