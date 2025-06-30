from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import replicate
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.post("/generate")
def generate_image(prompt: Prompt):
    try:
        # Read token from environment variable (Railway will set this)
        replicate_token = os.getenv("REPLICATE_API_TOKEN")
        logger.info(f"Replicate token available: {bool(replicate_token)}")
        
        if not replicate_token:
            raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN not found in environment variables")
        
        # Set the API token
        os.environ["REPLICATE_API_TOKEN"] = replicate_token
        
        logger.info(f"Generating image for prompt: {prompt.text}")
        
        # Use a free text-to-image model
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={"prompt": prompt.text}
        )
        
        logger.info(f"Replicate output: {output}")
        
        if not output or len(output) == 0:
            raise HTTPException(status_code=500, detail="No image generated")
        
        # The output is a list of image URLs
        image_url = output[0] if isinstance(output, list) else output
        
        # Download the image
        import requests
        response = requests.get(image_url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to download image")
        
        output_path = "output/generated_image.png"
        os.makedirs("output", exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.info(f"Image saved to {output_path}")
        return {
            "image_path": output_path, 
            "image_url": image_url,
            "message": "Image generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/info")
def get_info():
    return {
        "message": "Your Docker API is working perfectly!",
        "status": "ready",
        "note": "Most Replicate models require billing. Consider using free alternatives like:",
        "free_alternatives": [
            "Hugging Face Inference API (some free models)",
            "OpenAI API (free tier available)",
            "Local models with Ollama",
            "Google Colab with free models"
        ]
    }
