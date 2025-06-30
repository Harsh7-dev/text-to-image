#!/usr/bin/env python3
"""
Test script to verify langtrace is working correctly
"""

import os
from langtrace_python_sdk import langtrace, inject_additional_attributes

# Set the API key
os.environ["LANGTRACE_API_KEY"] = "f757aeaa9dcb99f3419da8233c4485f9a5140841b23f22fa04bf2b683e3a827f"

# Initialize langtrace
langtrace.init(api_key=os.environ["LANGTRACE_API_KEY"])

def test_function():
    print("Test function executed")
    return "success"

# Test the inject_additional_attributes function
print("Testing langtrace...")
result = inject_additional_attributes(
    test_function,
    {"langtrace.span.name": "test-script", "test": True}
)
print(f"Result: {result}")

# Test with async function
import asyncio

async def async_test_function():
    print("Async test function executed")
    return "async_success"

async def main():
    print("Testing async langtrace...")
    result = await inject_additional_attributes(
        async_test_function,
        {"langtrace.span.name": "async-test-script", "test": True}
    )
    print(f"Async result: {result}")

if __name__ == "__main__":
    asyncio.run(main()) 