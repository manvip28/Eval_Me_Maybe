# Setup Guide - AI Question Generator & Answer Evaluator

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Navigate to the streamlit_app directory
cd streamlit_app

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Run the Application

#### Option A: Using the Fixed Runner (Recommended)
```bash
python run_app.py
```

#### Option B: Using the Startup Scripts
**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

#### Option C: Manual Setup (if needed)
```bash
# Navigate to parent directory first
cd ..
# Then run from streamlit_app directory
cd streamlit_app
streamlit run app.py
```

### 3. Access the Application
- Open your browser and go to: `http://localhost:8501`
- The application should load with a beautiful interface

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "Missing ScriptRunContext" Warning
**Problem:** You're running `python app.py` instead of `streamlit run app.py`

**Solution:**
```bash
# ❌ Wrong way
python app.py

# ✅ Correct way
streamlit run app.py
```

#### 2. Import Errors
**Problem:** Missing dependencies or import errors

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# If you get specific import errors, install missing packages
pip install streamlit pandas plotly
```

#### 3. Port Already in Use
**Problem:** Port 8501 is already in use

**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port 8502

# Or kill the process using port 8501
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F

# Linux/Mac:
lsof -ti:8501 | xargs kill -9
```

#### 4. File Path Issues
**Problem:** Cannot find modules or files

**Solution:**
```bash
# Make sure you're in the correct directory
cd streamlit_app

# Check if all files exist
ls -la  # Linux/Mac
dir     # Windows
```

#### 5. Permission Issues (Linux/Mac)
**Problem:** Cannot execute startup script

**Solution:**
```bash
chmod +x start.sh
./start.sh
```

## 📁 Directory Structure

Make sure your directory structure looks like this:
```
streamlit_app/
├── app.py
├── pages/
│   ├── question_generation.py
│   └── answer_evaluation.py
├── utils/
│   ├── file_handlers.py
│   └── pipeline_integration.py
├── requirements.txt
├── start.bat
├── start.sh
└── .streamlit/
    └── config.toml
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Using Docker directly
```bash
# Build image
docker build -t question-generator .

# Run container
docker run -p 8501:8501 question-generator
```

## 🌐 Production Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy automatically

### Heroku
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## 🔍 Debugging

### Enable Debug Mode
```bash
streamlit run app.py --logger.level debug
```

### Check Logs
```bash
# Streamlit logs
streamlit run app.py --logger.level info

# Check for errors in console
```

### Common Error Messages

1. **"ModuleNotFoundError"**
   - Install missing dependencies: `pip install <module_name>`

2. **"Permission denied"**
   - Check file permissions
   - Run with appropriate privileges

3. **"Port already in use"**
   - Use different port: `--server.port 8502`
   - Kill existing process

4. **"File not found"**
   - Check file paths
   - Ensure you're in correct directory

## 📞 Support

If you're still having issues:

1. **Check the console output** for specific error messages
2. **Verify all dependencies** are installed correctly
3. **Ensure you're using the correct command**: `streamlit run app.py`
4. **Check file permissions** and directory structure
5. **Try running in a clean environment** (new virtual environment)

## ✅ Success Indicators

When everything is working correctly, you should see:
- Streamlit app starts without errors
- Browser opens automatically to `http://localhost:8501`
- Beautiful interface loads with navigation
- No import errors in console
- File upload and processing works
