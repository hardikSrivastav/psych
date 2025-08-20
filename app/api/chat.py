from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from app.models.chat import ChatRequest, ChatResponse
from app.services.redis import redis_service
from app.core.rag import rag_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with RAG pipeline integration"""
    logger.info(f"Chat request received: {len(request.message)} characters")
    
    try:
        # Step 1: Handle session management
        session_id = await _handle_session(request.session_id)
        
        # Step 2: Process query through RAG pipeline
        rag_result = await rag_service.process_query(
            user_message=request.message,
            session_id=session_id
        )
        
        # Step 3: Store user message in session
        await redis_service.add_message(
            session_id=session_id,
            role="user",
            content=request.message,
            metadata={"rag_metadata": rag_result.get("metadata", {})}
        )
        
        # Step 4: Store assistant response in session
        await redis_service.add_message(
            session_id=session_id,
            role="assistant",
            content=rag_result["response"],
            metadata={"rag_metadata": rag_result.get("metadata", {})}
        )
        
        # Step 5: Prepare response
        response = ChatResponse(
            response=rag_result["response"],
            session_id=session_id,
            metadata=rag_result.get("metadata", {})
        )
        
        logger.info(f"Chat response generated for session {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def _handle_session(session_id: str = None) -> str:
    """Handle session creation or validation"""
    try:
        if not session_id:
            # Create new session
            session_id = await redis_service.create_session()
            logger.info(f"Created new session: {session_id}")
        else:
            # Validate existing session
            session_info = await redis_service.get_session_info(session_id)
            if not session_info:
                # Session expired or invalid, create new one
                session_id = await redis_service.create_session()
                logger.info(f"Session expired, created new session: {session_id}")
            else:
                # Extend session TTL
                await redis_service.update_session_ttl(session_id)
                logger.info(f"Extended session TTL: {session_id}")
        
        return session_id
        
    except Exception as e:
        logger.error(f"Session handling error: {e}")
        # Create new session as fallback
        return await redis_service.create_session()


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    try:
        session_info = await redis_service.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session info error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        success = await redis_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Deleted session: {session_id}")
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
