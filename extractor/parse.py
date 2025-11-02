import os
import sys
import json
from dotenv import load_dotenv
from .handle_pdf import convert_pdf_to_images
from .extract import extract_json
from .structure import convert_to_final_format
from .handle_docx import extract_from_docx_table  # import your DOCX handler

# Load environment variables
load_dotenv()

# Import storage client for persistent file operations
try:
    from storage import get_storage_client, should_use_temp_local
    _storage_available = True
except ImportError:
    _storage_available = False

# ====== CONFIG ======
# Poppler path - check environment variable first, then use Windows default or None for Linux
import platform
POPPLER_PATH_ENV = os.getenv("POPPLER_PATH")
if POPPLER_PATH_ENV:
    POPPLER_PATH = POPPLER_PATH_ENV
elif platform.system() == "Windows":
    POPPLER_PATH = r"C:\poppler-25.07.0\Library\bin"  # Windows default
else:
    POPPLER_PATH = None  # Linux/Mac - Poppler should be in PATH
OUTPUT_FOLDER = "./output"

# Check if custom output folder is provided via environment variable
if os.getenv("CUSTOM_OUTPUT_FOLDER"):
    OUTPUT_FOLDER = os.getenv("CUSTOM_OUTPUT_FOLDER")

# Get Azure credentials from environment
AZURE_ENDPOINT = os.getenv("AZURE_AI_VISION_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_AI_VISION_KEY")

if not AZURE_ENDPOINT or not AZURE_KEY:
    print("Error: Azure AI Vision credentials not found.")
    print("Please set AZURE_AI_VISION_ENDPOINT and AZURE_AI_VISION_KEY in your .env file.")
    sys.exit(1)

# ====== STEP 0: Get input file from terminal ======
if len(sys.argv) < 2:
    print("Usage: python -m extractor.parse <input_file>")
    sys.exit(1)

INPUT_FILE = sys.argv[1]
INPUT_FILE = os.path.abspath(INPUT_FILE)  # Ensure absolute path

if not os.path.exists(INPUT_FILE):
    print(f"Error: File '{INPUT_FILE}' does not exist.")
    sys.exit(1)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ====== STEP 1: Handle PDF, DOCX, or image ======
structured_json_files = []

if INPUT_FILE.lower().endswith(".pdf"):
    # Convert PDF pages to images
    image_files = convert_pdf_to_images(
        INPUT_FILE, 
        output_folder=os.path.join(OUTPUT_FOLDER, "pages"), 
        poppler_path=POPPLER_PATH
    )

    # Extract JSON from each image using Azure
    for idx, img_path in enumerate(image_files, start=1):
        data = extract_json(img_path, AZURE_ENDPOINT, AZURE_KEY, output_folder=OUTPUT_FOLDER)
        page_json_file = os.path.join(OUTPUT_FOLDER, f"structured_output_page_{idx}.json")
        
        # Save to storage (blob or local)
        if _storage_available and not should_use_temp_local(page_json_file):
            storage = get_storage_client()
            storage.write_json(page_json_file, data)
        else:
            # Local file system fallback
            os.makedirs(os.path.dirname(page_json_file), exist_ok=True)
            with open(page_json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        structured_json_files.append(page_json_file)

elif INPUT_FILE.lower().endswith(".docx"):
    # Directly extract typed answers + diagrams from DOCX
    data = extract_from_docx_table(INPUT_FILE, output_file=os.path.join(OUTPUT_FOLDER, "structured_output_docx.json"))
    # For DOCX, the extractor already returns the final per-question structure
    final_output_file = os.path.join(OUTPUT_FOLDER, "final_answer.json")
    
    # Save to storage (blob or local)
    if _storage_available and not should_use_temp_local(final_output_file):
        storage = get_storage_client()
        storage.write_json(final_output_file, data)
    else:
        # Local file system fallback
        os.makedirs(os.path.dirname(final_output_file), exist_ok=True)
        with open(final_output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Final structured JSON saved to {final_output_file}")
    sys.exit(0)

elif INPUT_FILE.lower().endswith((".png", ".jpg", ".jpeg")):
    # Directly extract JSON from image
    data = extract_json(INPUT_FILE, AZURE_ENDPOINT, AZURE_KEY, output_folder=OUTPUT_FOLDER)
    image_json_file = os.path.join(OUTPUT_FOLDER, "structured_output_image.json")
    
    # Save to storage (blob or local)
    if _storage_available and not should_use_temp_local(image_json_file):
        storage = get_storage_client()
        storage.write_json(image_json_file, data)
    else:
        # Local file system fallback
        os.makedirs(os.path.dirname(image_json_file), exist_ok=True)
        with open(image_json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    structured_json_files.append(image_json_file)

else:
    print("Error: Unsupported file type. Only PDF, DOCX, and PNG/JPG are supported.")
    sys.exit(1)

# ====== STEP 2: Convert to final structured JSON ======
final_output_file = os.path.join(OUTPUT_FOLDER, "final_answer.json")
convert_to_final_format(structured_json_files, final_output_file)
print(f"[SUCCESS] Final structured JSON saved to {final_output_file}")
