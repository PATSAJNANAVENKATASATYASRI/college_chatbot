# import os
# from typing import List
# from langchain_community.document_loaders import PyPDFLoader, TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# # from langchain_community.embeddings import SentenceTransformerEmbeddings
# from langchain.schema import Document

# # --- CONFIG ---
# WEB_DIR = "web_page"
# PDF_DIR = "pdfs"
# DB_DIR = "chroma_db"  # Folder to store vector database
# BASE_URL = "https://www.srivasaviengg.ac.in"

# os.makedirs(DB_DIR, exist_ok=True)

# # --- Helper Functions ---
# def reconstruct_url_from_filename(filename, base_url=BASE_URL):
#     """Rebuild approximate URL if 'URL:' line is missing."""
#     name = filename
#     if name.endswith(".txt"):
#         name = name[:-4]

#     ext_map = {
#         "_html": ".html",
#         "_htm":  ".htm",
#         "_php":  ".php",
#         "_asp":  ".asp",
#         "_aspx": ".aspx",
#     }
#     for marker, ext in ext_map.items():
#         if name.endswith(marker):
#             name = name[:-len(marker)] + ext
#             break

#     path = name.replace("_", "/")
#     if not path.startswith("/"):
#         path = "/" + path
#     while "//" in path:
#         path = path.replace("//", "/")

#     if path.endswith("/index.html") or path.endswith("/index"):
#         path = path.rsplit("/", 1)[0] + "/"

#     return base_url.rstrip("/") + path


# def load_text_files() -> List[Document]:
#     """Load all .txt files and create LangChain Documents."""
#     docs = []
#     for filename in os.listdir(WEB_DIR):
#         if not filename.endswith(".txt"):
#             continue

#         path = os.path.join(WEB_DIR, filename)
#         try:
#             with open(path, "r", encoding="utf-8") as f:
#                 first_line = f.readline().strip()
#                 content = f.read().strip()

#             if first_line.startswith("URL: "):
#                 source_url = first_line.replace("URL: ", "")
#             else:
#                 source_url = reconstruct_url_from_filename(filename)

#             if content.strip():
#                 docs.append(Document(page_content=content, metadata={"source": source_url}))

#         except Exception as e:
#             print(f"⚠️ Error reading {filename}: {e}")

#     print(f"✅ Loaded {len(docs)} text files from {WEB_DIR}")
#     return docs


# def load_pdfs() -> List[Document]:
#     """Load and split PDF files into documents."""
#     docs = []
#     for filename in os.listdir(PDF_DIR):
#         if not filename.lower().endswith(".pdf"):
#             continue

#         try:
#             loader = PyPDFLoader(os.path.join(PDF_DIR, filename))
#             pdf_docs = loader.load()
#             docs.extend(pdf_docs)
#         except Exception as e:
#             print(f"⚠️ Error loading {filename}: {e}")

#     print(f"✅ Loaded {len(docs)} PDF pages from {PDF_DIR}")
#     return docs


# # --- MAIN ---
# def main():
#     print("📥 Loading and preparing documents...")
#     web_docs = load_text_files()
#     pdf_docs = load_pdfs()

#     all_docs = web_docs + pdf_docs
#     print(f"📚 Total documents before splitting: {len(all_docs)}")

#     splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#     split_docs = splitter.split_documents(all_docs)
#     print(f"🧩 Total chunks created: {len(split_docs)}")

#     print("🔍 Creating embeddings...")
#     # embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
#     from langchain_huggingface import HuggingFaceEmbeddings
#     embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


#     print("💾 Saving to Chroma vectorstore...")
#     vectordb = Chroma.from_documents(
#         documents=split_docs,
#         embedding=embedding_model,
#         persist_directory=DB_DIR
#     )
#     vectordb.persist()
#     print(f"\n✅ Ingestion complete. Vector database saved to: {DB_DIR}")


# if __name__ == "__main__":
#     main()
import os
import glob
import gc
from typing import List
from math import ceil

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings # Use HuggingFaceEmbeddings for consistency
from langchain.schema import Document

# ---------------------- CONFIG ----------------------
WEB_PAGES_DIR  = "web_pages"       # Folder containing .txt files
CHROMA_DIR     = "chroma_db_webss"   # CRITICAL FIX: Match the directory used in main.py
EMBED_MODEL    = "sentence-transformers/all-MiniLM-L6-v2" # Match the model used in main.py

CHUNK_SIZE     = 1000 # Keep consistent with your combined script's size
CHUNK_OVERLAP  = 100  # Keep consistent with your combined script's overlap
CHROMA_MAX_BATCH = 5000 
# -----------------------------------------------------

def find_txt_files(web_dir: str) -> List[str]:
    """Return all valid .txt file paths."""
    return glob.glob(os.path.join(web_dir, "**/*.txt"), recursive=True)

def load_and_split(txt_paths: List[str]) -> List[Document]:
    """
    Load text files, extract the actual URL from the first line (if present), 
    and split into clean text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    documents: List[Document] = []
    for path in txt_paths:
        filename = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                # Read content line by line to check for URL
                lines = f.readlines()
            
            if not lines:
                continue

            # 1. CRITICAL URL FIX: Check the first line for the URL
            first_line = lines[0].strip()
            if first_line.lower().startswith("url:"):
                actual_url = first_line.split(':', 1)[-1].strip()
                content_to_split = "".join(lines[1:]) # Use the rest of the file
            else:
                # 2. Fallback (If URL is not the first line)
                # This should be the actual URL (e.g., from your PDF ingest logic) 
                # or a clear placeholder like "URL not found in file."
                # NOTE: Reconstruct_url is removed as it's unreliable.
                actual_url = f"URL NOT FOUND - SOURCE FILE: {filename}"
                content_to_split = "".join(lines)


            text = content_to_split.strip()
            if not text:
                continue
            
            # 3. Split the content
            for chunk in splitter.split_text(text):
                if chunk.strip():
                    documents.append(Document(
                        page_content=chunk.strip(),
                        metadata={
                            "source": filename,
                            "url": actual_url  # Set the actual public URL
                        }
                    ))
        except Exception as e:
            print(f"⚠️ Skipping text file: {path} ({e})")
            
    return documents

def build_vectorstore():
    """Embed web documents in batches and write to Chroma."""
    os.makedirs(CHROMA_DIR, exist_ok=True)
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    # Load existing or create new Chroma DB
    vs = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )
    
    print("🔍 Scanning web pages…")
    txt_paths = find_txt_files(WEB_PAGES_DIR)
    
    if not txt_paths:
        raise SystemExit("No .txt files found to ingest.")

    print(f"✅ Found {len(txt_paths)} text files.")
    
    docs = load_and_split(txt_paths)
    total_docs = len(docs)
    print(f"   ➡️  Loaded {total_docs} chunks from web pages")

    if total_docs > 0:
        # Batching logic for Chroma
        num_batches = ceil(total_docs / CHROMA_MAX_BATCH)
        for i in range(num_batches):
            start = i * CHROMA_MAX_BATCH
            end = min((i + 1) * CHROMA_MAX_BATCH, total_docs)
            batch = docs[start:end]
            
            print(f"   🚀 Adding sub-batch {i + 1}/{num_batches} ({len(batch)} chunks)...")
            try:
                vs.add_documents(batch)
                print(f"   ✅ Sub-batch {i + 1} committed.")
            except Exception as e:
                print(f"❌ Failed to embed sub-batch {i + 1}: {e}")
                
        del docs
        gc.collect()

    print("\n🎯 Web ingestion complete. **RESTART YOUR API SERVER**")

if __name__ == "__main__":
    build_vectorstore()