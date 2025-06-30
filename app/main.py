import os
import time
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import replicate
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text-to-Image API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for generated images (in production, use a database)
generated_images = {}

# Pydantic models
class ImageRequest(BaseModel):
    prompt: str

class ImageResponse(BaseModel):
    imageId: str
    imageUrl: str
    status: str
    message: str

class MCPRequest(BaseModel):
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class MCPResponse(BaseModel):
    tools: Optional[List[MCPTool]] = None
    content: Optional[List[Dict[str, Any]]] = None

@app.get("/")
async def read_root():
    """Serve the main frontend page"""
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/api/generate-image", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    """Generate image from text prompt"""
    start_time = time.time()
    request_id = f"req_{int(time.time())}"
    
    try:
        # Check for Replicate API token
        replicate_token = os.getenv("REPLICATE_API_TOKEN")
        if not replicate_token:
            raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN not found in environment variables")
        
        # Generate unique ID
        image_id = str(uuid.uuid4()).replace("-", "")[:12]
        
        # Store initial request
        generated_images[image_id] = {
            "id": image_id,
            "prompt": request.prompt,
            "status": "processing",
            "createdAt": datetime.now().isoformat()
        }
        
        logger.info(f"[{request_id}] Generating image for prompt: {request.prompt}")
        
        # Call Replicate API
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={"prompt": request.prompt}
        )
        
        if not output or len(output) == 0:
            generated_images[image_id]["status"] = "error"
            generated_images[image_id]["error"] = "No image generated"
            raise HTTPException(status_code=500, detail="No image generated")
        
        image_url = output[0] if isinstance(output, list) else output
        
        # Update status
        generated_images[image_id].update({
            "status": "ready",
            "imageUrl": image_url,
            "completedAt": datetime.now().isoformat()
        })
        
        duration = time.time() - start_time
        logger.info(f"[{request_id}] Image generated successfully in {duration:.2f}s")
        
        return ImageResponse(
            imageId=image_id,
            imageUrl=image_url,
            status="ready",
            message="Image generated successfully"
        )
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[{request_id}] Error generating image after {duration:.2f}s: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")

@app.get("/api/image/{image_id}/status")
async def get_image_status(image_id: str):
    """Get the status of a generated image"""
    if image_id not in generated_images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image = generated_images[image_id]
    return {
        "id": image["id"],
        "status": image["status"],
        "prompt": image["prompt"],
        "createdAt": image["createdAt"],
        "completedAt": image.get("completedAt"),
        "imageUrl": image.get("imageUrl")
    }

@app.get("/api/images")
async def list_images():
    """List all generated images"""
    images = []
    for image_id, image in generated_images.items():
        images.append({
            "id": image["id"],
            "status": image["status"],
            "prompt": image["prompt"],
            "createdAt": image["createdAt"]
        })
    
    return {"images": images}

@app.delete("/api/image/{image_id}")
async def delete_image(image_id: str):
    """Delete a generated image"""
    if image_id not in generated_images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    del generated_images[image_id]
    return {"success": True}

# MCP Server endpoints (following short-video-maker pattern)
@app.get("/mcp/sse")
async def mcp_sse():
    """Server-Sent Events endpoint for MCP"""
    async def event_generator():
        yield "data: {\"type\": \"connected\"}\n\n"
        
        # Keep connection alive with periodic pings
        import asyncio
        while True:
            await asyncio.sleep(30)
            yield "data: {\"type\": \"ping\"}\n\n"
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/mcp/messages")
async def mcp_messages(request: MCPRequest):
    """MCP messages endpoint"""
    if request.method == "tools/list":
        return MCPResponse(
            tools=[
                MCPTool(
                    name="generate-image",
                    description="Generate an image from a text prompt using Stable Diffusion XL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The text prompt describing the image you want to generate"
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                MCPTool(
                    name="get-image-status",
                    description="Get the status of a generated image",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "imageId": {
                                "type": "string",
                                "description": "The ID of the generated image"
                            }
                        },
                        "required": ["imageId"]
                    }
                )
            ]
        )
    
    elif request.method == "tools/call":
        tool_name = request.params.get("name")
        args = request.params.get("arguments", {})
        
        if tool_name == "generate-image":
            # Generate image using the same logic as REST API
            prompt = args.get("prompt")
            if not prompt:
                return MCPResponse(
                    content=[{"type": "text", "text": "Error: Prompt is required"}]
                )
            
            try:
                # Generate unique ID
                image_id = str(uuid.uuid4()).replace("-", "")[:12]
                
                # Store initial request
                generated_images[image_id] = {
                    "id": image_id,
                    "prompt": prompt,
                    "status": "processing",
                    "createdAt": datetime.now().isoformat()
                }
                
                # Call Replicate API
                output = replicate.run(
                    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                    input={"prompt": prompt}
                )
                
                if output and len(output) > 0:
                    image_url = output[0] if isinstance(output, list) else output
                    generated_images[image_id].update({
                        "status": "ready",
                        "imageUrl": image_url,
                        "completedAt": datetime.now().isoformat()
                    })
                    
                    return MCPResponse(
                        content=[
                            {
                                "type": "text",
                                "text": f"Image generated successfully! Image ID: {image_id}. Image URL: {image_url}"
                            }
                        ]
                    )
                else:
                    generated_images[image_id]["status"] = "error"
                    return MCPResponse(
                        content=[{"type": "text", "text": "Error: No image generated"}]
                    )
                    
            except Exception as e:
                logger.error(f"Error in MCP generate-image: {str(e)}")
                return MCPResponse(
                    content=[{"type": "text", "text": f"Error generating image: {str(e)}"}]
                )
        
        elif tool_name == "get-image-status":
            image_id = args.get("imageId")
            if not image_id:
                return MCPResponse(
                    content=[{"type": "text", "text": "Error: Image ID is required"}]
                )
            
            if image_id not in generated_images:
                return MCPResponse(
                    content=[{"type": "text", "text": "Image not found"}]
                )
            
            image = generated_images[image_id]
            status_text = f"Image status: {image['status']}"
            if image.get("imageUrl"):
                status_text += f". Image URL: {image['imageUrl']}"
            
            return MCPResponse(
                content=[{"type": "text", "text": status_text}]
            )
        
        else:
            return MCPResponse(
                content=[{"type": "text", "text": f"Unknown tool: {tool_name}"}]
            )
    
    else:
        return MCPResponse(
            content=[{"type": "text", "text": f"Unknown method: {request.method}"}]
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3123))
    uvicorn.run(app, host="0.0.0.0", port=port) 