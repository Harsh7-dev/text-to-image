#!/usr/bin/env python3
"""
MCP Server Test Script
======================

This script tests the MCP server functionality to ensure everything is working correctly.
"""

import requests
import json
import sys
import time

def test_health_endpoint(base_url):
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_mcp_list_tools(base_url):
    """Test MCP tools/list endpoint."""
    print("📋 Testing MCP tools/list...")
    try:
        response = requests.post(
            f"{base_url}/mcp/messages",
            json={"method": "tools/list"}
        )
        if response.status_code == 200:
            data = response.json()
            tools = data.get('tools', [])
            print(f"✅ Found {len(tools)} MCP tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
            return True
        else:
            print(f"❌ MCP tools/list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP tools/list error: {e}")
        return False

def test_mcp_generate_image(base_url):
    """Test MCP generate-image tool."""
    print("🎨 Testing MCP generate-image...")
    try:
        response = requests.post(
            f"{base_url}/mcp/messages",
            json={
                "method": "tools/call",
                "params": {
                    "name": "generate-image",
                    "arguments": {"prompt": "a simple red circle on white background"}
                }
            }
        )
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', [{}])[0].get('text', '')
            if 'Image ID:' in content and 'Image URL:' in content:
                print("✅ Image generation successful")
                image_id = content.split('Image ID: ')[1].split('.')[0]
                print(f"   Image ID: {image_id}")
                return image_id
            else:
                print("❌ Image generation failed - no ID/URL in response")
                print(f"   Response: {content}")
                return None
        else:
            print(f"❌ MCP generate-image failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ MCP generate-image error: {e}")
        return None

def test_mcp_get_status(base_url, image_id):
    """Test MCP get-image-status tool."""
    if not image_id:
        print("⏭️ Skipping status check - no image ID")
        return False
    
    print(f"📊 Testing MCP get-image-status for {image_id}...")
    try:
        response = requests.post(
            f"{base_url}/mcp/messages",
            json={
                "method": "tools/call",
                "params": {
                    "name": "get-image-status",
                    "arguments": {"imageId": image_id}
                }
            }
        )
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', [{}])[0].get('text', '')
            print(f"✅ Status check successful: {content}")
            return True
        else:
            print(f"❌ MCP get-image-status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP get-image-status error: {e}")
        return False

def test_mcp_sse(base_url):
    """Test MCP SSE endpoint."""
    print("📡 Testing MCP SSE endpoint...")
    try:
        response = requests.get(f"{base_url}/mcp/sse", stream=True)
        if response.status_code == 200:
            print("✅ SSE endpoint accessible")
            # Read first few lines to verify it's working
            lines = []
            for i, line in enumerate(response.iter_lines()):
                if line:
                    lines.append(line.decode('utf-8'))
                if i >= 2:  # Read first 3 lines
                    break
            print(f"   SSE data: {lines}")
            return True
        else:
            print(f"❌ MCP SSE failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP SSE error: {e}")
        return False

def test_rest_api(base_url):
    """Test REST API endpoints."""
    print("🌐 Testing REST API endpoints...")
    
    # Test generate image
    try:
        response = requests.post(
            f"{base_url}/api/generate-image",
            json={"prompt": "a blue square on white background"}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ REST API generate-image working")
            print(f"   Image ID: {data.get('imageId')}")
            return data.get('imageId')
        else:
            print(f"❌ REST API generate-image failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ REST API generate-image error: {e}")
        return None

def main():
    """Run all tests."""
    base_url = "http://localhost:3123"
    
    print("🧪 MCP Server Test Suite")
    print("=" * 50)
    
    # Check if server is running
    if not test_health_endpoint(base_url):
        print("\n❌ Server is not running or not accessible!")
        print("Please start the server first:")
        print("  python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3123")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Test MCP endpoints
    tests_passed = 0
    total_tests = 5
    
    if test_mcp_list_tools(base_url):
        tests_passed += 1
    
    image_id = test_mcp_generate_image(base_url)
    if image_id:
        tests_passed += 1
    
    if test_mcp_get_status(base_url, image_id):
        tests_passed += 1
    
    if test_mcp_sse(base_url):
        tests_passed += 1
    
    # Test REST API
    rest_image_id = test_rest_api(base_url)
    if rest_image_id:
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! MCP server is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 