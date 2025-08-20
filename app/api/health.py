from datetime import datetime
from fastapi import APIRouter, HTTPException
from loguru import logger
from app.models.chat import HealthResponse, MetricsResponse
from app.services.qdrant import qdrant_service
from app.services.redis import redis_service
from app.services.openai import openai_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with service connectivity tests"""
    logger.info("Health check requested")
    
    # Check individual services
    services_status = {}
    
    # Check Qdrant
    try:
        qdrant_healthy = await qdrant_service.initialize_collection()
        services_status["qdrant"] = "healthy" if qdrant_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        services_status["qdrant"] = "unhealthy"
    
    # Check Redis
    try:
        redis_healthy = await redis_service.health_check()
        services_status["redis"] = "healthy" if redis_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        services_status["redis"] = "unhealthy"
    
    # Check OpenAI
    try:
        openai_healthy = await openai_service.health_check()
        services_status["openai"] = "healthy" if openai_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        services_status["openai"] = "unhealthy"
    
    # Determine overall status
    overall_status = "healthy" if all(status == "healthy" for status in services_status.values()) else "unhealthy"
    
    response = HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services_status
    )
    
    logger.info(f"Health check completed: {overall_status}")
    return response


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Basic performance metrics endpoint"""
    logger.info("Metrics requested")
    
    try:
        # Get vector database info
        vector_info = await qdrant_service.get_collection_info()
        
        # For MVP, we'll return basic metrics
        # In production, you'd want to track these over time
        response = MetricsResponse(
            total_sessions=0,  # Would need to implement session counting
            total_messages=0,  # Would need to implement message counting
            average_response_time_ms=0.0,  # Would need to implement timing tracking
            vector_database_info=vector_info
        )
        
        logger.info("Metrics retrieved successfully")
        return response
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")
