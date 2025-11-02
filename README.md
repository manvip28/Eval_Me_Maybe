# AI-Powered Question Generation and Answer Evaluation System

An intelligent system that generates educational questions from textbooks and evaluates student answers using AI models.

## Features

- **Question Generation**: Generate questions from PDF textbooks using Mistral AI
- **Answer Generation**: Automatically generate answers for created questions
- **Answer Evaluation**: Evaluate student answers against answer keys
- **Image Processing**: Extract and analyze images from documents using Azure AI Vision
- **Bloom's Taxonomy**: Categorize questions by cognitive levels
- **Interactive Interfaces**: Both CLI and Streamlit web interfaces

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root with your API keys:
Edit `.env` file with your actual API keys:

```env
# API Keys - Add your actual keys here
OPENROUTER_API_KEY=your_openrouter_api_key_here
AZURE_AI_VISION_KEY=your_azure_ai_vision_key_here
AZURE_AI_VISION_ENDPOINT=your_azure_ai_vision_endpoint_here

# Optional: Other configuration
DEFAULT_MODEL=mistralai/mistral-7b-instruct
DEFAULT_TEMPERATURE=0.7

# Optional: Poppler path (Windows only - uncomment and update if Poppler is not in PATH)
# POPPLER_PATH=C:\poppler\Library\bin

# Optional: Tesseract OCR path (Windows only - uncomment and update if Tesseract is not in PATH)
# TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

### 3. Get API Keys

#### OpenRouter API Key
1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up and get your API key
3. Add it to your `.env` file

#### Azure AI Vision Key
1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a Computer Vision resource
3. Get your endpoint and key
4. Add them to your `.env` file

### 4. Install OCR and PDF Processing Tools

The project uses OCR (Optical Character Recognition) and PDF processing tools that require separate installation.

#### Tesseract OCR

**Windows:**
1. Download Tesseract installer from [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install the `.exe` file (recommended: `tesseract-ocr-w64-setup-*.exe`)
3. During installation, remember the installation path (default: `C:\Program Files\Tesseract-OCR`)
4. Add Tesseract to your system PATH:
   - Open "Environment Variables" in System Properties
   - Add `C:\Program Files\Tesseract-OCR` to the PATH variable
   - Or add to your `.env` file: `TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata`

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Linux (Fedora):**
```bash
sudo dnf install tesseract
```

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
# Check Tesseract
tesseract --version

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

### 5. Download Python Models and Data

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
1. Generate Questions from Textbook
2. Upload Answer Key
3. Upload Student Answer
4. Evaluate Student Answer

### Streamlit Interface

Run the Streamlit web application:

```bash
streamlit run app.py
```

This will launch a web interface where you can:
- Generate questions from textbooks
- Review and approve questions
- Evaluate student answers
- Download reports and documents

## Project Structure

```
├── generation/                 # Question generation pipeline
│   ├── pipeline.py            # Main generation pipeline
│   ├── question_generation/   # Question generation modules
│   └── utils/                 # Utility functions
├── extractor/                 # Document extraction
├── evaluator/                 # Answer evaluation
├── streamlit_app/             # Streamlit web application
├── input/                     # Input documents
├── output/                    # Generated outputs
├── main.py                    # CLI application
├── app.py                     # Streamlit application
├── requirements.txt           # Dependencies
└── .env                       # Environment variables (create this)
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
- Text similarity analysis
- Bloom's taxonomy alignment
- Comprehensive scoring

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `.env` file exists with correct keys
   - Check API key validity and permissions

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Download spaCy model: `python -m spacy download en_core_web_sm`
   - Download NLTK data: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`
   - Ensure Tesseract OCR is installed and accessible
   - Ensure Poppler is installed (for PDF to image conversion on Windows)
   - Install PyMuPDF for image extraction: `pip install PyMuPDF`

3. **PDF Processing Issues**
   - Ensure PDF is not password protected
   - Check file format compatibility
   - Ensure Poppler is installed correctly and accessible
   - On Windows, verify the Poppler path in `extractor/parse.py` matches your installation
   - If using `.env`, ensure `POPPLER_PATH` is set correctly
   - Test Poppler manually: `pdftoppm -h` (or `C:\poppler\Library\bin\pdftoppm.exe -h` on Windows)

4. **OCR Issues (Tesseract)**
   - Verify Tesseract is installed: `tesseract --version`
   - Check if Tesseract is in your PATH
   - On Windows, ensure `TESSDATA_PREFIX` points to the `tessdata` folder
   - If pytesseract can't find Tesseract, set the path manually:
     ```python
     import pytesseract
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

5. **spaCy Model Issues**
   - If you get "Can't find model 'en_core_web_sm'", download it:
     ```bash
     python -m spacy download en_core_web_sm
     ```
   - Verify installation: `python -c "import spacy; spacy.load('en_core_web_sm')"`

6. **NLTK Data Issues**
   - If NLTK data download fails, download manually:
     ```bash
     python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
     ```
   - On some systems, NLTK may require additional data - check error messages

7. **Memory Issues**
   - Reduce batch sizes for large documents
   - Use smaller models for limited resources
   - First-time model downloads can use significant disk space (1-2 GB)
   - Ensure sufficient RAM for large documents (recommended: 8GB+)

8. **Model Download Issues**
   - Ensure stable internet connection for first-time model downloads
   - Sentence Transformer and CLIP models are large (500MB-1GB)
   - Models download automatically on first use - be patient
   - If downloads fail, check firewall/antivirus settings

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=1
```
Then run either `python main.py` or `streamlit run app.py`

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
