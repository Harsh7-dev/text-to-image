#!/usr/bin/env python3
"""
MCP Client for Text-to-Image Generator
======================================

This is a Python client for interacting with the MCP server.
Use this to integrate image generation into your Python applications.
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List

class MCPClient:
    """Client for interacting with the Text-to-Image MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:3123"):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def list_tools(self) -> Dict[str, Any]:
        """
        Get available MCP tools.
        
        Returns:
            Dictionary containing available tools
        """
        response = self.session.post(
            f"{self.base_url}/mcp/messages",
            json={"method": "tools/list"}
        )
        response.raise_for_status()
        return response.json()
    
    def generate_image(self, prompt: str) -> Dict[str, Any]:
        """
        Generate an image using MCP.
        
        Args:
            prompt: Text description of the image to generate
            
        Returns:
            Dictionary containing the generation result
        """
        response = self.session.post(
            f"{self.base_url}/mcp/messages",
            json={
                "method": "tools/call",
                "params": {
                    "name": "generate-image",
                    "arguments": {"prompt": prompt}
                }
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_image_status(self, image_id: str) -> Dict[str, Any]:
        """
        Get image status using MCP.
        
        Args:
            image_id: ID of the generated image
            
        Returns:
            Dictionary containing the image status
        """
        response = self.session.post(
            f"{self.base_url}/mcp/messages",
            json={
                "method": "tools/call",
                "params": {
                    "name": "get-image-status",
                    "arguments": {"imageId": image_id}
                }
            }
        )
        response.raise_for_status()
        return response.json()
    
    def extract_image_id(self, result: Dict[str, Any]) -> Optional[str]:
        """
        Extract image ID from generation result.
        
        Args:
            result: Result from generate_image method
            
        Returns:
            Image ID if found, None otherwise
        """
        content = result.get('content', [{}])[0].get('text', '')
        if 'Image ID:' in content:
            return content.split('Image ID: ')[1].split('.')[0]
        return None
    
    def extract_image_url(self, result: Dict[str, Any]) -> Optional[str]:
        """
        Extract image URL from generation result.
        
        Args:
            result: Result from generate_image method
            
        Returns:
            Image URL if found, None otherwise
        """
        content = result.get('content', [{}])[0].get('text', '')
        if 'Image URL:' in content:
            return content.split('Image URL: ')[1]
        return None

def mcp_workflow_example():
    """Example workflow demonstrating MCP usage."""
    print("🚀 MCP Client Workflow Example")
    print("=" * 40)
    
    # Initialize client
    mcp = MCPClient()
    
    try:
        # Step 1: List available tools
        print("📋 Listing available tools...")
        tools = mcp.list_tools()
        print(f"✅ Found {len(tools.get('tools', []))} tools")
        
        # Step 2: Generate an image
        prompt = "a magical forest with glowing mushrooms and fairy lights"
        print(f"🎨 Generating image: '{prompt}'")
        
        result = mcp.generate_image(prompt)
        print("✅ Image generation initiated")
        
        # Step 3: Extract image ID and URL
        image_id = mcp.extract_image_id(result)
        image_url = mcp.extract_image_url(result)
        
        if image_id:
            print(f"🆔 Image ID: {image_id}")
            print(f"🔗 Image URL: {image_url}")
            
            # Step 4: Check status
            print("⏳ Checking image status...")
            status_result = mcp.get_image_status(image_id)
            print("📊 Status:", status_result)
            
        else:
            print("❌ Could not extract image ID from result")
            print("Result:", result)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def batch_generate_example():
    """Example of generating multiple images."""
    print("\n🔄 Batch Generation Example")
    print("=" * 40)
    
    mcp = MCPClient()
    prompts = [
        "a serene mountain lake at sunset",
        "a futuristic city with flying cars",
        "a cozy coffee shop interior"
    ]
    
    results = []
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n🎨 Generating image {i}/{len(prompts)}: '{prompt}'")
        
        try:
            result = mcp.generate_image(prompt)
            image_id = mcp.extract_image_id(result)
            image_url = mcp.extract_image_url(result)
            
            results.append({
                'prompt': prompt,
                'image_id': image_id,
                'image_url': image_url,
                'result': result
            })
            
            print(f"✅ Generated: {image_id}")
            print(f"🔗 URL: {image_url}")
            
            # Small delay between requests
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Failed to generate image {i}: {e}")
    
    print(f"\n📊 Batch complete: {len(results)}/{len(prompts)} images generated")
    return results

if __name__ == "__main__":
    # Run the workflow example
    mcp_workflow_example()
    
    # Run the batch generation example
    batch_generate_example() 