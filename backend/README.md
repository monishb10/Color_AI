# Jerryy's AI — Backend Engine

FastAPI backend providing curriculum intelligence, reasoning, and color synthesis for **Jerryy's AI Exam Preparation Model**.

## Setup & Running

1. Create and activate a Python virtual environment:
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Launch server:
```powershell
uvicorn main:app --reload --port 8000
```

4. Access API:
- Health check: `http://localhost:8000/api/health`
- Chat endpoint: `POST http://localhost:8000/api/chat`
- Web Application: `http://localhost:8000/`
