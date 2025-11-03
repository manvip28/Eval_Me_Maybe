# AI-Powered Question Generation and Answer Evaluation System

An intelligent system that generates educational questions from textbooks and evaluates student answers using AI models.

## Features

### Core Features
- **Question Generation**: Generate questions from PDF/DOCX textbooks using Mistral AI
- **Answer Generation**: Automatically generate answers for created questions
- **Answer Evaluation**: Evaluate student answers against answer keys with comprehensive scoring
- **Image Processing**: Extract and analyze images/diagrams from documents using Azure AI Vision
- **Bloom's Taxonomy**: Categorize questions by cognitive levels (Remember, Understand, Apply, Analyze, Evaluate, Create)
- **Manual Review**: Review and approve generated questions before final document generation
- **Interactive Interfaces**: Both CLI and Streamlit web interfaces

### Storage & Cloud Features
- **Azure Blob Storage Integration**: All files (textbooks, generated questions, diagrams, documents) stored in Azure cloud
- **Automatic Cloud Backup**: Combined evaluation reports automatically backed up to Azure
- **No Local Storage**: All generated content exclusively uses Azure Blob Storage (no local files)

### Report Generation
- **Combined Report**: Generate a single DOCX report with all student evaluations
- **Individual Reports**: Generate separate DOCX reports for each student (with filename as student name)
- **Smart Download**: 
  - ≤10 students: Individual download buttons for each report
  - >10 students: ZIP file download
- **Automatic Backup**: Combined reports saved to Azure for safety

## Setup

You can install the application using **Docker** (recommended) or **manual installation**. Docker automatically includes all dependencies including Poppler.

---

## 🐳 Installation with Docker (Recommended)

Docker installation automatically includes all dependencies and system tools (Poppler, etc.) - no manual setup needed!

### Prerequisites
- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

### Quick Start

1. **Build and run with Docker Compose:**
   ```bash
   # Build and start the container
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Stop the container
   docker-compose down
   ```

2. **Access the application:**
   Open your browser and go to: `http://localhost:8501`

### Using Pre-built Docker Image (From Docker Hub)

If you prefer to use a pre-built Docker image instead of building locally, the app is available on Docker Hub.

#### Steps to Run with Pre-built Image

1. **Pull the image:**
   ```bash
   docker pull manvip28/majorproject-app:latest
   ```

2. **Run the container with environment variables:**

   **Option 1: Using .env file (Recommended)**
   ```bash
   docker run -d \
     -p 8501:8501 \
     --env-file .env \
     --name ai-question-generator \
     manvip28/majorproject-app:latest
   ```

   **Option 2: Set environment variables directly**
   ```bash
   docker run -d \
     -p 8501:8501 \
     -e OPENROUTER_API_KEY=your_key \
     -e AZURE_AI_VISION_ENDPOINT=your_endpoint \
     -e AZURE_AI_VISION_KEY=your_key \
     -e AZURE_STORAGE_CONNECTION_STRING=your_connection_string \
     -e AZURE_CONTAINER_NAME=your_container \
     -e STORAGE_TYPE=blob \
     --name ai-question-generator \
     manvip28/majorproject-app:latest
   ```

3. **Access the application:**
   Open your browser and go to: `http://localhost:8501`

4. **View logs:**
   ```bash
   docker logs -f ai-question-generator
   ```

5. **Stop the container:**
   ```bash
   docker stop ai-question-generator
   docker rm ai-question-generator
   ```

#### Important Notes

⚠️ **Requirements:**
- Docker must be installed on your system
- No need to install Python, dependencies, or Poppler manually — everything is included in the Docker image
- You must provide your own `.env` file or environment variables with API keys and Azure credentials

⚠️ **Environment Variables Required:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `AZURE_AI_VISION_ENDPOINT` - Your Azure AI Vision endpoint
- `AZURE_AI_VISION_KEY` - Your Azure AI Vision key
- `AZURE_STORAGE_CONNECTION_STRING` - Your Azure Storage connection string
- `AZURE_CONTAINER_NAME` - Your Azure container name
- `STORAGE_TYPE=blob` - Set to "blob" for Azure storage

> **Note:** The pre-built image includes all dependencies (Python packages, Poppler, Tesseract, spaCy model, NLTK data, CLIP) — no manual setup needed!

### What's Included in Docker

✅ **All Python dependencies** (PyTorch, CLIP, spaCy, etc.)  
✅ **System dependencies** (Poppler for PDF processing, Tesseract OCR)  
✅ **Pre-configured models:**
   - spaCy English model (`en_core_web_sm`)
   - NLTK data (punkt tokenizer, stopwords)
   - CLIP model (downloads on first use)
   - Sentence Transformer models (download on first use)

✅ **No manual setup needed** - Everything is pre-configured!

### Docker Commands (Local Build)

```bash
# Build the image
docker-compose build

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild from scratch (if needed)
docker-compose build --no-cache
```

### Docker Notes

- **Azure Storage**: All files are stored in Azure Blob Storage (cloud) - no local volume mounts needed
- **Session State**: Streamlit session state is in-memory (ephemeral) - no volume mounts needed
- **Stateless Container**: Container is completely stateless - all data in Azure cloud

---

## 📦 Manual Installation

If you prefer to install manually (without Docker):

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install CLIP from GitHub

```bash
pip install git+https://github.com/openai/CLIP.git
```

### 3. Environment Variables & API Keys

Create a `.env` file in the project root with your API keys:

```env
# API Keys - Add your actual keys here
OPENROUTER_API_KEY=your_openrouter_api_key_here
AZURE_AI_VISION_KEY=your_azure_ai_vision_key_here
AZURE_AI_VISION_ENDPOINT=your_azure_ai_vision_endpoint_here

# Azure Blob Storage Configuration
STORAGE_TYPE=blob
AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string_here
AZURE_CONTAINER_NAME=your_container_name_here

# Optional: Other configuration
DEFAULT_MODEL=mistralai/mistral-7b-instruct
DEFAULT_TEMPERATURE=0.7

# Optional: Poppler path (Windows only - uncomment and update if Poppler is not in PATH)
# POPPLER_PATH=C:\poppler\Library\bin
```

#### How to Get API Keys

#### OpenRouter API Key
1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up and get your API key
3. Add it to your `.env` file

#### Azure AI Vision Key
1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a Computer Vision resource
3. Get your endpoint and key
4. Add them to your `.env` file

#### Azure Blob Storage (Required for Cloud Storage)
1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a Storage Account
3. Create a Blob Container (or use existing one)
4. Get your Storage Account connection string from "Access keys"
5. Add to your `.env` file:
   - `STORAGE_TYPE=blob`
   - `AZURE_STORAGE_CONNECTION_STRING=your_connection_string`
   - `AZURE_CONTAINER_NAME=your_container_name`

**Note:** If you don't configure Azure Blob Storage, the system will use local storage. However, for full functionality and cloud backup, Azure Blob Storage is recommended.

### 5. Install PDF Processing Tools (Manual Installation Only)

> **Note:** If you're using Docker, skip this section - Poppler and Tesseract are already included!

The project uses PDF processing tools that require separate installation.


#### Poppler (for PDF to Image Conversion)

Poppler is required for converting PDF pages to images. It's used by the `pdf2image` library.

**Windows:**
1. Download Poppler for Windows from [GitHub](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Download the latest release (e.g., `Release-XX.XX.X-X.zip`)
3. Extract the zip file to a location like:
   - `C:\poppler`
   - `C:\Program Files\poppler`
   - Or any folder you prefer
4. Remember the path to the `bin` folder inside the extracted directory (e.g., `C:\poppler\Library\bin`)
5. **Option 1 - Add to PATH:**
   - Open "Environment Variables" in System Properties
   - Add the `bin` folder to your PATH variable (e.g., `C:\poppler\Library\bin`)
6. **Option 2 - Set in .env file (recommended for this project):**
   - Add to your `.env` file: `POPPLER_PATH=C:\poppler\Library\bin`
   - Update the path in `extractor/parse.py` if needed (line 14)
   - Or update `extractor/handle_pdf.py` if using it directly (line 49)

**macOS:**
```bash
brew install poppler
```
Poppler will be automatically available after installation via Homebrew.

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

**Linux (Fedora):**
```bash
sudo dnf install poppler-utils
```

**Note:** On Windows, you may need to manually set the Poppler path in the code if it's not in your system PATH. The default path used in this project is `C:\poppler-25.07.0\Library\bin` (or similar version). Update the `POPPLER_PATH` variable in `extractor/parse.py` to match your installation location.

**Verification:**
After installation, verify that the tools are accessible:

```bash

# Check Poppler (if in PATH)
pdftoppm -h
# OR on Windows, if not in PATH:
# C:\poppler\Library\bin\pdftoppm.exe -h
```

**Troubleshooting Poppler on Windows:**
- If you get "poppler not found" errors, ensure the path points to the `bin` folder (not the root poppler folder)
- The path should end with `\Library\bin` or `\bin` depending on your extraction location
- You can test the path by running: `C:\poppler\Library\bin\pdftoppm.exe -h` (replace with your actual path)
- If errors persist, try adding the full path to `extractor/parse.py` line 14

### 6. Download Python Models and Data (Manual Installation Only)

> **Note:** If you're using Docker, skip this section - Models are already downloaded during build!

**Important:** While `spacy` and `nltk` are installed via `requirements.txt`, their models and data need to be downloaded separately.

#### spaCy English Model

The `spacy` library is in `requirements.txt`, but the English language model must be downloaded separately:

```bash
python -m spacy download en_core_web_sm
```

**Why separate?** The spaCy library (the framework) is installed via pip, but language models are separate packages that need to be downloaded using spaCy's download command.

**Alternative (if the above doesn't work):**
```bash
# Download and install directly via pip
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

#### NLTK Data

The `nltk` library is in `requirements.txt`, but the data files (punkt tokenizer and stopwords) are not included in the pip package. They download automatically on first use, but it's recommended to download them manually first:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

**Why separate?** NLTK stores its data separately from the library code. The code will auto-download on first run, but manual download ensures they're available immediately.

## Usage

### CLI Interface

Run the command-line interface:

```bash
python main.py
```

This will show a menu with options:
1. **Generate Questions from Textbook**: Upload a textbook and generate questions
2. **Upload Answer Key**: Upload and process answer key files
3. **Upload Student Answer**: Upload and process student answer files
4. **Evaluate Student Answer**: Evaluate student answers against answer keys

### Streamlit Interface

Run the Streamlit web application:

```bash
streamlit run app.py
```

This will launch a web interface with the following features:

#### Question Generation Page
- **📤 Upload PDF/DOCX**: Upload your textbook file (automatically saved to Azure)
- **🚀 Generate Questions**: Start the question generation process
- **✅ Approve/❌ Reject**: Review and approve questions before document generation
- **📄 Generate Question Paper**: Generate final question paper DOCX document
- **📄 Generate Answer Key**: Generate final answer key DOCX document
- **📥 Download Question Paper**: Download the generated question paper
- **📥 Download Answer Key**: Download the generated answer key
- **🔄 Regenerate Documents**: Regenerate documents if needed

#### Answer Evaluation Page
- **📋 Upload Answer Key**: Upload answer key file (JSON or DOCX)
- **📝 Upload Student Answer(s)**: Upload one or more student answer files
- **📊 Evaluate Answers**: Start evaluation process
- **📄 Generate & Download Combined Report**: Generate single DOCX with all students
- **📄 Generate & Download Individual Reports**: Generate separate DOCX files for each student
- **📥 Download All Student Reports**: 
  - If ≤10 students: Individual download buttons for each report
  - If >10 students: Download as ZIP file

## Project Structure

```
├── generation/                 # Question generation pipeline
│   ├── pipeline.py            # Main generation pipeline
│   ├── question_generation/   # Question generation modules
│   └── utils/                 # Utility functions (image extraction, association)
├── extractor/                 # Document extraction
├── evaluator/                 # Answer evaluation
│   ├── answer_evaluator.py    # Main evaluation logic
│   ├── report_generator.py    # DOCX report generation
│   └── clip_image_compare.py # Image comparison using CLIP
├── storage/                    # Storage abstraction layer
│   ├── storage_client.py      # Azure Blob Storage and Local storage client
│   └── __init__.py           # Storage exports
├── streamlit_app/             # Streamlit web application
│   ├── utils/
│   │   ├── pages/            # Page components
│   │   ├── pipeline/         # Pipeline integration
│   │   ├── evaluation/       # Evaluation UI components
│   │   ├── document/         # Document generation
│   │   └── file/             # File upload handlers
│   └── app.py                # Streamlit app entry point
├── input/                     # Input documents (legacy)
├── output/                    # Generated outputs (legacy)
├── local_uploads/            # Local file storage (fallback only)
├── main.py                   # CLI application
├── app.py                    # Streamlit application
├── requirements.txt          # Dependencies
└── .env                      # Environment variables (create this)
```

### Azure Blob Storage Structure

All files are stored in Azure Blob Storage with the following structure:
```
Azure Container/
├── uploads/
│   ├── textbook/            # Uploaded textbook files
│   ├── answer_key/          # Uploaded answer key files
│   └── student_answer/      # Uploaded student answer files
├── answer_key_gen/
│   ├── intermediate_questions.json    # Generated questions (before approval)
│   ├── final_questions.json           # Approved questions
│   ├── question_paper.docx            # Final question paper
│   ├── final_answer_key.docx          # Final answer key
│   └── diagrams/                      # Extracted diagrams/images
│       └── diagram_*.png
└── evaluation_reports/
    └── combined_report_all_students.docx    # Combined evaluation report (backed up)
```

## API Integration

### OpenRouter (Mistral AI)
- Used for question and answer generation
- Supports various models via OpenRouter API
- Configurable model selection

### Azure AI Vision
- Used for document analysis and image extraction
- Extracts text and diagrams from documents
- Supports PDF, DOCX, and image formats

## Configuration

### Models
- Default: `mistralai/mistral-7b-instruct`
- Configurable via environment variables
- Supports other OpenRouter models

### Question Generation
- Configurable questions per topic
- Bloom's taxonomy categorization
- Keyword-based content selection
- Duplicate detection and filtering

### Answer Evaluation
- CLIP-based image comparison
- Text similarity analysis (semantic, BLEU, ROUGE-L)
- Bloom's taxonomy alignment
- Keyword coverage analysis
- Comprehensive scoring with weighted metrics


### Common Issues

1. **API Key Errors**
   - Ensure `.env` file exists with correct keys
   - Check API key validity and permissions

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Download spaCy model: `python -m spacy download en_core_web_sm`
   - Download NLTK data: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`
   - Ensure Poppler is installed (for PDF to image conversion on Windows)
   - Install PyMuPDF for image extraction: `pip install PyMuPDF`

3. **PDF Processing Issues**
   - Ensure PDF is not password protected
   - Check file format compatibility
   - Ensure Poppler is installed correctly and accessible
   - On Windows, verify the Poppler path in `extractor/parse.py` matches your installation
   - If using `.env`, ensure `POPPLER_PATH` is set correctly
   - Test Poppler manually: `pdftoppm -h` (or `C:\poppler\Library\bin\pdftoppm.exe -h` on Windows)

4. **spaCy Model Issues**
   - If you get "Can't find model 'en_core_web_sm'", download it:
     ```bash
     python -m spacy download en_core_web_sm
     ```
   - Verify installation: `python -c "import spacy; spacy.load('en_core_web_sm')"`

5. **NLTK Data Issues**
   - If NLTK data download fails, download manually:
     ```bash
     python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
     ```
   - On some systems, NLTK may require additional data - check error messages

6. **Memory Issues**
   - Reduce batch sizes for large documents
   - Use smaller models for limited resources
   - First-time model downloads can use significant disk space (1-2 GB)
   - Ensure sufficient RAM for large documents (recommended: 8GB+)

7. **Model Download Issues**
   - Ensure stable internet connection for first-time model downloads
   - Sentence Transformer and CLIP models are large (500MB-1GB)
   - Models download automatically on first use - be patient
   - If downloads fail, check firewall/antivirus settings

8. **Azure Blob Storage Issues**
   - Ensure `STORAGE_TYPE=blob` is set in `.env` file
   - Verify `AZURE_STORAGE_CONNECTION_STRING` is correct
   - Verify `AZURE_CONTAINER_NAME` exists in your storage account
   - Check that the storage account and container allow the required permissions
   - If uploads fail, check Azure portal for container access and permissions

9. **File Not Found Errors**
   - If you see "Textbook not found in Azure blob storage", ensure the file was uploaded successfully
   - Check that Azure Blob Storage is properly configured
   - Verify the file appears in Azure portal under the specified container

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all dependencies are installed
4. Verify API keys are correct
