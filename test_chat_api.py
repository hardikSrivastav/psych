#!/usr/bin/env python3
"""
Test script for Chat API endpoint
"""
import asyncio
import sys
import httpx
import json
from loguru import logger

# Add app to path
sys.path.append('.')

from data.ingestion.ingest_papers import test_ingestion


async def test_chat_api():
    """Test the chat API endpoint directly"""
    logger.info("Testing Chat API endpoint...")
    
    # First, ensure we have test data
    await test_ingestion()
    
    # Test the API endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        base_url = "http://localhost:8000"
        
        # Test 1: First message (should create new session)
        logger.info("Test 1: First message")
        response1 = await client.post(
            f"{base_url}/chat/",
            json={
                "message": "I'm feeling anxious and stressed. What can help me?"
            }
        )
        
        if response1.status_code == 200:
            data1 = response1.json()
            session_id = data1["session_id"]
            logger.info(f"Created session: {session_id}")
            logger.info(f"Response: {data1['response'][:100]}...")
            logger.info(f"Metadata: {data1['metadata']}")
        else:
            logger.error(f"API call failed: {response1.status_code} - {response1.text}")
            return
        
        # Test 2: Follow-up message (should use existing session)
        logger.info("Test 2: Follow-up message")
        response2 = await client.post(
            f"{base_url}/chat/",
            json={
                "message": "Can you tell me more about breathing exercises?",
                "session_id": session_id
            }
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            logger.info(f"Follow-up response: {data2['response'][:100]}...")
            logger.info(f"Follow-up metadata: {data2['metadata']}")
        else:
            logger.error(f"Follow-up API call failed: {response2.status_code} - {response2.text}")
        
        # Test 3: Check session info
        logger.info("Test 3: Session info")
        response3 = await client.get(f"{base_url}/chat/session/{session_id}")
        
        if response3.status_code == 200:
            session_info = response3.json()
            logger.info(f"Session info: {session_info}")
        else:
            logger.error(f"Session info failed: {response3.status_code} - {response3.text}")
        
        # Test 4: Health check
        logger.info("Test 4: Health check")
        response4 = await client.get(f"{base_url}/health")
        
        if response4.status_code == 200:
            health_data = response4.json()
            logger.info(f"Health status: {health_data['status']}")
            logger.info(f"Services: {health_data['services']}")
        else:
            logger.error(f"Health check failed: {response4.status_code} - {response4.text}")


async def test_vector_search_direct():
    """Test vector search directly through the API"""
    logger.info("Testing vector search through API...")
    
    # First, ensure we have test data
    await test_ingestion()
    
    # Test queries that should match our test data
    test_queries = [
        "CBT for anxiety",
        "mindfulness stress reduction",
        "cognitive behavioral therapy",
        "breathing exercises"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        base_url = "http://localhost:8000"
        
        for query in test_queries:
            logger.info(f"Testing query: {query}")
            
            response = await client.post(
                f"{base_url}/chat/",
                json={"message": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                chunks_retrieved = data["metadata"]["chunks_retrieved"]
                logger.info(f"Retrieved {chunks_retrieved} chunks for '{query}'")
                
                if chunks_retrieved > 0:
                    logger.success(f"✓ Found relevant content for: {query}")
                else:
                    logger.warning(f"⚠ No relevant content found for: {query}")
            else:
                logger.error(f"API call failed for '{query}': {response.status_code}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Chat API")
    parser.add_argument("--chat", action="store_true", help="Test chat API")
    parser.add_argument("--search", action="store_true", help="Test vector search")
    
    args = parser.parse_args()
    
    if args.chat:
        asyncio.run(test_chat_api())
    elif args.search:
        asyncio.run(test_vector_search_direct())
    else:
        # Run both tests
        asyncio.run(test_chat_api())
        asyncio.run(test_vector_search_direct())
