# AI-Powered Question Generation & Answer Evaluation System

[![Docker Pulls](https://img.shields.io/docker/pulls/manvip28/majorproject-app)](https://hub.docker.com/r/manvip28/majorproject-app)
![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-orange.svg)

An AI-powered system that generates exam questions from textbooks and evaluates student answers using NLP, OCR, image comparison, and Bloom's Taxonomy. Built with Mistral (via OpenRouter), Azure AI Vision, Sentence Transformers, and CLIP. Supports full cloud storage via Azure Blob.

---

## 🎥 Project Demo

https://github.com/user-attachments/assets/3374a5b6-1f5b-403a-88ae-0ebacfeea8fc


## ✨ Features

### 🔹 Question & Answer Generation
- Generate questions from PDF/DOCX using Mistral AI
- Auto-generate detailed answers
- Extract text & diagrams using Azure AI Vision
- Tag questions with Bloom's Taxonomy
- Approve or reject generated questions via UI
- Generate question paper & answer key (DOCX)

### 🔹 AI-Based Answer Evaluation
- Evaluate student answers against generated keys
- Multi-stage scoring:
  - Semantic similarity (SBERT)
  - Keyword matching
  - Bloom's Taxonomy validation
  - Image comparison (CLIP)
- Accept multiple student answer uploads
- Generate per-student or combined DOCX reports

### 🔹 Cloud & Storage
- Azure Blob Storage for:
  - Textbooks
  - Answer keys
  - Student uploads
  - Generated documents
- Automatic cloud backup
- No local files required

### 🔹 Interfaces
- Full Streamlit web UI
- Command-line interface (CLI)

---

## 📦 Installation Options

Choose based on your use case:
1. **Pre-built Docker Image (Recommended for end users)** - Fastest setup
2. **Docker Compose (Recommended for developers)** - Easy to modify
3. **Manual Installation** - No Docker required

---

## 🐳 1. Pre-built Docker Image (Recommended - Fastest Setup)

Includes all system dependencies (Poppler, Tesseract, NLTK data, spaCy model, CLIP downloads).

### Pull and run the image

### Pull the image
```bash
docker pull manvip28/majorproject-app:latest
```

### Run with .env file
```bash
docker run -d \
  -p 8501:8501 \
  --env-file .env \
  --name ai-question-engine \
  manvip28/majorproject-app:latest
```

## 🖥️ 3. Manual Installation (Without Docker)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env
```env
OPENROUTER_API_KEY=your_key
AZURE_AI_VISION_KEY=your_key
AZURE_AI_VISION_ENDPOINT=your_endpoint
AZURE_STORAGE_CONNECTION_STRING=your_conn
AZURE_CONTAINER_NAME=your_container
STORAGE_TYPE=blob
```

### 3. Install Poppler

**Windows:**
- Download Poppler: https://github.com/oschwartz10612/poppler-windows/releases/
- Set path: `POPPLER_PATH=C:\poppler\Library\bin`

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
sudo apt install poppler-utils
```

### 4. Install spaCy model
```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

### 5. Install NLTK data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## 🚀 Usage

### CLI
```bash
python main.py
```

### Streamlit App
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
generation/           # Question generation
extractor/            # PDF/DOCX extraction
evaluator/            # Answer evaluation + reports
storage/              # Azure/local storage
streamlit_app/        # Web UI
main.py               # CLI entry
app.py                # Streamlit entry
```

---

## ☁️ Azure Blob Storage Layout

```
uploads/
  textbook/
  answer_key/
  student_answer/
answer_key_gen/
  final_questions.json
  final_answer_key.docx
  diagrams/
evaluation_reports/
  combined_report_all_students.docx
```

---

## 🔗 API Integrations

**OpenRouter (Mistral)**  
Used for question and answer generation.

**Azure AI Vision**  
Used for document parsing, OCR, and diagram extraction.

---

## 📜 License

This project is licensed under the MIT License.
