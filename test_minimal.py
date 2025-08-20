#!/usr/bin/env python3
"""
Minimal test to isolate the chat API issue
"""
import asyncio
import sys
from loguru import logger

# Add app to path
sys.path.append('.')

from app.services.redis import redis_service
from app.core.rag import rag_service


async def test_minimal():
    """Minimal test to isolate the issue"""
    logger.info("Testing minimal components...")
    
    # Test 1: Redis service
    try:
        session_id = await redis_service.create_session()
        logger.success(f"✓ Redis session created: {session_id}")
    except Exception as e:
        logger.error(f"✗ Redis session creation failed: {e}")
        return
    
    # Test 2: RAG service with minimal query
    try:
        result = await rag_service.process_query(
            user_message="Hello",
            session_id=session_id
        )
        logger.success(f"✓ RAG service working: {len(result.get('response', ''))} chars")
        logger.info(f"Metadata: {result.get('metadata', {})}")
    except Exception as e:
        logger.error(f"✗ RAG service failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: Session storage
    try:
        await redis_service.add_message(
            session_id=session_id,
            role="user",
            content="Test message",
            metadata={}
        )
        logger.success("✓ Session storage working")
    except Exception as e:
        logger.error(f"✗ Session storage failed: {e}")
        return
    
    logger.success("All minimal tests passed!")


if __name__ == "__main__":
    asyncio.run(test_minimal())
