#!/usr/bin/env python3
"""
Data ingestion script for AI Psychologist RAG System
Processes PDF papers and populates the vector database
"""
import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.services.qdrant import qdrant_service
from app.services.openai import openai_service
from app.utils.preprocessing import process_paper, clean_text, validate_chunk


async def ingest_papers(pdf_directory: str, batch_size: int = 10):
    """Ingest papers from PDF directory into vector database"""
    logger.info(f"Starting paper ingestion from {pdf_directory}")
    
    # Initialize Qdrant collection
    await qdrant_service.initialize_collection()
    
    # Get all PDF files
    pdf_dir = Path(pdf_directory)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {pdf_directory}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process papers in batches
    all_chunks = []
    
    for i, pdf_file in enumerate(pdf_files):
        logger.info(f"Processing paper {i+1}/{len(pdf_files)}: {pdf_file.name}")
        
        # Create paper metadata
        paper_metadata = {
            "paper_id": f"paper_{i+1}",
            "title": pdf_file.stem,  # Use filename as title
            "authors": ["Unknown"],  # Would need to extract from PDF
            "journal": "Unknown",
            "year": 2023,  # Would need to extract from PDF
            "doi": "",
            "therapeutic_modality": ["general"]  # Would need classification
        }
        
        # Process paper
        chunks = process_paper(str(pdf_file), paper_metadata)
        
        # Clean and validate chunks
        valid_chunks = []
        for chunk in chunks:
            chunk["text"] = clean_text(chunk["text"])
            if validate_chunk(chunk):
                valid_chunks.append(chunk)
        
        all_chunks.extend(valid_chunks)
        logger.info(f"Created {len(valid_chunks)} valid chunks from {pdf_file.name}")
        
        # Process in batches to avoid memory issues
        if len(all_chunks) >= batch_size:
            await _process_batch(all_chunks)
            all_chunks = []
    
    # Process remaining chunks
    if all_chunks:
        await _process_batch(all_chunks)
    
    logger.success(f"Paper ingestion completed! Total chunks processed: {len(all_chunks)}")


async def _process_batch(chunks: List[Dict[str, Any]]):
    """Process a batch of chunks: generate embeddings and store in Qdrant"""
    try:
        # Extract text for embedding generation
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = await openai_service.generate_embeddings(texts)
        
        if not embeddings or len(embeddings) != len(chunks):
            logger.error(f"Embedding generation failed: expected {len(chunks)}, got {len(embeddings) if embeddings else 0}")
            return
        
        # Prepare metadata for storage
        metadata_list = []
        for chunk in chunks:
            metadata = {
                "paper_id": chunk["paper_id"],
                "title": chunk["title"],
                "authors": chunk["authors"],
                "section_type": chunk["section_type"],
                "therapeutic_modality": chunk["therapeutic_modality"],
                "journal": chunk["journal"],
                "year": chunk["year"],
                "doi": chunk["doi"],
                "text": chunk["text"],
                "chunk_index": chunk["chunk_index"]
            }
            metadata_list.append(metadata)
        
        # Store in Qdrant
        success = await qdrant_service.store_embeddings(embeddings, metadata_list)
        
        if success:
            logger.info(f"Successfully stored {len(chunks)} chunks in Qdrant")
        else:
            logger.error("Failed to store chunks in Qdrant")
            
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")


async def test_ingestion():
    """Test the ingestion pipeline with sample data"""
    logger.info("Testing ingestion pipeline...")
    
    # Create sample data
    sample_papers = [
        {
            "paper_id": "test_1",
            "title": "Cognitive Behavioral Therapy for Anxiety",
            "authors": ["Dr. Smith", "Dr. Johnson"],
            "section_type": "abstract",
            "therapeutic_modality": ["CBT"],
            "journal": "Journal of Psychology",
            "year": 2023,
            "doi": "10.1234/test.2023.001",
            "text": "This study examines the effectiveness of Cognitive Behavioral Therapy (CBT) in treating anxiety disorders. Results show significant improvement in symptoms after 12 weeks of treatment.",
            "chunk_index": 0
        },
        {
            "paper_id": "test_2", 
            "title": "Mindfulness-Based Stress Reduction",
            "authors": ["Dr. Brown"],
            "section_type": "discussion",
            "therapeutic_modality": ["mindfulness"],
            "journal": "Clinical Psychology Review",
            "year": 2023,
            "doi": "10.1234/test.2023.002",
            "text": "Mindfulness-based interventions have shown promising results in reducing stress and improving emotional regulation. The practice of present-moment awareness helps individuals develop better coping mechanisms.",
            "chunk_index": 0
        }
    ]
    
    # Generate embeddings for sample data
    texts = [paper["text"] for paper in sample_papers]
    embeddings = await openai_service.generate_embeddings(texts)
    
    if embeddings:
        # Store in Qdrant
        success = await qdrant_service.store_embeddings(embeddings, sample_papers)
        if success:
            logger.success("Test ingestion completed successfully!")
            
            # Test search
            test_embedding = await openai_service.generate_embeddings(["anxiety treatment"])
            if test_embedding:
                results = await qdrant_service.similarity_search(test_embedding[0], limit=2)
                logger.info(f"Test search returned {len(results)} results")
        else:
            logger.error("Test ingestion failed")
    else:
        logger.error("Failed to generate test embeddings")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest psychology papers into vector database")
    parser.add_argument("--pdf-dir", default="./papers", help="Directory containing PDF files")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")
    parser.add_argument("--test", action="store_true", help="Run test ingestion")
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_ingestion())
    else:
        asyncio.run(ingest_papers(args.pdf_dir, args.batch_size))
