#!/usr/bin/env python3
"""
Script to ingest PDFs from sources/ folder into PostgreSQL with proper page tracking.
This will replace existing documents with page-by-page entries.
"""

import os
import psycopg2
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use localhost when running from host machine
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskuser:supersecretpassword@localhost:5432/taskmaster")
if "host.docker.internal" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("host.docker.internal", "localhost")
SOURCES_DIR = "./sources"

def clear_existing_pdfs():
    """Clear existing PDF documents from the database."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Clearing existing PDF documents...")
    cur.execute("DELETE FROM pdf_documents;")
    conn.commit()
    
    cur.close()
    conn.close()
    print("Existing documents cleared.")

def extract_pdf_pages(pdf_path):
    """Extract text from PDF page by page."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            pages = []
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    pages.append((page_num, text))
            
            return pages
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return []

def ingest_pdf_with_pages():
    """Ingest PDFs with page tracking."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    pdf_files = [f for f in os.listdir(SOURCES_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {SOURCES_DIR}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to ingest...")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(SOURCES_DIR, pdf_file)
        print(f"Processing {pdf_file}...")
        
        pages = extract_pdf_pages(pdf_path)
        
        if not pages:
            print(f"No content extracted from {pdf_file}")
            continue
        
        # Insert each page as a separate row
        for page_num, content in pages:
            cur.execute("""
                INSERT INTO pdf_documents (filename, content_text, page_number)
                VALUES (%s, %s, %s)
            """, (pdf_file, content, page_num))
        
        print(f"Ingested {len(pages)} pages from {pdf_file}")
    
    conn.commit()
    cur.close()
    conn.close()
    print("Ingestion completed!")

def main():
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable not set")
        return
    
    if not os.path.exists(SOURCES_DIR):
        print(f"ERROR: Sources directory {SOURCES_DIR} not found")
        return
    
    print("Starting PDF ingestion with page tracking...")
    clear_existing_pdfs()
    ingest_pdf_with_pages()
    
    # Verify results
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM pdf_documents;")
    count = cur.fetchone()[0]
    cur.execute("SELECT filename, COUNT(*) as pages FROM pdf_documents GROUP BY filename;")
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    print(f"\nTotal documents in database: {count}")
    for filename, pages in results:
        print(f"  {filename}: {pages} pages")

if __name__ == "__main__":
    main()
