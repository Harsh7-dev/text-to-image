import os
from dotenv import load_dotenv
load_dotenv()  # Must be before langtrace import/init
import logging
import contextlib
import replicate
import traceback
from langtrace_python_sdk import inject_additional_attributes

# --- Logging configuration ---
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_FILE = "server.log"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)

# --- Safe langtrace initialization ---
langtrace = None
langtrace_available = False
try:
    from langtrace_python_sdk import langtrace as _langtrace
    api_key = os.getenv("LANGTRACE_API_KEY")
    if api_key:
        _langtrace.init(api_key=api_key)
        langtrace = _langtrace
        langtrace_available = True
        logger.info("langtrace initialized successfully.")
    else:
        logger.warning("LANGTRACE_API_KEY not set. langtrace is disabled.")
except Exception as e:
    logger.error(f"Failed to initialize langtrace: {e}")
    logger.error(traceback.format_exc())
    langtrace = None
    langtrace_available = False

# --- Tracing helper function ---
async def trace_operation(operation_name, operation_func, attributes=None):
    """
    Helper function to trace operations using OpenTelemetry.
    
    Args:
        operation_name: Name of the operation being traced
        operation_func: Async function to execute
        attributes: Additional attributes to add to the trace
    
    Returns:
        Result of the operation function
    """
    if not langtrace_available:
        logger.info(f"Tracing skipped (langtrace unavailable): {operation_name}")
        return await operation_func()
    
    logger.info(f"Tracing operation: {operation_name}")
    try:
        from opentelemetry import trace
        tracer = trace.get_tracer(__name__)
        
        # Create span attributes
        span_attributes = {"operation.name": operation_name}
        if attributes:
            span_attributes.update(attributes)
        
        # Create and use span
        with tracer.start_as_current_span(operation_name, attributes=span_attributes) as span:
            logger.info(f"Started span: {operation_name}")
            result = await operation_func()
            span.set_attribute("operation.status", "success")
            logger.info(f"Completed span: {operation_name}")
            return result
            
    except Exception as e:
        logger.error(f"Tracing error for '{operation_name}': {e}")
        logger.error(traceback.format_exc())
        # Fallback to executing without tracing
        return await operation_func()

import time
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# In-memory storage for generated images and videos
generated_images = {}
generated_videos = {}

# Pydantic models
class ImageRequest(BaseModel):
    prompt: str

class ImageResponse(BaseModel):
    imageId: str
    imageUrl: str
    status: str
    message: str

class VideoRequest(BaseModel):
    prompt: str

class VideoResponse(BaseModel):
    videoId: str
    videoUrl: str
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

@app.on_event("startup")
async def startup_event():
    logger.info("Starting FastAPI server...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FastAPI server...")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code} for {request.method} {request.url}")
    return response

@app.get("/")
async def read_root():
    """Serve the main frontend page"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    logger.info("Health check requested")
    return {"status": "ok"}

@app.post("/api/generate-image", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    """Generate image from text prompt"""
    start_time = time.time()
    request_id = f"req_{int(time.time())}"
    async def logic():
        try:
            replicate_token = os.getenv("REPLICATE_API_TOKEN")
            if not replicate_token:
                raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN not found in environment variables")
            image_id = str(uuid.uuid4()).replace("-", "")[:12]
            generated_images[image_id] = {
                "id": image_id,
                "prompt": request.prompt,
                "status": "processing",
                "createdAt": datetime.now().isoformat()
            }
            logger.info(f"[{request_id}] Generating image for prompt: {request.prompt}")
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={"prompt": request.prompt}
            )
            if not output or len(output) == 0:
                generated_images[image_id]["status"] = "error"
                generated_images[image_id]["error"] = "No image generated"
                raise HTTPException(status_code=500, detail="No image generated")
            image_url = output[0] if isinstance(output, list) else output
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
    return await trace_operation("generate-image", logic, {"prompt": request.prompt})

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

# Text-to-Video Endpoint
@app.post("/api/generate-video", response_model=VideoResponse)
async def generate_video(request: VideoRequest):
    start_time = time.time()
    request_id = f"req_{int(time.time())}"
    async def logic():
        try:
            replicate_token = os.getenv("REPLICATE_API_TOKEN")
            if not replicate_token:
                raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN not found in environment variables")
            video_id = str(uuid.uuid4()).replace("-", "")[:12]
            generated_videos[video_id] = {
                "id": video_id,
                "prompt": request.prompt,
                "status": "processing",
                "createdAt": datetime.now().isoformat()
            }
            logger.info(f"[{request_id}] Generating video for prompt: {request.prompt}")
            output = replicate.run(
                "tencent/hunyuan-video:6c9132aee14409cd6568d030453f1ba50f5f3412b844fe67f78a9eb62d55664f",
                input={"prompt": request.prompt}
            )
            if not output or len(output) == 0:
                generated_videos[video_id]["status"] = "error"
                generated_videos[video_id]["error"] = "No video generated"
                raise HTTPException(status_code=500, detail="No video generated")
            video_url = output[0] if isinstance(output, list) else output
            generated_videos[video_id].update({
                "status": "ready",
                "videoUrl": video_url,
                "completedAt": datetime.now().isoformat()
            })
            duration = time.time() - start_time
            logger.info(f"[{request_id}] Video generated successfully in {duration:.2f}s")
            return VideoResponse(
                videoId=video_id,
                videoUrl=video_url,
                status="ready",
                message="Video generated successfully"
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[{request_id}] Error generating video after {duration:.2f}s: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")
    return await trace_operation("generate-video", logic, {"prompt": request.prompt})

@app.get("/api/video/{video_id}/status")
async def get_video_status(video_id: str):
    if video_id not in generated_videos:
        raise HTTPException(status_code=404, detail="Video not found")
    video = generated_videos[video_id]
    return {
        "id": video["id"],
        "status": video["status"],
        "prompt": video["prompt"],
        "createdAt": video["createdAt"],
        "completedAt": video.get("completedAt"),
        "videoUrl": video.get("videoUrl")
    }

@app.get("/api/videos")
async def list_videos():
    videos = []
    for video_id, video in generated_videos.items():
        videos.append({
            "id": video["id"],
            "status": video["status"],
            "prompt": video["prompt"],
            "createdAt": video["createdAt"]
        })
    return {"videos": videos}

@app.delete("/api/video/{video_id}")
async def delete_video(video_id: str):
    if video_id not in generated_videos:
        raise HTTPException(status_code=404, detail="Video not found")
    del generated_videos[video_id]
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
                ),
                MCPTool(
                    name="generate-video",
                    description="Generate a video from a text prompt using wavespeedai/wan-2.1-i2v-480p",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The text prompt describing the video you want to generate"
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                MCPTool(
                    name="get-video-status",
                    description="Get the status of a generated video",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "videoId": {
                                "type": "string",
                                "description": "The ID of the generated video"
                            }
                        },
                        "required": ["videoId"]
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
                async def logic():
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
                
                return await trace_operation("generate-image", logic, {"prompt": prompt})
                
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
        
        elif tool_name == "generate-video":
            prompt = args.get("prompt")
            if not prompt:
                return MCPResponse(
                    content=[{"type": "text", "text": "Error: Prompt is required"}]
                )
            try:
                video_id = str(uuid.uuid4()).replace("-", "")[:12]
                generated_videos[video_id] = {
                    "id": video_id,
                    "prompt": prompt,
                    "status": "processing",
                    "createdAt": datetime.now().isoformat()
                }
                async def logic():
                    output = replicate.run(
                        "tencent/hunyuan-video:6c9132aee14409cd6568d030453f1ba50f5f3412b844fe67f78a9eb62d55664f",
                        input={"prompt": prompt}
                    )
                    if output and len(output) > 0:
                        video_url = output[0] if isinstance(output, list) else output
                        generated_videos[video_id].update({
                            "status": "ready",
                            "videoUrl": video_url,
                            "completedAt": datetime.now().isoformat()
                        })
                        return MCPResponse(
                            content=[
                                {
                                    "type": "text",
                                    "text": f"Video generated successfully! Video ID: {video_id}. Video URL: {video_url}"
                                }
                            ]
                        )
                    else:
                        generated_videos[video_id]["status"] = "error"
                        return MCPResponse(
                            content=[{"type": "text", "text": "Error: No video generated"}]
                        )
                return await trace_operation("generate-video", logic, {"prompt": prompt})
            except Exception as e:
                return MCPResponse(
                    content=[{"type": "text", "text": f"Error generating video: {str(e)}"}]
                )
        elif tool_name == "get-video-status":
            video_id = args.get("videoId")
            if not video_id:
                return MCPResponse(
                    content=[{"type": "text", "text": "Error: Video ID is required"}]
                )
            if video_id not in generated_videos:
                return MCPResponse(
                    content=[{"type": "text", "text": "Video not found"}]
                )
            video = generated_videos[video_id]
            status_text = f"Video status: {video['status']}"
            if video.get("videoUrl"):
                status_text += f". Video URL: {video['videoUrl']}"
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

# Add a test endpoint for tracing
from fastapi import APIRouter
router = APIRouter()

@router.get("/test-trace")
async def test_trace():
    logger.info("/test-trace endpoint called")
    async def logic():
        logger.info("Inside test trace span")
        return {"message": "Test trace executed"}
    return await trace_operation("test-trace-endpoint", logic, {"test": True})

app.include_router(router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3123))
    uvicorn.run(app, host="0.0.0.0", port=port) 