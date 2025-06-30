/**
 * MCP Client for Text-to-Image Generator
 * ======================================
 * 
 * This is a JavaScript client for interacting with the MCP server.
 * Use this to integrate image generation into your Node.js applications.
 */

class MCPClient {
    /**
     * Initialize the MCP client.
     * 
     * @param {string} baseUrl - Base URL of the MCP server
     */
    constructor(baseUrl = 'http://localhost:3123') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }

    /**
     * Get available MCP tools.
     * 
     * @returns {Promise<Object>} Dictionary containing available tools
     */
    async listTools() {
        const response = await fetch(`${this.baseUrl}/mcp/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ method: 'tools/list' })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    }

    /**
     * Generate an image using MCP.
     * 
     * @param {string} prompt - Text description of the image to generate
     * @returns {Promise<Object>} Dictionary containing the generation result
     */
    async generateImage(prompt) {
        const response = await fetch(`${this.baseUrl}/mcp/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: 'tools/call',
                params: {
                    name: 'generate-image',
                    arguments: { prompt }
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    }

    /**
     * Get image status using MCP.
     * 
     * @param {string} imageId - ID of the generated image
     * @returns {Promise<Object>} Dictionary containing the image status
     */
    async getImageStatus(imageId) {
        const response = await fetch(`${this.baseUrl}/mcp/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: 'tools/call',
                params: {
                    name: 'get-image-status',
                    arguments: { imageId }
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    }

    /**
     * Extract image ID from generation result.
     * 
     * @param {Object} result - Result from generateImage method
     * @returns {string|null} Image ID if found, null otherwise
     */
    extractImageId(result) {
        const content = result.content?.[0]?.text || '';
        if (content.includes('Image ID:')) {
            return content.split('Image ID: ')[1].split('.')[0];
        }
        return null;
    }

    /**
     * Extract image URL from generation result.
     * 
     * @param {Object} result - Result from generateImage method
     * @returns {string|null} Image URL if found, null otherwise
     */
    extractImageUrl(result) {
        const content = result.content?.[0]?.text || '';
        if (content.includes('Image URL:')) {
            return content.split('Image URL: ')[1];
        }
        return null;
    }

    /**
     * Set up Server-Sent Events listener.
     * 
     * @param {Function} onMessage - Callback for message events
     * @param {Function} onError - Callback for error events
     * @returns {EventSource} The EventSource instance
     */
    setupSSE(onMessage, onError) {
        const eventSource = new EventSource(`${this.baseUrl}/mcp/sse`);
        
        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Error parsing SSE data:', error);
            }
        };
        
        eventSource.onerror = function(error) {
            onError(error);
        };
        
        return eventSource;
    }
}

/**
 * Example workflow demonstrating MCP usage.
 */
async function mcpWorkflowExample() {
    console.log('🚀 MCP Client Workflow Example');
    console.log('='.repeat(40));
    
    const mcp = new MCPClient();
    
    try {
        // Step 1: List available tools
        console.log('📋 Listing available tools...');
        const tools = await mcp.listTools();
        console.log(`✅ Found ${tools.tools?.length || 0} tools`);
        
        // Step 2: Generate an image
        const prompt = 'a magical forest with glowing mushrooms and fairy lights';
        console.log(`🎨 Generating image: '${prompt}'`);
        
        const result = await mcp.generateImage(prompt);
        console.log('✅ Image generation initiated');
        
        // Step 3: Extract image ID and URL
        const imageId = mcp.extractImageId(result);
        const imageUrl = mcp.extractImageUrl(result);
        
        if (imageId) {
            console.log(`🆔 Image ID: ${imageId}`);
            console.log(`🔗 Image URL: ${imageUrl}`);
            
            // Step 4: Check status
            console.log('⏳ Checking image status...');
            const statusResult = await mcp.getImageStatus(imageId);
            console.log('📊 Status:', statusResult);
            
        } else {
            console.log('❌ Could not extract image ID from result');
            console.log('Result:', result);
        }
    
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

/**
 * Example of generating multiple images.
 */
async function batchGenerateExample() {
    console.log('\n🔄 Batch Generation Example');
    console.log('='.repeat(40));
    
    const mcp = new MCPClient();
    const prompts = [
        'a serene mountain lake at sunset',
        'a futuristic city with flying cars',
        'a cozy coffee shop interior'
    ];
    
    const results = [];
    
    for (let i = 0; i < prompts.length; i++) {
        const prompt = prompts[i];
        console.log(`\n🎨 Generating image ${i + 1}/${prompts.length}: '${prompt}'`);
        
        try {
            const result = await mcp.generateImage(prompt);
            const imageId = mcp.extractImageId(result);
            const imageUrl = mcp.extractImageUrl(result);
            
            results.push({
                prompt,
                imageId,
                imageUrl,
                result
            });
            
            console.log(`✅ Generated: ${imageId}`);
            console.log(`🔗 URL: ${imageUrl}`);
            
            // Small delay between requests
            await new Promise(resolve => setTimeout(resolve, 1000));
            
        } catch (error) {
            console.error(`❌ Failed to generate image ${i + 1}:`, error.message);
        }
    }
    
    console.log(`\n📊 Batch complete: ${results.length}/${prompts.length} images generated`);
    return results;
}

/**
 * Example of using Server-Sent Events.
 */
function sseExample() {
    console.log('\n📡 Server-Sent Events Example');
    console.log('='.repeat(40));
    
    const mcp = new MCPClient();
    
    const eventSource = mcp.setupSSE(
        (data) => {
            console.log('📨 SSE Message:', data);
        },
        (error) => {
            console.error('❌ SSE Error:', error);
        }
    );
    
    console.log('✅ SSE connection established');
    console.log('Press Ctrl+C to stop listening...');
    
    // Keep the connection alive for demonstration
    setTimeout(() => {
        eventSource.close();
        console.log('🔌 SSE connection closed');
    }, 30000); // Close after 30 seconds
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MCPClient, mcpWorkflowExample, batchGenerateExample, sseExample };
}

// Run examples if this file is executed directly
if (typeof window === 'undefined') {
    // Node.js environment
    (async () => {
        await mcpWorkflowExample();
        await batchGenerateExample();
        sseExample();
    })();
} 