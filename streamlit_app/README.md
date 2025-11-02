# AI Question Generator & Answer Evaluator - Streamlit App

A comprehensive web application for generating questions from textbooks and evaluating student answers using AI.

## Features

### 📝 Question Generation
- Upload textbooks in PDF or DOCX format
- AI-powered question generation with Bloom's taxonomy classification
- Interactive manual review interface
- Generate question papers and answer keys in DOCX format
- Support for diagrams and images in DOCX files

### 📊 Answer Evaluation
- Upload answer keys in JSON or DOCX format
- Upload student answers in multiple formats (PDF, DOCX, JSON, PNG, JPG)
- Comprehensive evaluation with multiple metrics:
  - Semantic similarity
  - BLEU score
  - ROUGE-L score
  - Keyword coverage
  - Bloom's taxonomy analysis
  - Image comparison
- Detailed reports with visualizations
- Export results to Excel, CSV, and Markdown

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Navigate to the Streamlit app directory**:
   ```bash
   cd streamlit_app
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install additional dependencies** (if needed):
   ```bash
   # For CLIP image comparison
   pip install git+https://github.com/openai/CLIP.git
   
   # For NLTK data
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

## Running the Application

### Local Development

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8501
   ```

### Production Deployment

#### Option 1: Streamlit Cloud (Recommended)

1. **Push your code to GitHub**
2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
3. **Connect your GitHub repository**
4. **Deploy the app**

#### Option 2: Docker Deployment

1. **Create a Dockerfile**:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and run**:
   ```bash
   docker build -t question-generator .
   docker run -p 8501:8501 question-generator
   ```

#### Option 3: Heroku Deployment

1. **Create a Procfile**:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy to Heroku**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## Usage

### Question Generation Workflow

1. **Navigate to Question Generation page**
2. **Upload a textbook** (PDF or DOCX)
3. **Configure settings**:
   - Number of questions per topic
   - Advanced options (diagrams, Bloom's distribution, etc.)
4. **Generate questions** and wait for processing
5. **Review questions** in the manual review interface:
   - Approve/reject questions
   - Edit question text
   - Filter by Bloom's level or marks
6. **Generate final documents**:
   - Question paper (DOCX)
   - Answer key (DOCX)

### Answer Evaluation Workflow

1. **Navigate to Answer Evaluation page**
2. **Upload answer key** (JSON or DOCX)
3. **Upload student answer** (PDF, DOCX, JSON, PNG, JPG)
4. **Configure evaluation options**:
   - Image comparison
   - Semantic similarity weight
   - Bloom's taxonomy analysis
   - Keyword coverage weight
5. **Run evaluation** and wait for processing
6. **Review results**:
   - Overall summary
   - Performance charts
   - Detailed question analysis
   - Score distribution
7. **Export results**:
   - Detailed report (Markdown)
   - Excel spreadsheet
   - CSV file

## File Structure

```
streamlit_app/
├── app.py                          # Main Streamlit application
├── pages/
│   ├── question_generation.py      # Question generation page
│   └── answer_evaluation.py        # Answer evaluation page
├── utils/
│   ├── file_handlers.py           # File upload and handling utilities
│   └── pipeline_integration.py    # Integration with existing pipeline
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── temp_files/                     # Temporary file storage (auto-created)
```

## Configuration

### Environment Variables

Create a `.env` file in the `streamlit_app` directory:

```env
# API Keys (if using external services)
OPENAI_API_KEY=your_openai_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# File upload limits
MAX_FILE_SIZE_MB=50
MAX_QUESTIONS_PER_TOPIC=10

# Processing settings
ENABLE_IMAGE_COMPARISON=true
ENABLE_BLOOM_ANALYSIS=true
```

### Streamlit Configuration

Create a `.streamlit/config.toml` file:

```toml
[server]
port = 8501
address = "0.0.0.0"

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[browser]
gatherUsageStats = false
```

## Troubleshooting

### Common Issues

1. **File upload errors**:
   - Check file size (max 50MB)
   - Verify file format is supported
   - Ensure file is not corrupted

2. **Processing errors**:
   - Check if all dependencies are installed
   - Verify file paths and permissions
   - Check console for error messages

3. **Memory issues**:
   - Reduce file size
   - Close other applications
   - Restart the Streamlit app

### Performance Optimization

1. **For large files**:
   - Use smaller file sizes
   - Process in batches
   - Enable file compression

2. **For slow processing**:
   - Check system resources
   - Optimize file formats
   - Use faster hardware

## Development

### Adding New Features

1. **Create new page**:
   ```python
   # In pages/ directory
   def show_new_page():
       st.markdown("# New Page")
       # Your code here
   ```

2. **Add navigation**:
   ```python
   # In app.py
   if st.button("New Page"):
       st.session_state.current_page = 'new_page'
   ```

3. **Update requirements**:
   ```bash
   pip freeze > requirements.txt
   ```

### Testing

1. **Run tests**:
   ```bash
   python -m pytest tests/
   ```

2. **Test file uploads**:
   - Use sample files from the `input/` directory
   - Test different file formats
   - Verify file size limits

## Support

For issues and questions:

1. **Check the troubleshooting section**
2. **Review the console logs**
3. **Check file formats and sizes**
4. **Verify all dependencies are installed**

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Acknowledgments

- Built with Streamlit
- Uses existing question generation and evaluation pipelines
- Integrates with various AI models and libraries
- Supports multiple file formats and processing options
