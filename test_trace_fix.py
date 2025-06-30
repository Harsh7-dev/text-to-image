#!/usr/bin/env python3
"""
Test script to verify the new tracing implementation
"""

import os
import asyncio
from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import baggage, context, LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY

# Set the API key
os.environ["LANGTRACE_API_KEY"] = "f757aeaa9dcb99f3419da8233c4485f9a5140841b23f22fa04bf2b683e3a827f"

# Initialize langtrace
langtrace.init(api_key=os.environ["LANGTRACE_API_KEY"])

async def test_async_function():
    print("Async test function executed")
    await asyncio.sleep(0.1)  # Simulate some async work
    return "async_success"

async def trace_operation_test(operation_name, operation_func, attributes=None):
    """Test version of our trace_operation function"""
    print(f"Tracing operation: {operation_name}")
    
    trace_attributes = {"langtrace.span.name": operation_name}
    if attributes:
        trace_attributes.update(attributes)
    
    # Set the baggage context
    new_ctx = baggage.set_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY, trace_attributes)
    token = context.attach(new_ctx)
    
    try:
        # Execute the operation
        result = await operation_func()
        print(f"Tracing completed successfully: {operation_name}")
        return result
    finally:
        # Clean up the context
        context.detach(token)

async def main():
    print("Testing new tracing implementation...")
    
    # Test the new tracing approach
    result = await trace_operation_test(
        "test-async-trace", 
        test_async_function, 
        {"test": True, "prompt": "test prompt"}
    )
    
    print(f"Result: {result}")
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 