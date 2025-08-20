#!/usr/bin/env python3
"""
Simple health check test
"""
import asyncio
import httpx
from loguru import logger


async def test_health():
    """Test if the FastAPI server is running"""
    logger.info("Testing FastAPI server health...")
    
    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8000"
        
        # Test root endpoint
        try:
            response = await client.get(f"{base_url}/")
            logger.info(f"Root endpoint: {response.status_code}")
            if response.status_code == 200:
                logger.success("✓ Root endpoint working")
                logger.info(f"Response: {response.json()}")
        except Exception as e:
            logger.error(f"✗ Root endpoint failed: {e}")
        
        # Test health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            logger.info(f"Health endpoint: {response.status_code}")
            if response.status_code == 200:
                logger.success("✓ Health endpoint working")
                health_data = response.json()
                logger.info(f"Status: {health_data.get('status')}")
                logger.info(f"Services: {health_data.get('services')}")
            else:
                logger.error(f"Health endpoint returned {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"✗ Health endpoint failed: {e}")
        
        # Test chat endpoint with GET (should return 405 Method Not Allowed)
        try:
            response = await client.get(f"{base_url}/chat/")
            logger.info(f"Chat GET endpoint: {response.status_code}")
            if response.status_code == 405:
                logger.success("✓ Chat endpoint exists (correctly rejects GET)")
            else:
                logger.warning(f"Chat GET returned {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"✗ Chat endpoint test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_health())
