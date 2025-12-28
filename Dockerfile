# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - poppler-utils: Required for pdf2image (PDF to image conversion)
# - tesseract-ocr: Required for pytesseract (OCR functionality)
# - git: Required for installing CLIP from GitHub
# - build-essential: Required for building Python packages (including CLIP)
# - wget: For downloading files if needed
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    git \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Note: CLIP requires git installation, handled separately
RUN pip install --no-cache-dir --upgrade pip && \
    # First install CLIP from git (before other packages that might conflict)
    # This ensures CLIP is built properly before other dependencies
    pip install --no-cache-dir git+https://github.com/openai/CLIP.git && \
    # Then install all other requirements
    # Pip will skip CLIP if already installed, but we install it first to ensure proper build order
    pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Download NLTK data (punkt tokenizer and stopwords)
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')" || exit 1

# Default command: run Streamlit app
CMD sh -c "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"
