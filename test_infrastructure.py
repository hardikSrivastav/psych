#!/usr/bin/env python3
"""
Simple infrastructure test script for AI Psychologist RAG System
"""
import asyncio
import sys
from loguru import logger

# Add app to path
sys.path.append('.')

from app.services.qdrant import qdrant_service
from app.services.redis import redis_service
from app.services.openai import openai_service


async def test_services():
    """Test all services connectivity"""
    logger.info("Starting infrastructure tests...")
    
    # Test Qdrant
    logger.info("Testing Qdrant service...")
    try:
        qdrant_ok = await qdrant_service.initialize_collection()
        if qdrant_ok:
            logger.success("✓ Qdrant service: OK")
        else:
            logger.error("✗ Qdrant service: FAILED")
            return False
    except Exception as e:
        logger.error(f"✗ Qdrant service: ERROR - {e}")
        return False
    
    # Test Redis
    logger.info("Testing Redis service...")
    try:
        redis_ok = await redis_service.health_check()
        if redis_ok:
            logger.success("✓ Redis service: OK")
        else:
            logger.error("✗ Redis service: FAILED")
            return False
    except Exception as e:
        logger.error(f"✗ Redis service: ERROR - {e}")
        return False
    
    # Test OpenAI
    logger.info("Testing OpenAI service...")
    try:
        openai_ok = await openai_service.health_check()
        if openai_ok:
            logger.success("✓ OpenAI service: OK")
        else:
            logger.error("✗ OpenAI service: FAILED")
            return False
    except Exception as e:
        logger.error(f"✗ OpenAI service: ERROR - {e}")
        return False
    
    logger.success("All services are working correctly!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_services())
    sys.exit(0 if success else 1)
