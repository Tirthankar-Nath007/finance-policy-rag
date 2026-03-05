from pypdf import PdfReader
from pathlib import Path
from typing import List
import os


def extract_text_from_pdf(pdf_path: Path) -> str:
    print(f"DEBUG: Reading PDF: {pdf_path}")
    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = start + chunk_size - overlap
    
    return chunks


def get_all_pdfs_and_chunk(pdf_dir: Path, chunk_size: int = 800, overlap: int = 100) -> tuple[List[str], List[str]]:
    print(f"DEBUG: pdf_dir = {pdf_dir}")
    print(f"DEBUG: pdf_dir exists = {pdf_dir.exists()}")
    
    if not pdf_dir.exists():
        print(f"ERROR: Directory does not exist: {pdf_dir}")
        return [], []
    
    all_chunks = []
    sources = []
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"DEBUG: Found {len(pdf_files)} PDF files")
    
    for pdf_file in pdf_files:
        print(f"DEBUG: Processing {pdf_file.name}")
        text = extract_text_from_pdf(pdf_file)
        chunks = chunk_text(text, chunk_size, overlap)
        all_chunks.extend(chunks)
        sources.extend([pdf_file.name] * len(chunks))
        print(f"DEBUG: Created {len(chunks)} chunks from {pdf_file.name}")
    
    return all_chunks, sources
