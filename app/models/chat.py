from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User input text", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="AI psychologist response")
    session_id: str = Field(..., description="Session ID for conversation continuity")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Response metadata including chunks retrieved, response time, tokens used"
    )


class Message(BaseModel):
    """Message model for conversation history"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Message metadata")


class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str = Field(..., description="Session ID")
    ttl_seconds: int = Field(..., description="Time to live in seconds")
    message_count: int = Field(..., description="Number of messages in session")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    services: Dict[str, str] = Field(..., description="Individual service statuses")


class MetricsResponse(BaseModel):
    """Metrics response model"""
    total_sessions: int = Field(..., description="Total active sessions")
    total_messages: int = Field(..., description="Total messages processed")
    average_response_time_ms: float = Field(..., description="Average response time in milliseconds")
    vector_database_info: Dict[str, Any] = Field(..., description="Vector database statistics")
