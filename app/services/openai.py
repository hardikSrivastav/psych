import tiktoken
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from loguru import logger
from app.core.config import settings


class OpenAIService:
    """Service for OpenAI API operations including embeddings and chat completion"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.embedding_model = "text-embedding-3-large"
        self.chat_model = "gpt-4"
        self.logger = logger.bind(service="OpenAIService")
        
        # Initialize tokenizer for cost tracking
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.chat_model)
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using text-embedding-3-large model"""
        try:
            if not texts:
                return []
            
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [embedding.embedding for embedding in response.data]
            self.logger.info(f"Generated {len(embeddings)} embeddings using {self.embedding_model}")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            return []
    
    async def generate_chat_response(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate chat response with therapeutic system prompt"""
        try:
            # Prepare messages with system prompt
            chat_messages = []
            if system_prompt:
                chat_messages.append({"role": "system", "content": system_prompt})
            chat_messages.extend(messages)
            
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=chat_messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract response and metadata
            content = response.choices[0].message.content
            usage = response.usage
            
            # Calculate token counts
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            self.logger.info(f"Generated chat response: {input_tokens} input, {output_tokens} output tokens")
            
            return {
                "content": content,
                "tokens_used": total_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate chat response: {e}")
            return {
                "content": "I apologize, but I'm experiencing technical difficulties. Please try again.",
                "tokens_used": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "error": str(e)
            }
    
    def get_therapeutic_system_prompt(self) -> str:
        """Get the therapeutic system prompt for the AI psychologist"""
        return """You are an AI psychologist assistant designed to provide scientifically-grounded, empathetic responses based on psychology research. Your role is to:

THERAPEUTIC APPROACHES:
- Use evidence-based therapeutic techniques from CBT, DBT, and humanistic approaches
- Provide validation and empathy while maintaining professional boundaries
- Encourage self-reflection and insight development
- Offer practical coping strategies when appropriate

SAFETY GUIDELINES:
- Do NOT provide medical diagnosis or treatment recommendations
- Do NOT give specific medical advice
- If someone expresses suicidal thoughts, self-harm, or crisis situations, immediately provide crisis resources
- Maintain appropriate professional boundaries
- Refer to mental health professionals for serious concerns

RESPONSE STYLE:
- Be warm, empathetic, and validating
- Use "I" statements to show understanding
- Provide evidence-based information when relevant
- Encourage self-reflection and personal growth
- Keep responses conversational but professional

SCIENTIFIC GROUNDING:
- Base responses on psychological research and evidence
- Cite relevant therapeutic concepts when appropriate
- Acknowledge limitations of AI assistance
- Encourage professional help for complex issues

Remember: You are a supportive AI assistant, not a replacement for professional mental health care. Always prioritize safety and appropriate referrals when needed."""

    def count_tokens(self, text: str) -> int:
        """Count tokens in text for cost tracking"""
        try:
            return len(self.tokenizer.encode(text))
        except:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4
    
    async def health_check(self) -> bool:
        """Check OpenAI API connectivity"""
        try:
            # Simple test with a short embedding
            test_embedding = await self.generate_embeddings(["test"])
            if test_embedding:
                self.logger.info("OpenAI health check passed")
                return True
            return False
        except Exception as e:
            self.logger.error(f"OpenAI health check failed: {e}")
            return False


# Global instance
openai_service = OpenAIService()
