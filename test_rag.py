#!/usr/bin/env python3
"""
Test script for RAG pipeline functionality
"""
import asyncio
import sys
from loguru import logger

# Add app to path
sys.path.append('.')

from app.services.qdrant import qdrant_service
from app.services.redis import redis_service
from app.services.openai import openai_service
from app.core.rag import rag_service
from data.ingestion.ingest_papers import test_ingestion


async def test_rag_pipeline():
    """Test the complete RAG pipeline"""
    logger.info("Testing RAG pipeline...")
    
    # Step 1: Test data ingestion
    logger.info("Step 1: Testing data ingestion...")
    await test_ingestion()
    
    # Step 2: Test session management
    logger.info("Step 2: Testing session management...")
    session_id = await redis_service.create_session()
    logger.info(f"Created session: {session_id}")
    
    # Step 3: Test RAG pipeline
    logger.info("Step 3: Testing RAG pipeline...")
    test_query = "I'm feeling anxious and stressed. What can help me?"
    
    result = await rag_service.process_query(
        user_message=test_query,
        session_id=session_id
    )
    
    logger.info(f"RAG Response: {result['response'][:200]}...")
    logger.info(f"Metadata: {result['metadata']}")
    
    # Step 4: Test conversation history
    logger.info("Step 4: Testing conversation history...")
    session_info = await redis_service.get_session_info(session_id)
    logger.info(f"Session info: {session_info}")
    
    # Step 5: Test follow-up query
    logger.info("Step 5: Testing follow-up query...")
    follow_up_query = "Can you tell me more about breathing exercises?"
    
    result2 = await rag_service.process_query(
        user_message=follow_up_query,
        session_id=session_id
    )
    
    logger.info(f"Follow-up Response: {result2['response'][:200]}...")
    logger.info(f"Follow-up Metadata: {result2['metadata']}")
    
    logger.success("RAG pipeline test completed successfully!")


async def test_vector_search():
    """Test vector search functionality"""
    logger.info("Testing vector search...")
    
    # Test queries
    test_queries = [
        "anxiety treatment",
        "stress management",
        "cognitive behavioral therapy",
        "mindfulness meditation"
    ]
    
    for query in test_queries:
        logger.info(f"Testing query: {query}")
        
        # Generate embedding
        embeddings = await openai_service.generate_embeddings([query])
        if embeddings:
            # Search
            results = await qdrant_service.similarity_search(embeddings[0], limit=3)
            logger.info(f"Found {len(results)} results for '{query}'")
            
            for i, result in enumerate(results):
                score = result.get('score', 0)
                title = result.get('payload', {}).get('title', 'Unknown')
                logger.info(f"  {i+1}. {title} (score: {score:.3f})")
        else:
            logger.error(f"Failed to generate embedding for: {query}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RAG pipeline")
    parser.add_argument("--pipeline", action="store_true", help="Test complete RAG pipeline")
    parser.add_argument("--search", action="store_true", help="Test vector search")
    
    args = parser.parse_args()
    
    if args.pipeline:
        asyncio.run(test_rag_pipeline())
    elif args.search:
        asyncio.run(test_vector_search())
    else:
        # Run both tests
        asyncio.run(test_rag_pipeline())
        asyncio.run(test_vector_search())
