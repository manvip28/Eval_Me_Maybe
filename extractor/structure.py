import json
import re
import os

# Import storage client for persistent file operations
try:
    from storage import get_storage_client, should_use_temp_local
    _storage_available = True
except ImportError:
    _storage_available = False

def convert_to_final_format(input_json_files, output_file):
    """
    Combine one or more structured_output.json files and produce a final JSON
    linking questions to diagrams. Cleans text by removing escape characters and extra spaces.
    """
    questions = {}

    # Merge all pages
    for file in input_json_files:
        # Read JSON file (supports both local and blob)
        if _storage_available and not should_use_temp_local(file):
            storage = get_storage_client()
            if storage.is_blob_storage() and not os.path.exists(file):
                # Try blob storage if file doesn't exist locally
                data = storage.read_json(file)
            else:
                # Local file exists
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        else:
            # Local file system
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        text = data.get('text', '')
        diagrams = data.get('diagrams', [])
        question_pattern = r'(Q\d+\.)'
        parts = re.split(question_pattern, text)
        current_q = None

        for part in parts:
            if re.match(question_pattern, part):
                current_q = part.strip()
                if current_q not in questions:
                    questions[current_q] = {"text": "", "diagram": None}
            elif current_q:
                # Clean text: remove \n, tabs, extra spaces
                clean_text = part.strip().replace("\n", " ").replace("\t", " ")
                questions[current_q]["text"] += clean_text + " "

        # Associate diagrams with questions
        for diagram in diagrams:
            question_key = diagram.get('question', '')
            match = re.match(question_pattern, question_key)
            if match:
                q_num = match.group(1)
                if q_num in questions:
                    if questions[q_num]["diagram"] is None:
                        questions[q_num]["diagram"] = diagram['filename']
                    elif isinstance(questions[q_num]["diagram"], str):
                        questions[q_num]["diagram"] = [questions[q_num]["diagram"], diagram['filename']]
                    else:
                        questions[q_num]["diagram"].append(diagram['filename'])

    # Final cleanup: remove multiple spaces in text
    for q_num, content in questions.items():
        content["text"] = re.sub(r"\s+", " ", content["text"]).strip()

    # Save final JSON (supports both local and blob)
    if _storage_available and not should_use_temp_local(output_file):
        storage = get_storage_client()
        storage.write_json(output_file, questions)
    else:
        # Local file system fallback
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Final JSON saved: {output_file}")
    return questions
