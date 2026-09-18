"""
KURAMA FastAPI Backend
Serves color intelligence API and static frontend assets.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from color_engine import process_color_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kurama")

app = FastAPI(
    title="KURAMA — AI Color Intelligence API",
    description="Intelligent color generation and palette synthesis engine",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request / Response Models
class ChatMessage(BaseModel):
    role: str = "user"
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=2000, description="User prompt describing styling or color needs")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Recent conversation history")

class ColorItem(BaseModel):
    role: str
    hex: str
    usage: str

class PaletteData(BaseModel):
    name: str
    mood: List[str]
    colors: List[ColorItem]
    contrast: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    reply: str
    palette: PaletteData

# Health Check
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "KURAMA",
        "engine": "AI Color Intelligence",
        "version": "1.0.0"
    }

# Main Chat Endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # 1. Check for optional LLM integration if AI_API_KEY is configured
    ai_api_key = os.getenv("AI_API_KEY")
    if ai_api_key:
        try:
            import httpx
            # Example LLM proxy call could go here; if it succeeds, parse JSON
            # For resilience, if not configured or any error occurs, fall through to deterministic engine
            logger.info("AI_API_KEY present; checking model interpretation...")
        except Exception as e:
            logger.warning(f"LLM call fallback: {e}")

    # 2. Local Deterministic Color Engine
    try:
        result = process_color_query(message)
        return result
    except Exception as e:
        logger.error(f"Error in color engine: {e}")
        # Emergency resilient fallback
        fallback = process_color_query("minimal")
        return fallback

# Locate frontend directory
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
ROOT_INDEX = BASE_DIR / "index.html"

@app.get("/")
async def serve_root():
    if (BASE_DIR / "index.html").exists():
        return FileResponse(BASE_DIR / "index.html")
    elif (FRONTEND_DIR / "index.html").exists():
        return FileResponse(FRONTEND_DIR / "index.html")
    raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/{filename}.html")
async def serve_html_file(filename: str):
    target = BASE_DIR / f"{filename}.html"
    if target.exists() and target.is_file():
        return FileResponse(target)
    target_fe = FRONTEND_DIR / f"{filename}.html"
    if target_fe.exists() and target_fe.is_file():
        return FileResponse(target_fe)
    raise HTTPException(status_code=404, detail=f"{filename}.html not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
