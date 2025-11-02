import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

# Import storage client for persistent file operations
try:
    from storage import get_storage_client, should_use_temp_local
    _storage_available = True
except ImportError:
    _storage_available = False


PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ANSWER_KEY_DIR = PROJECT_ROOT / "answer_key"
STUDENT_ANSWER_DIR = PROJECT_ROOT / "student_answer"


def run_parse(input_path: Path, output_dir: Path = None) -> Path:
    """Run parse.py on the given file and return the generated final JSON path."""
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    final_json = output_dir / "final_answer.json"
    final_json_str = str(final_json)
    
    # Delete existing file if it exists (check both local and blob)
    if final_json.exists():
        try:
            final_json.unlink()
        except Exception:
            pass
    elif _storage_available and not should_use_temp_local(final_json_str):
        storage = get_storage_client()
        if storage.is_blob_storage() and storage.exists(final_json_str):
            try:
                storage.delete_file(final_json_str)
            except Exception:
                pass

    cmd = [sys.executable, "-m", "extractor.parse", str(input_path)]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["CUSTOM_OUTPUT_FOLDER"] = str(output_dir)
    # Inherit parent stdio; avoid Python decoding of child output to prevent cp1252 errors
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        raise RuntimeError("Parsing failed. See logs above.")

    # Check if file exists (both local and blob)
    file_exists = False
    if final_json.exists():
        file_exists = True
    elif _storage_available and not should_use_temp_local(final_json_str):
        storage = get_storage_client()
        if storage.is_blob_storage() and storage.exists(final_json_str):
            file_exists = True
    
    if not file_exists:
        raise FileNotFoundError(f"Expected parsed output not found: {final_json}")
    return final_json


def load_json(path: Path) -> dict:
    """Load JSON file (supports both local and blob storage)"""
    path_str = str(path)
    
    # Temp files should always be local
    if should_use_temp_local(path_str) or not _storage_available:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Try blob storage for persistent files
        storage = get_storage_client()
        if storage.is_blob_storage():
            # Check if it's a blob path or local path
            if path.exists():
                # Local file exists, use it
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Try blob storage
                return storage.read_json(path_str)
        else:
            # Local storage, use file system
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)


def save_json(path: Path, data: dict) -> None:
    """Save JSON file (supports both local and blob storage)"""
    path_str = str(path)
    
    # Temp files should always be local
    if should_use_temp_local(path_str) or not _storage_available:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        # Use blob storage for persistent files
        storage = get_storage_client()
        storage.write_json(path_str, data)


def file_exists(path: Path) -> bool:
    """Check if file exists (supports both local and blob storage)"""
    path_str = str(path)
    
    # Temp files should always be local
    if should_use_temp_local(path_str) or not _storage_available:
        return path.exists()
    else:
        # Check both local and blob
        if path.exists():
            return True
        if _storage_available:
            storage = get_storage_client()
            if storage.is_blob_storage():
                return storage.exists(path_str)
        return False


def transform_parsed_to_schema(parsed: dict, for_answer_key: bool) -> dict:
    """
    Transform parsed structure (with keys like {Q1: {text, diagram}}) into
    evaluator schema with capitalized fields.
    For answer key, include defaults for metadata fields.
    """
    transformed: dict = {}
    def normalize_qid(raw_qid: str) -> str:
        # Convert variants like "Q1.", "Q1:", " q1 " to canonical "Q1"
        if not raw_qid:
            return raw_qid
        s = str(raw_qid).strip()
        # Remove trailing punctuation like . : ) -
        while len(s) > 0 and s[-1] in ".:)-":
            s = s[:-1].strip()
        # Ensure starts with Q and digits
        if s.lower().startswith('q'):
            s_num = ''.join(ch for ch in s[1:] if ch.isdigit())
            if s_num:
                return f"Q{s_num}"
        # Fallback: leave as-is
        return s

    for raw_qid, item in parsed.items():
        qid = normalize_qid(raw_qid)
        text = item.get("text") or item.get("Text") or ""
        image = item.get("diagram") or item.get("Image")

        if for_answer_key:
            transformed[qid] = {
                "Text": text,
                "Image": image,
                "Question": item.get("question") or item.get("Question") or "",
                "BloomLevel": item.get("BloomLevel") or "Understand",
                "Keywords": item.get("Keywords") or [],
            }
        else:
            transformed[qid] = {
                "Text": text,
                "Image": image,
            }
    return transformed


def handle_upload_answer_key():
    path_str = input("Enter path to answer key document (DOCX/JSON): ").strip().strip('"')
    input_path = Path(path_str)
    if not input_path.exists():
        print("Error: File not found.")
        return

    # Check file type
    file_extension = input_path.suffix.lower()
    if file_extension not in ['.docx', '.json']:
        print(f"Error: Unsupported file type '{file_extension}'. Only DOCX and JSON files are supported for answer keys.")
        return

    if file_extension == '.json':
        # Direct JSON upload - no parsing needed
        parsed = load_json(input_path)
        print("Loaded answer key from JSON file.")
    else:
        # DOCX file - use parsing
        final_parsed_path = run_parse(input_path, ANSWER_KEY_DIR)
        parsed = load_json(final_parsed_path)

    # Move diagrams into answer_key/diagrams and rewrite paths in parsed JSON (only for DOCX files)
    if file_extension == '.docx':
        diagrams_dir = ANSWER_KEY_DIR / "diagrams"
        diagrams_dir.mkdir(parents=True, exist_ok=True)

        def relocate_diagram_path(path_str: str) -> str:
            if not path_str:
                return path_str
            src = Path(path_str)
            if not src.is_absolute():
                src = (PROJECT_ROOT / src).resolve()
            if not src.exists():
                return path_str
            dest = (diagrams_dir / src.name).resolve()
            try:
                if src != dest:
                    shutil.move(str(src), str(dest))
            except Exception:
                pass
            # return project-root-relative path
            return str(dest.relative_to(PROJECT_ROOT))

        for qid, item in list(parsed.items()):
            diagram_val = item.get("diagram")
            if not diagram_val:
                continue
            if isinstance(diagram_val, list):
                new_list = [relocate_diagram_path(p) for p in diagram_val if p]
                parsed[qid]["diagram"] = new_list if len(new_list) > 1 else (new_list[0] if new_list else None)
            elif isinstance(diagram_val, str):
                parsed[qid]["diagram"] = relocate_diagram_path(diagram_val)

    transformed = transform_parsed_to_schema(parsed, for_answer_key=True)
    save_path = ANSWER_KEY_DIR / "answer_key.json"
    save_json(save_path, transformed)
    print(f"Saved answer key to: {save_path}")


def handle_evaluate():
    answer_key_path = ANSWER_KEY_DIR / "answer_key.json"
    if not file_exists(answer_key_path):
        print(f"Answer key not found at {answer_key_path}. Please upload the answer key first.")
        return

    path_str = input("Enter path to student answer document (PDF/DOCX/PNG/JPG): ").strip().strip('"')
    input_path = Path(path_str)
    if not input_path.exists():
        print("Error: File not found.")
        return

    final_parsed_path = run_parse(input_path, STUDENT_ANSWER_DIR)
    parsed = load_json(final_parsed_path)

    # Move diagrams into student_answer/diagrams and rewrite paths in parsed JSON
    diagrams_dir = STUDENT_ANSWER_DIR / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    def relocate_diagram_path(path_str: str) -> str:
        if not path_str:
            return path_str
        src = Path(path_str)
        if not src.is_absolute():
            src = (PROJECT_ROOT / src).resolve()
        if not src.exists():
            return path_str
        dest = (diagrams_dir / src.name).resolve()
        try:
            if src != dest:
                shutil.move(str(src), str(dest))
        except Exception:
            pass
        return str(dest.relative_to(PROJECT_ROOT))

    for qid, item in list(parsed.items()):
        diagram_val = item.get("diagram")
        if not diagram_val:
            continue
        if isinstance(diagram_val, list):
            new_list = [relocate_diagram_path(p) for p in diagram_val if p]
            parsed[qid]["diagram"] = new_list if len(new_list) > 1 else (new_list[0] if new_list else None)
        elif isinstance(diagram_val, str):
            parsed[qid]["diagram"] = relocate_diagram_path(diagram_val)

    transformed = transform_parsed_to_schema(parsed, for_answer_key=False)
    student_json_path = STUDENT_ANSWER_DIR / "student_answer.json"
    save_json(student_json_path, transformed)
    print(f"Saved student answer to: {student_json_path}")

    # Run evaluator
    evaluator_cmd = [
        sys.executable,
        "-m", "evaluator.answer_evaluator",
        str(student_json_path),
        str(ANSWER_KEY_DIR / "answer_key.json"),
    ]
    print("Running evaluation...\n")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # Inherit parent stdio (no decoding in Python), just ensure child prints UTF-8
    result = subprocess.run(evaluator_cmd, env=env)
    if result.returncode != 0:
        print("Evaluation exited with non-zero status.")


def handle_question_generation():
    """Handle question generation from textbook"""
    print("\n=== Question Generation ===")
    path_str = input("Enter path to textbook (PDF or DOCX): ").strip().strip('"')
    input_path = Path(path_str)
    if not input_path.exists():
        print("Error: File not found.")
        return
    
    # Check file type
    file_extension = input_path.suffix.lower()
    if file_extension not in ['.pdf', '.docx']:
        print(f"Error: Unsupported file type '{file_extension}'. Only PDF and DOCX files are supported.")
        return
    
    print(f"Detected file type: {file_extension.upper()}")
    if file_extension == '.docx':
        print("Note: DOCX files support image extraction and will include diagrams in the output.")
    else:
        print("Note: PDF files will generate questions without diagrams.")
    
    try:
        # Import and run the question generation pipeline
        from generation.pipeline import run_pipeline
        
        output_file = input("Enter output filename (default: questions.json): ").strip()
        if not output_file:
            output_file = "questions.json"
        
        questions_per_topic = input("How many questions per topic? (default: 2): ").strip()
        if questions_per_topic:
            try:
                questions_per_topic = int(questions_per_topic)
            except ValueError:
                print("Invalid number, using default: 2")
                questions_per_topic = 2
        else:
            questions_per_topic = 2
        
        print(f"\nGenerating {questions_per_topic} questions per topic from: {input_path}")
        run_pipeline(str(input_path), output_file, questions_per_topic)
        print(f"\nQuestion generation completed! Check {output_file} and final_questions.json")
        
    except Exception as e:
        print(f"Error during question generation: {e}")

def handle_upload_answer():
    """Handle uploading student answer for evaluation"""
    print("\n=== Upload Student Answer ===")
    path_str = input("Enter path to student answer document (PDF/DOCX/PNG/JPG): ").strip().strip('"')
    input_path = Path(path_str)
    # Input files for processing are typically local
    if not input_path.exists():
        print("Error: File not found.")
        return
    
    # Check file type
    file_extension = input_path.suffix.lower()
    if file_extension not in ['.pdf', '.docx', '.png', '.jpg', '.jpeg']:
        print(f"Error: Unsupported file type '{file_extension}'. Only PDF, DOCX, PNG, and JPG files are supported for student answers.")
        return
    
    try:
        # Run the parsing process
        final_parsed_path = run_parse(input_path, STUDENT_ANSWER_DIR)
        parsed = load_json(final_parsed_path)
        
        # Transform and save student answer
        transformed = transform_parsed_to_schema(parsed, for_answer_key=False)
        save_path = STUDENT_ANSWER_DIR / "student_answer.json"
        save_json(save_path, transformed)
        print(f"Student answer processed and saved to: {save_path}")
        
    except Exception as e:
        print(f"Error processing student answer: {e}")

def handle_answer_evaluation():
    """Handle answer evaluation"""
    print("\n=== Answer Evaluation ===")
    
    # Check if answer key exists
    answer_key_path = ANSWER_KEY_DIR / "answer_key.json"
    if not file_exists(answer_key_path):
        print(f"Answer key not found at {answer_key_path}")
        print("Please upload the answer key first (option 2).")
        return
    
    # Check if student answer exists
    student_answer_path = STUDENT_ANSWER_DIR / "student_answer.json"
    if not file_exists(student_answer_path):
        print(f"Student answer not found at {student_answer_path}")
        print("Please upload the student answer first (option 3).")
        return
    
    try:
        # Run evaluation
        evaluator_cmd = [
            sys.executable,
            "-m", "evaluator.answer_evaluator",
            str(STUDENT_ANSWER_DIR / "student_answer.json"),
            str(ANSWER_KEY_DIR / "answer_key.json"),
        ]
        print("Running evaluation...\n")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        # Inherit parent stdio (no decoding in Python), just ensure child prints UTF-8
        result = subprocess.run(evaluator_cmd, env=env)
        if result.returncode != 0:
            print("Evaluation exited with non-zero status.")
        else:
            print("Evaluation completed! Check the output files.")
        
    except Exception as e:
        print(f"Error during evaluation: {e}")

def main():
    while True:
        print("\n=== Main Menu ===")
        print("1) Generate Questions from Textbook")
        print("2) Upload Answer Key")
        print("3) Upload Student Answer")
        print("4) Evaluate Student Answer")
        print("q) Quit")
        choice = input("Select an option: ").strip().lower()

        if choice == "1":
            handle_question_generation()
        elif choice == "2":
            handle_upload_answer_key()
        elif choice == "3":
            handle_upload_answer()
        elif choice == "4":
            handle_answer_evaluation()
        elif choice in {"q", "quit", "exit"}:
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()


