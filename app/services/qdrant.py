from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, 
    Filter, FieldCondition, MatchValue, Range
)
from loguru import logger
from app.core.config import settings


class QdrantService:
    """Service for managing vector database operations with Qdrant"""
    
    def __init__(self):
        self.client = QdrantClient(settings.qdrant_url)
        self.collection_name = settings.collection_name
        self.vector_size = settings.vector_size
        self.logger = logger.bind(service="QdrantService")
        
    async def initialize_collection(self) -> bool:
        """Create the psychology_papers collection if it doesn't exist"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                self.logger.info(f"Created collection: {self.collection_name}")
            else:
                self.logger.info(f"Collection {self.collection_name} already exists")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize collection: {e}")
            return False
    
    async def store_embeddings(
        self, 
        embeddings: List[List[float]], 
        metadata: List[Dict[str, Any]]
    ) -> bool:
        """Store embeddings with metadata in Qdrant"""
        try:
            points = []
            for i, (embedding, meta) in enumerate(zip(embeddings, metadata)):
                point = PointStruct(
                    id=i,
                    vector=embedding,
                    payload=meta
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            self.logger.info(f"Stored {len(points)} embeddings in Qdrant")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store embeddings: {e}")
            return False
    
    async def similarity_search(
        self, 
        query_embedding: List[float], 
        limit: int = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings with optional metadata filtering"""
        try:
            limit = limit or settings.chunks_per_query
            
            # Build filter if provided
            search_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        conditions.append(
                            FieldCondition(key=key, match=MatchValue(any=value))
                        )
                    elif isinstance(value, dict) and 'min' in value and 'max' in value:
                        conditions.append(
                            FieldCondition(key=key, range=Range(**value))
                        )
                    else:
                        conditions.append(
                            FieldCondition(key=key, match=MatchValue(value=value))
                        )
                search_filter = Filter(must=conditions)
            
            # Perform similarity search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=settings.similarity_threshold,
                query_filter=search_filter
            )
            
            results = []
            for result in search_result:
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })
            
            self.logger.info(f"Retrieved {len(results)} similar embeddings")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to perform similarity search: {e}")
            return []
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': info.name,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            self.logger.error(f"Failed to get collection info: {e}")
            return {}


# Global instance
qdrant_service = QdrantService()
