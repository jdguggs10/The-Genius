# Fantasy AI Backend

> **The Brain Behind The Genius** - FastAPI server that powers your fantasy sports AI assistant

This is the backend API server that handles all the smart stuff - connecting to OpenAI's GPT-4.1, processing fantasy sports questions, and sending back intelligent responses. Think of it as the "brain" that makes your fantasy AI assistant work.

## 🧠 What This Does

This backend server:
- **Receives Questions**: Gets fantasy sports questions from your web app or mobile app
- **Talks to AI**: Sends questions to OpenAI's GPT-4.1 (the smartest AI available)
- **Returns Answers**: Sends back intelligent, detailed fantasy sports advice
- **Handles Web Search**: Can search the internet for current stats when needed
- **Manages CORS**: Makes sure your web app can talk to this server properly

## 🔧 Technology Stack (What's Under the Hood)

- **FastAPI**: Modern Python web framework (super fast and easy to use)
- **OpenAI GPT-4.1**: The latest AI model via Responses API (not Chat Completions)
- **Pydantic**: Ensures data is properly formatted and validated
- **Uvicorn**: Production-ready web server
- **Docker**: Containerization for easy deployment
- **Render.com**: Cloud hosting platform

## 📁 Project Structure

```
backend/
├── app/                           # Main application code
│   ├── services/                  # External service connections
│   │   └── openai_client.py      # Connects to OpenAI GPT-4.1
│   ├── models.py                  # Data structure definitions
│   └── main.py                    # Main server file with all endpoints
├── tests/                         # Automated tests
│   ├── test_main.py              # Tests for API endpoints
│   ├── test_openai_client.py     # Tests for OpenAI integration
│   └── test_responses_api.py     # Tests for Responses API
├── requirements.txt               # Python packages needed
├── requirements-test.txt          # Testing packages
├── pyproject.toml                # Poetry configuration (modern Python packaging)
├── Dockerfile                    # Instructions for Docker deployment
├── render.yaml                   # Render.com deployment settings
└── README.md                     # This file
```

## 🚀 Quick Start Guide

### Step 1: Get Your Environment Ready

**Install Python** (if you don't have it):
1. Go to [python.org](https://python.org)
2. Download Python 3.11 or newer
3. Install it (check "Add to PATH" on Windows)

**Get an OpenAI API Key**:
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an account or sign in
3. Click "API Keys" in the left menu
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)
6. **Important**: Add $5-10 credit to your OpenAI account

### Step 2: Download and Set Up the Code

```bash
# 1. Navigate to the backend folder
cd backend

# 2. Create a virtual environment (keeps your Python organized)
python3 -m venv venv

# 3. Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install all required packages
pip install -r requirements.txt
```

### Step 3: Configure Your Environment

**Create your environment file**:
```bash
# Copy the example file (if it exists)
cp .env.example .env

# Or create a new .env file
touch .env  # Mac/Linux
# On Windows, just create a new file called .env
```

**Edit the .env file** (use any text editor):
```env
# Required: Your OpenAI API Key
OPENAI_API_KEY=sk-your_actual_openai_key_here

# Optional: System prompt (how the AI should behave)
SYSTEM_PROMPT=You are a helpful fantasy sports assistant with deep knowledge of player performance, matchups, and strategy.
```

### Step 4: Test the Server

**Start the development server**:
```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python module
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using the main file directly
python app/main.py
```

**Test it's working**:
1. Open your web browser
2. Go to: `http://localhost:8000`
3. Should see: "🏆 Fantasy AI Backend - ✅ API is running successfully!"

**Test the API**:
1. Go to: `http://localhost:8000/docs`
2. You'll see an interactive API documentation page
3. Click on "POST /advice" 
4. Click "Try it out"
5. Use this test data:
```json
{
  "conversation": [
    {
      "role": "user",
      "content": "Should I start Patrick Mahomes or Josh Allen this week?"
    }
  ]
}
```
6. Click "Execute"
7. Should get back an AI response!

## 🌐 API Endpoints

### 1. `GET /` - Welcome Page
**What it does**: Shows you the API is running
**When to use**: Just to check if the server is alive
**Example**: Visit `http://localhost:8000` in your browser

### 2. `GET /health` - Health Check
**What it does**: Detailed server status with system information
**When to use**: To check if everything is working properly
**Response includes**:
- Server status
- System information (memory, CPU usage)
- Python version
- CORS settings

### 3. `POST /advice` - Get AI Fantasy Advice
**What it does**: Main endpoint - sends your question to GPT-4.1
**When to use**: This is the main endpoint your web app uses

**Request Format**:
```json
{
  "conversation": [
    {
      "role": "user",
      "content": "Your fantasy question here"
    }
  ],
  "enable_web_search": false
}
```

**Response Format**:
```json
{
  "reply": "AI's response to your question",
  "model": "gpt-4.1"
}
```

**Example Usage**:
```bash
curl -X POST "http://localhost:8000/advice" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {
        "role": "user", 
        "content": "Who are the best QB sleepers this week?"
      }
    ]
  }'
```

### 4. `POST /custom-advice` - Advanced Options
**What it does**: Same as /advice but with more control
**When to use**: When you want to specify different settings

**Additional Options**:
- `model`: Choose different OpenAI model
- `enable_web_search`: Let AI search the web for current stats

**Example with Web Search**:
```bash
curl -X POST "http://localhost:8000/custom-advice?enable_web_search=true" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation": [
      {
        "role": "user",
        "content": "What are Lamar Jackson's current season stats?"
      }
    ]
  }'
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key | `sk-abc123...` |
| `SYSTEM_PROMPT` | ❌ No | How the AI should behave | `You are a fantasy expert...` |
| `PORT` | ❌ No | Port to run server on | `8000` |

### OpenAI Settings (in code)

You can modify these in `app/services/openai_client.py`:

```python
def get_response(
    prompt: str,
    model: str = "gpt-4.1",              # AI model to use
    instructions: str = "You are helpful", # System instructions  
    max_tokens: int = 150,                # Length of response
    temperature: float = 0.7,             # Creativity (0-1)
    enable_web_search: bool = False       # Web search capability
):
```

### CORS Settings (Cross-Origin Resource Sharing)

The server is configured to work with web browsers:
- **Allows all origins**: Any website can connect
- **Allows all methods**: GET, POST, OPTIONS, etc.
- **Allows all headers**: No restrictions on request headers

This is set up in `app/main.py` - if you need to restrict access, modify the CORS middleware settings.

## 🏗 Development Guide

### Running in Development Mode

```bash
# Start with auto-reload (restarts when you change code)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With verbose logging
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

### Testing Your Changes

**Run the automated tests**:
```bash
# Install test requirements
pip install -r requirements-test.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app

# Run specific test file
pytest tests/test_main.py
```

**Manual testing with curl**:
```bash
# Test basic functionality
curl -X GET "http://localhost:8000/health"

# Test advice endpoint
curl -X POST "http://localhost:8000/advice" \
  -H "Content-Type: application/json" \
  -d '{"conversation":[{"role":"user","content":"Hello"}]}'
```

### Adding New Features

**To add a new API endpoint**:
1. Open `app/main.py`
2. Add your new function with `@app.get()` or `@app.post()` decorator
3. Define request/response models in `app/models.py` if needed
4. Add tests in `tests/` folder

**Example - Adding a simple endpoint**:
```python
@app.get("/status")
async def get_status():
    return {"status": "running", "version": "1.0.0"}
```

## 🚀 Deployment Guide

### Deploy to Render.com (Recommended)

**Step 1: Prepare Your Code**
1. Make sure your code is pushed to GitHub
2. Ensure `render.yaml` file exists in the backend folder
3. Test locally first to make sure everything works

**Step 2: Set Up Render**
1. Go to [render.com](https://render.com) and create account
2. Click "New" → "Web Service"  
3. Connect your GitHub repository
4. Choose the repository with your code

**Step 3: Configure the Service**
- **Name**: `genius-backend` (or whatever you prefer)
- **Environment**: `Docker`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your main branch)
- **Build Command**: Uses Dockerfile automatically
- **Start Command**: Not needed (uses Dockerfile)

**Step 4: Add Environment Variables**
1. In Render dashboard, go to your service
2. Click "Environment" tab
3. Add your variables:
   - `OPENAI_API_KEY`: Your actual OpenAI key
   - Any other variables you need

**Step 5: Deploy**
1. Click "Create Web Service"
2. Wait for deployment (takes 5-10 minutes first time)
3. Test your deployed API at the provided URL

### Deploy with Docker (Alternative)

**Build the Docker image**:
```bash
# From the backend folder
docker build -t fantasy-backend .

# Run locally to test
docker run -p 8000:8000 --env-file .env fantasy-backend
```

**Deploy to any Docker-compatible platform**:
- **DigitalOcean App Platform**
- **AWS ECS/Fargate** 
- **Google Cloud Run**
- **Azure Container Instances**

### Deploy to Traditional VPS

**On Ubuntu/Debian server**:
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# Set up your code
git clone your-repo
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_key" > .env

# Run with gunicorn (production server)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔐 Security Considerations

### API Key Security
- **Never commit your API key to Git**
- **Use environment variables only**
- **Rotate keys regularly**
- **Monitor OpenAI usage dashboard**

### CORS Configuration
Current setup allows all origins for development. For production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting
Consider adding rate limiting for production:
```python
# Add to requirements.txt
slowapi==0.1.5

# Add to main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/advice")
@limiter.limit("5/minute")  # 5 requests per minute per IP
async def get_advice(request: Request, body: AdviceRequest):
    # ... existing code
```

## 💰 Cost Management

### OpenAI Costs
**GPT-4.1 Pricing** (as of 2024):
- **Input**: ~$0.30 per 1M tokens (words/characters sent to AI)
- **Output**: ~$1.20 per 1M tokens (words/characters AI sends back)

**Typical Usage**:
- **100 questions/day**: ~$5-10/month
- **500 questions/day**: ~$15-25/month
- **1000+ questions/day**: ~$30-50/month

### Monitoring Usage
1. **OpenAI Dashboard**: Check platform.openai.com for usage
2. **Set Usage Limits**: Configure hard limits in OpenAI dashboard
3. **Add Logging**: Monitor requests in your server logs

### Cost Reduction Tips
- **Use shorter system prompts** (fewer input tokens)
- **Limit response length** (adjust max_tokens)
- **Cache common responses** (save repeated answers)
- **Add user rate limits** (prevent abuse)

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'app'"**
```bash
# Make sure you're in the backend directory
cd backend

# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**"OpenAI API key not found"**
```bash
# Check your .env file exists and has the right content
cat .env  # Should show: OPENAI_API_KEY=sk-...

# Make sure you're loading the .env file
# Add this to the top of app/main.py if needed:
from dotenv import load_dotenv
load_dotenv()
```

**"CORS errors in browser"**
- Check that CORS middleware is properly configured
- Verify the frontend is making requests to the right URL
- Look at browser developer tools (F12) → Network tab for details

**"Connection refused" or "Server not responding"**
```bash
# Check if server is actually running
ps aux | grep uvicorn

# Check what's using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Try a different port
uvicorn app.main:app --port 8001
```

**"OpenAI API errors"**
- **401 Unauthorized**: API key is wrong or missing
- **429 Rate limit**: You're making too many requests
- **402 Payment required**: No credits in your OpenAI account
- **503 Service unavailable**: OpenAI is down (check status.openai.com)

### Debugging Tips

**Enable detailed logging**:
```python
# Add to app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Test OpenAI connection separately**:
```bash
# Run the test script
cd backend
python tests/test_responses_api.py
```

**Check server health**:
```bash
# Should return server status
curl http://localhost:8000/health
```

## 📊 Monitoring & Maintenance

### Health Monitoring
- **Health endpoint**: `GET /health` returns system status
- **OpenAI usage**: Monitor token usage and costs
- **Server resources**: Check memory and CPU usage
- **Error rates**: Monitor failed requests

### Log Management
```python
# Add structured logging to app/main.py
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

### Performance Optimization
- **Response caching**: Cache common questions/answers
- **Connection pooling**: Reuse HTTP connections to OpenAI
- **Async processing**: Handle multiple requests simultaneously
- **Load balancing**: Run multiple server instances

## 🔄 Updates & Maintenance

### Updating Dependencies
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade openai

# Update all packages (be careful!)
pip install --upgrade -r requirements.txt

# Update requirements file
pip freeze > requirements.txt
```

### OpenAI Model Updates
When new models are released:
1. Update the default model in `app/services/openai_client.py`
2. Test thoroughly with the new model
3. Update documentation
4. Consider cost implications

### Backup & Recovery
- **Code**: Stored in Git repository
- **Environment variables**: Document all required variables
- **Logs**: Back up important application logs
- **Configuration**: Keep deployment configs in version control

---

## 📞 Support & Contributing

### Getting Help
1. **Check this README** for common issues
2. **Look at the logs** - they usually tell you what's wrong
3. **Test components separately** - isolate the problem
4. **Check OpenAI status**: platform.openai.com/status

### Contributing
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Make changes and test thoroughly**
4. **Update documentation as needed** 
5. **Submit pull request**

### Development Best Practices
- **Write tests** for new features
- **Use type hints** in Python code
- **Keep functions small and focused**
- **Document complex logic**
- **Test with different inputs**

---

**🚀 Ready to power your fantasy sports AI? Let's get this backend running!**