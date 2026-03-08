import os
import psycopg2
from PyPDF2 import PdfReader

# Ensure this matches your Docker Compose / DB setup
DATABASE_URL = "postgresql://taskuser:supersecretpassword@localhost:5432/taskmaster"
PDF_FOLDER = "/Users/khrystynka/Desktop/uni/programming 4/sources"

def extract_text_from_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
        return None

def push_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # NEW: Create the table if it doesn't exist
    print("Checking for table 'pdf_documents'...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pdf_documents (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            content_text TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    # Loop through the sources folder
    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith(".pdf"):
            file_path = os.path.join(PDF_FOLDER, filename)
            print(f"Processing: {filename}...")
            
            content = extract_text_from_pdf(file_path)
            
            if content:
                cur.execute(
                    "INSERT INTO pdf_documents (filename, content_text) VALUES (%s, %s)",
                    (filename, content)
                )
    
    conn.commit()
    cur.close()
    conn.close()
    print("Successfully pushed all PDFs to the database!")

if __name__ == "__main__":
    push_to_db()