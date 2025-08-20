import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
from loguru import logger
from app.core.config import settings


class RedisService:
    """Service for managing session storage and conversation caching with Redis"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.session_ttl = settings.session_ttl_hours * 3600  # Convert to seconds
        self.max_conversation_length = settings.max_conversation_length
        self.logger = logger.bind(service="RedisService")
    
    async def create_session(self) -> str:
        """Create a new session and return session ID"""
        try:
            session_id = str(uuid.uuid4())
            await self.redis_client.setex(
                f"chat:{session_id}",
                self.session_ttl,
                json.dumps([])
            )
            self.logger.info(f"Created new session: {session_id}")
            return session_id
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve session data and conversation history"""
        try:
            data = await self.redis_client.get(f"chat:{session_id}")
            if data:
                messages = json.loads(data)
                self.logger.info(f"Retrieved session {session_id} with {len(messages)} messages")
                return messages
            else:
                self.logger.warning(f"Session {session_id} not found or expired")
                return None
        except Exception as e:
            self.logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    async def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a message to the session and maintain conversation limit"""
        try:
            messages = await self.get_session(session_id)
            if messages is None:
                return False
            
            # Create message object
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add message and maintain FIFO limit
            messages.append(message)
            if len(messages) > self.max_conversation_length:
                messages = messages[-self.max_conversation_length:]
            
            # Update session with new message list
            await self.redis_client.setex(
                f"chat:{session_id}",
                self.session_ttl,
                json.dumps(messages)
            )
            
            self.logger.info(f"Added message to session {session_id}, total: {len(messages)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add message to session {session_id}: {e}")
            return False
    
    async def update_session_ttl(self, session_id: str) -> bool:
        """Extend session TTL on activity"""
        try:
            messages = await self.get_session(session_id)
            if messages is not None:
                await self.redis_client.setex(
                    f"chat:{session_id}",
                    self.session_ttl,
                    json.dumps(messages)
                )
                self.logger.info(f"Extended TTL for session {session_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to update TTL for session {session_id}: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            result = await self.redis_client.delete(f"chat:{session_id}")
            if result:
                self.logger.info(f"Deleted session {session_id}")
            return bool(result)
        except Exception as e:
            self.logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information including TTL and message count"""
        try:
            ttl = await self.redis_client.ttl(f"chat:{session_id}")
            if ttl > 0:
                messages = await self.get_session(session_id)
                if messages:
                    return {
                        "session_id": session_id,
                        "ttl_seconds": ttl,
                        "message_count": len(messages),
                        "last_activity": messages[-1]["timestamp"] if messages else None
                    }
            return None
        except Exception as e:
            self.logger.error(f"Failed to get session info for {session_id}: {e}")
            return None
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (Redis handles this automatically with TTL)"""
        try:
            # This is mostly for logging purposes since Redis handles TTL automatically
            self.logger.info("Session cleanup completed (handled by Redis TTL)")
            return 0
        except Exception as e:
            self.logger.error(f"Failed to cleanup sessions: {e}")
            return 0
    
    async def health_check(self) -> bool:
        """Check Redis connection health"""
        try:
            await self.redis_client.ping()
            self.logger.info("Redis health check passed")
            return True
        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            return False


# Global instance
redis_service = RedisService()
