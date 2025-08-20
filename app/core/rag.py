import time
from typing import List, Dict, Any, Optional
from loguru import logger
from app.services.qdrant import qdrant_service
from app.services.redis import redis_service
from app.services.openai import openai_service
from app.core.config import settings


class RAGService:
    """Core RAG orchestration service for the AI psychologist"""
    
    def __init__(self):
        self.logger = logger.bind(service="RAGService")
    
    async def process_query(
        self, 
        user_message: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """Complete RAG pipeline: embed → search → retrieve → generate"""
        start_time = time.time()
        
        try:
            # Step 1: Get conversation history
            conversation_history = await self._get_conversation_history(session_id)
            
            # Step 2: Generate query embedding
            query_embedding = await self._generate_query_embedding(user_message)
            if not query_embedding:
                raise Exception("Failed to generate query embedding")
            
            # Step 3: Perform similarity search
            retrieved_chunks = await self._search_similar_chunks(query_embedding)
            
            # Step 4: Assemble context
            context = await self._assemble_context(retrieved_chunks, conversation_history)
            
            # Step 5: Generate response
            response_data = await self._generate_response(user_message, context, conversation_history)
            
            # Step 6: Calculate metadata
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            metadata = {
                "chunks_retrieved": len(retrieved_chunks),
                "response_time_ms": round(response_time, 2),
                "tokens_used": response_data.get("tokens_used", 0),
                "similarity_scores": [chunk.get("score", 0) for chunk in retrieved_chunks]
            }
            
            self.logger.info(f"RAG pipeline completed in {response_time:.2f}ms, retrieved {len(retrieved_chunks)} chunks")
            
            return {
                "response": response_data["content"],
                "metadata": metadata,
                "retrieved_chunks": retrieved_chunks
            }
            
        except Exception as e:
            self.logger.error(f"RAG pipeline failed: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again.",
                "metadata": {
                    "chunks_retrieved": 0,
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "tokens_used": 0,
                    "error": str(e)
                },
                "retrieved_chunks": []
            }
    
    async def _get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieve conversation history from Redis"""
        try:
            messages = await redis_service.get_session(session_id)
            if not messages:
                return []
            
            # Convert to format expected by OpenAI API
            history = []
            for msg in messages[-settings.max_conversation_length:]:  # Keep last N messages
                history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation history: {e}")
            return []
    
    async def _generate_query_embedding(self, user_message: str) -> Optional[List[float]]:
        """Generate embedding for user query"""
        try:
            embeddings = await openai_service.generate_embeddings([user_message])
            return embeddings[0] if embeddings else None
            
        except Exception as e:
            self.logger.error(f"Failed to generate query embedding: {e}")
            return None
    
    async def _search_similar_chunks(self, query_embedding: List[float]) -> List[Dict[str, Any]]:
        """Search for similar chunks in vector database"""
        try:
            results = await qdrant_service.similarity_search(
                query_embedding=query_embedding,
                limit=settings.chunks_per_query
            )
            
            self.logger.info(f"Retrieved {len(results)} similar chunks")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search similar chunks: {e}")
            return []
    
    async def _assemble_context(
        self, 
        retrieved_chunks: List[Dict[str, Any]], 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Assemble context from retrieved chunks and conversation history"""
        try:
            # Build context from retrieved chunks
            context_parts = []
            
            for chunk in retrieved_chunks:
                payload = chunk.get("payload", {})
                text = payload.get("text", "")
                title = payload.get("title", "Unknown Paper")
                section_type = payload.get("section_type", "unknown")
                
                context_parts.append(f"From '{title}' ({section_type}): {text}")
            
            # Add conversation history context
            if conversation_history:
                history_context = "\n\nRecent conversation:\n"
                for msg in conversation_history[-3:]:  # Last 3 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_context += f"{role}: {msg['content']}\n"
                context_parts.append(history_context)
            
            context = "\n\n".join(context_parts)
            
            self.logger.info(f"Assembled context with {len(retrieved_chunks)} chunks and {len(conversation_history)} history messages")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to assemble context: {e}")
            return ""
    
    async def _generate_response(
        self, 
        user_message: str, 
        context: str, 
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate AI response using context and conversation history"""
        try:
            # Prepare messages for OpenAI
            messages = []
            
            # Add conversation history
            messages.extend(conversation_history)
            
            # Add current user message with context
            contextualized_message = f"Context from psychology research:\n{context}\n\nUser: {user_message}"
            messages.append({"role": "user", "content": contextualized_message})
            
            # Get therapeutic system prompt
            system_prompt = openai_service.get_therapeutic_system_prompt()
            
            # Generate response
            response = await openai_service.generate_chat_response(
                messages=messages,
                system_prompt=system_prompt
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            return {
                "content": "I apologize, but I'm experiencing technical difficulties. Please try again.",
                "tokens_used": 0,
                "error": str(e)
            }


# Global instance
rag_service = RAGService()
