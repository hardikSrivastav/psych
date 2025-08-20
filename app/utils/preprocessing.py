import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
from loguru import logger


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        logger.info(f"Extracted text from {pdf_path}: {len(text)} characters")
        return text
        
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path}: {e}")
        return ""


def split_into_sections(text: str) -> List[Dict[str, str]]:
    """Split text into sections (Abstract, Introduction, Methods, Results, Discussion)"""
    sections = []
    
    # Common section headers in psychology papers
    section_patterns = [
        r'abstract|summary',
        r'introduction',
        r'method|methods|methodology',
        r'result|results',
        r'discussion|conclusion',
        r'references|bibliography'
    ]
    
    # Split text into sections based on headers
    lines = text.split('\n')
    current_section = "unknown"
    current_content = []
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check if line contains section header
        section_found = False
        for pattern in section_patterns:
            if re.search(pattern, line_lower):
                # Save previous section
                if current_content:
                    sections.append({
                        "section_type": current_section,
                        "content": "\n".join(current_content).strip()
                    })
                
                # Start new section
                current_section = pattern.replace('|', '_').replace('\\', '')
                current_content = [line]
                section_found = True
                break
        
        if not section_found:
            current_content.append(line)
    
    # Add final section
    if current_content:
        sections.append({
            "section_type": current_section,
            "content": "\n".join(current_content).strip()
        })
    
    logger.info(f"Split text into {len(sections)} sections")
    return sections


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            sentence_endings = ['.', '!', '?', '\n\n']
            for ending in sentence_endings:
                last_ending = text.rfind(ending, start, end)
                if last_ending > start + chunk_size // 2:  # Only break if it's not too early
                    end = last_ending + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    logger.info(f"Created {len(chunks)} chunks from text")
    return chunks


def process_paper(
    pdf_path: str, 
    paper_metadata: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Process a single paper: extract text, split into sections, and chunk"""
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        if not text:
            return []
        
        # Split into sections
        sections = split_into_sections(text)
        
        # Process each section
        chunks = []
        for i, section in enumerate(sections):
            section_chunks = chunk_text(section["content"])
            
            for j, chunk_text in enumerate(section_chunks):
                chunk_metadata = {
                    **paper_metadata,
                    "section_type": section["section_type"],
                    "chunk_index": j,
                    "text": chunk_text
                }
                chunks.append(chunk_metadata)
        
        logger.info(f"Processed paper {pdf_path}: {len(chunks)} chunks created")
        return chunks
        
    except Exception as e:
        logger.error(f"Failed to process paper {pdf_path}: {e}")
        return []


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    
    # Normalize quotes and dashes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('–', '-').replace('—', '-')
    
    return text.strip()


def validate_chunk(chunk: Dict[str, Any]) -> bool:
    """Validate chunk metadata and content"""
    required_fields = ["title", "text", "section_type"]
    
    for field in required_fields:
        if field not in chunk or not chunk[field]:
            return False
    
    # Check minimum text length
    if len(chunk["text"]) < 50:
        return False
    
    return True
