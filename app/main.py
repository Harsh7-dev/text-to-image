import os
import time
import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import traceback

# Must precede any llm module imports
from langtrace_python_sdk import langtrace
from opentelemetry.trace import get_tracer

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import replicate
import logging
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize LangTrace
langtrace_available = False
try:
    langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))
    langtrace_available = True
    logger.info("LangTrace initialized successfully")
except Exception as e:
    logger.warning(f"LangTrace initialization failed: {e}")

# Get the tracer for creating spans
tracer = get_tracer(__name__)

app = FastAPI(title="Text-to-Image API (Replicate)", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class Prompt(BaseModel):
    text: str

@app.get("/")
@app.head("/")
async def read_root():
    """Serve the main frontend page"""
    return FileResponse("static/index.html")

@app.get("/health")
@app.head("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/info")
def get_info():
    return {
        "message": "Your Docker API is working perfectly!",
        "status": "ready",
        "langtrace_available": langtrace_available,
        "note": "Most Replicate models require billing. Consider using free alternatives like:",
        "free_alternatives": [
            "Hugging Face Inference API (some free models)",
            "OpenAI API (free tier available)",
            "Local models with Ollama",
            "Google Colab with free models"
        ]
    }

@app.post("/generate")
def generate_image(prompt: Prompt):
    start_time = time.time()
    request_id = f"req_{int(time.time())}"
    
    try:
        # Read token from environment variable (Railway will set this)
        replicate_token = os.getenv("REPLICATE_API_TOKEN")
        logger.info(f"[{request_id}] Replicate token available: {bool(replicate_token)}")
        
        if not replicate_token:
            raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN not found in environment variables")
        
        # Set the API token
        os.environ["REPLICATE_API_TOKEN"] = replicate_token
        
        logger.info(f"[{request_id}] Generating image for prompt: {prompt.text}")
        
        # Use OpenTelemetry tracer for model interaction
        if langtrace_available:
            with tracer.start_as_current_span("replicate_sdxl") as span:
                span.set_attribute("prompt", prompt.text)
                span.set_attribute("model", "stability-ai/sdxl")
                
                output = replicate.run(
                    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                    input={"prompt": prompt.text}
                )
                if not output or len(output) == 0:
                    span.set_attribute("success", False)
                    span.set_attribute("error", "No image generated")
                    raise HTTPException(status_code=500, detail="No image generated")
                image_url = output[0] if isinstance(output, list) else output
                span.set_attribute("success", True)
                span.set_attribute("output_url", image_url)
        else:
            # Fallback without LangTrace
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={"prompt": prompt.text}
            )
            if not output or len(output) == 0:
                raise HTTPException(status_code=500, detail="No image generated")
            image_url = output[0] if isinstance(output, list) else output
        
        # Download the image
        import requests
        response = requests.get(image_url)
        
        if response.status_code != 200:
            logger.error(f"[{request_id}] Failed to download image: {response.status_code}")
            raise HTTPException(status_code=500, detail="Failed to download image")
        
        output_path = "output/generated_image.png"
        os.makedirs("output", exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(response.content)

        duration = time.time() - start_time
        logger.info(f"[{request_id}] Image generated successfully in {duration:.2f}s")
        
        # Log trace-like information
        trace_info = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "model": "stability-ai/sdxl",
            "prompt": prompt.text,
            "success": True,
            "output_url": image_url,
            "duration": duration,
            "platform": "railway"
        }
        logger.info(f"[{request_id}] TRACE: {json.dumps(trace_info)}")
        
        return {
            "image_path": output_path, 
            "image_url": image_url,
            "message": "Image generated successfully",
            "request_id": request_id,
            "duration": duration,
            "trace_info": trace_info
        }
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[{request_id}] Unexpected error after {duration:.2f}s: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
