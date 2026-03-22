# """
# ingest.py
# Robust ingestion of a very large set of PDFs into a Chroma vector store.

# Requirements:
#     pip install langchain langchain-community langchain-chroma
#     pip install sentence-transformers pypdf
# """

# import os
# import glob
# import gc
# from typing import List

# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
# from pypdf import PdfReader
# from langchain.schema import Document


# # ---------------------- CONFIG ----------------------
# PDF_DIR        = "pdfs"            # Folder containing PDFs
# CHROMA_DIR     = "chroma_db_pdf"  # Vector DB location
# EMBED_MODEL    = "sentence-transformers/all-MiniLM-L6-v2"

# BATCH_FILE_CT  = 50      # PDFs per batch
# CHUNK_SIZE     = 1200    # characters per chunk
# CHUNK_OVERLAP  = 150     # overlap between chunks
# MAX_CHUNK_LEN  = 4000    # absolute hard cap for a chunk
# # -----------------------------------------------------


# def find_good_pdfs(pdf_dir: str) -> List[str]:
#     """Return only valid, readable PDF paths."""
#     pdf_paths = glob.glob(os.path.join(pdf_dir, "**/*.pdf"), recursive=True)
#     good = []
#     for p in pdf_paths:
#         try:
#             PdfReader(p)  # quick validation
#             good.append(p)
#         except Exception as e:
#             print(f"⚠️  Skipping corrupt PDF: {p} ({e})")
#     return good


# def load_and_split(pdf_paths: List[str]) -> List[Document]:
#     """Load PDFs and split into clean text chunks."""
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=CHUNK_SIZE,
#         chunk_overlap=CHUNK_OVERLAP
#     )

#     documents: List[Document] = []
#     for path in pdf_paths:
#         print(f"📄 Loading {path}")
#         loader = PyPDFLoader(path)
#         for doc in loader.load():
#             text = doc.page_content.strip()
#             if not text:
#                 continue
#             # truncate extreme length
#             if len(text) > MAX_CHUNK_LEN:
#                 text = text[:MAX_CHUNK_LEN]
#             # for chunk in splitter.split_text(text):
#             #     documents.append(Document(page_content=chunk,
#             #                               metadata={"source": os.path.basename(path)}))
#             filename = os.path.basename(path)
#             for chunk in splitter.split_text(text):
#                 documents.append(Document(
#                     page_content=chunk,
#                     metadata={
#                         "source": filename,
#                         "url": f"/static/{filename}"  # ✅ or your actual hosting path
#                     }
#                 ))
#     return documents


# def build_vectorstore(all_pdf_paths: List[str]):
#     """
#     Embed documents in batches and write to Chroma incrementally.
#     Uses the new save_local() method instead of deprecated persist().
#     """
#     os.makedirs(CHROMA_DIR, exist_ok=True)

#     embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

#     # Create (or load) a persistent Chroma store
#     vs = Chroma(
#         persist_directory=CHROMA_DIR,
#         embedding_function=embeddings
#     )

#     for i in range(0, len(all_pdf_paths), BATCH_FILE_CT):
#         batch_paths = all_pdf_paths[i: i + BATCH_FILE_CT]
#         print(f"\n🚀 Processing batch {i // BATCH_FILE_CT + 1} "
#               f"({len(batch_paths)} PDFs)")

#         docs = load_and_split(batch_paths)
#         print(f"   ➡️  {len(docs)} text chunks to embed")

#         if docs:
#             vs.add_documents(docs)
#             # NEW: save_local replaces the old persist()
#             # vs.persist()
#             print("   ✅ Batch committed to Chroma")

#         # free memory between batches
#         del docs
#         gc.collect()

#     print("\n🎯 Ingestion complete.")


# if __name__ == "__main__":
#     print("🔍 Scanning PDFs…")
#     valid_pdfs = find_good_pdfs(PDF_DIR)
#     print(f"✅ {len(valid_pdfs)} valid PDFs found.")
#     if not valid_pdfs:
#         raise SystemExit("No valid PDFs to ingest.")

#     build_vectorstore(valid_pdfs)
# """
# ingest.py
# Robust ingestion of a large set of PDFs into a Chroma vector store.

# Requirements:
#     pip install langchain langchain-community langchain-chroma
#     pip install sentence-transformers pypdf
# """

# # import os
# # import glob
# # import gc
# # import warnings
# # from typing import List

# # from langchain_community.document_loaders import PyPDFLoader
# # from langchain.text_splitter import RecursiveCharacterTextSplitter
# # from langchain_chroma import Chroma
# # from langchain_huggingface import HuggingFaceEmbeddings
# # from pypdf import PdfReader
# # from langchain.schema import Document

# # # Suppress future warnings from transformers
# # warnings.filterwarnings("ignore", category=FutureWarning)

# # # ---------------------- CONFIG ----------------------
# # PDF_DIR        = "pdfs"            # Folder containing PDFs
# # CHROMA_DIR     = "chroma_db_pdfs"  # Vector DB location
# # EMBED_MODEL    = "sentence-transformers/all-MiniLM-L6-v2"

# # BATCH_FILE_CT  = 50      # PDFs per batch
# # CHUNK_SIZE     = 1200    # characters per chunk
# # CHUNK_OVERLAP  = 150     # overlap between chunks
# # MAX_CHUNK_LEN  = 4000    # absolute hard cap for a chunk
# # # -----------------------------------------------------


# # def find_good_pdfs(pdf_dir: str) -> List[str]:
# #     """Return only valid, readable PDF paths."""
# #     pdf_paths = glob.glob(os.path.join(pdf_dir, "**/*.pdf"), recursive=True)
# #     good = []
# #     for p in pdf_paths:
# #         try:
# #             PdfReader(p)  # quick validation
# #             good.append(p)
# #         except Exception as e:
# #             print(f"⚠️  Skipping corrupt PDF: {p} ({e})")
# #     return good


# # def load_and_split(pdf_paths: List[str]) -> List[Document]:
# #     """Load PDFs and split into clean text chunks."""
# #     splitter = RecursiveCharacterTextSplitter(
# #         chunk_size=CHUNK_SIZE,
# #         chunk_overlap=CHUNK_OVERLAP
# #     )

# #     documents: List[Document] = []
# #     for path in pdf_paths:
# #         print(f"📄 Loading {path}")
# #         loader = PyPDFLoader(path)
# #         for doc in loader.load():
# #             text = doc.page_content.strip()
# #             if not text:
# #                 continue
# #             if len(text) > MAX_CHUNK_LEN:
# #                 text = text[:MAX_CHUNK_LEN]
# #             for chunk in splitter.split_text(text):
# #                 if chunk.strip():  # skip empty chunks
# #                     documents.append(Document(
# #                         page_content=chunk,
# #                         metadata={"source": os.path.basename(path)}
# #                     ))
# #     return documents


# # def build_vectorstore(all_pdf_paths: List[str]):
# #     """Embed documents in batches and write to Chroma incrementally."""
# #     os.makedirs(CHROMA_DIR, exist_ok=True)

# #     embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

# #     # Create (or load) a persistent Chroma store
# #     vs = Chroma(
# #         persist_directory=CHROMA_DIR,
# #         embedding_function=embeddings
# #     )

# #     for i in range(0, len(all_pdf_paths), BATCH_FILE_CT):
# #         batch_paths = all_pdf_paths[i: i + BATCH_FILE_CT]
# #         print(f"\n🚀 Processing batch {i // BATCH_FILE_CT + 1} "
# #               f"({len(batch_paths)} PDFs)")

# #         docs = load_and_split(batch_paths)
# #         print(f"   ➡️  {len(docs)} text chunks to embed")

# #         # Sanitize chunks before embedding
# #         docs = [doc for doc in docs if isinstance(doc.page_content, str) and doc.page_content.strip()]

# #         if docs:
# #             try:
# #                 vs.add_documents(docs)
# #                 print("   ✅ Batch committed to Chroma")
# #             except Exception as e:
# #                 print(f"❌ Failed to embed batch: {e}")

# #         # Free memory between batches
# #         del docs
# #         gc.collect()

# #     print("\n🎯 Ingestion complete.")


# # if __name__ == "__main__":
# #     print("🔍 Scanning PDFs…")
# #     valid_pdfs = find_good_pdfs(PDF_DIR)
# #     print(f"✅ {len(valid_pdfs)} valid PDFs found.")
# #     if not valid_pdfs:
# #         raise SystemExit("No valid PDFs to ingest.")

# #     build_vectorstore(valid_pdfs)
# import os
# import glob
# import gc
# from typing import List

# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_community.embeddings import SentenceTransformerEmbeddings  # ✅ Correct wrapper
# from pypdf import PdfReader
# from langchain.schema import Document

# # ---------------------- CONFIG ----------------------
# PDF_DIR        = "pdfs"             # Folder containing PDFs
# CHROMA_DIR     = "chroma_db_pdf"    # Vector DB location
# EMBED_MODEL    = "all-MiniLM-L6-v2"  # ✅ No prefix needed here

# BATCH_FILE_CT  = 50                 # PDFs per batch
# CHUNK_SIZE     = 1200               # characters per chunk
# CHUNK_OVERLAP  = 150                # overlap between chunks
# MAX_CHUNK_LEN  = 4000               # absolute hard cap for a chunk
# # -----------------------------------------------------

# def find_good_pdfs(pdf_dir: str) -> List[str]:
#     """Return only valid, readable PDF paths."""
#     pdf_paths = glob.glob(os.path.join(pdf_dir, "**/*.pdf"), recursive=True)
#     good = []
#     for p in pdf_paths:
#         try:
#             PdfReader(p)  # quick validation
#             good.append(p)
#         except Exception as e:
#             print(f"⚠️  Skipping corrupt PDF: {p} ({e})")
#     return good

# def load_and_split(pdf_paths: List[str]) -> List[Document]:
#     """Load PDFs and split into clean text chunks."""
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=CHUNK_SIZE,
#         chunk_overlap=CHUNK_OVERLAP
#     )

#     documents: List[Document] = []
#     for path in pdf_paths:
#         print(f"📄 Loading {path}")
#         loader = PyPDFLoader(path)
#         for doc in loader.load():
#             text = doc.page_content.strip()
#             if not text:
#                 continue
#             if len(text) > MAX_CHUNK_LEN:
#                 text = text[:MAX_CHUNK_LEN]

#             filename = os.path.basename(path)
#             for chunk in splitter.split_text(text):
#                 if chunk.strip():
#                     documents.append(Document(
#                         page_content=chunk.strip(),
#                         metadata={
#                             "source": filename,
#                             "url": f"/static/{filename}"  # Adjust if hosted differently
#                         }
#                     ))
#     return documents

# def build_vectorstore(all_pdf_paths: List[str]):
#     """Embed documents in batches and write to Chroma incrementally."""
#     os.makedirs(CHROMA_DIR, exist_ok=True)
#     embeddings = SentenceTransformerEmbeddings(model_name=EMBED_MODEL)  # ✅ Correct wrapper

#     vs = Chroma(
#         persist_directory=CHROMA_DIR,
#         embedding_function=embeddings
#     )

#     for i in range(0, len(all_pdf_paths), BATCH_FILE_CT):
#         batch_paths = all_pdf_paths[i: i + BATCH_FILE_CT]
#         print(f"\n🚀 Processing batch {i // BATCH_FILE_CT + 1} ({len(batch_paths)} PDFs)")

#         docs = load_and_split(batch_paths)
#         print(f"   ➡️  {len(docs)} text chunks to embed")

#         if docs:
#             try:
#                 vs.add_documents(docs)
#                 print("   ✅ Batch committed to Chroma")
#             except Exception as e:
#                 print(f"❌ Failed to embed batch: {e}")

#         del docs
#         gc.collect()

#     print("\n🎯 Ingestion complete.")

# if __name__ == "__main__":
#     print("🔍 Scanning PDFs…")
#     valid_pdfs = find_good_pdfs(PDF_DIR)
#     print(f"✅ {len(valid_pdfs)} valid PDFs found.")
#     if not valid_pdfs:
#         raise SystemExit("No valid PDFs to ingest.")

#     build_vectorstore(valid_pdfs)
# main.py - FastAPI application for your RAG Chatbot

import os
import glob
import gc
from typing import List, Dict
from urllib.parse import urlparse
import requests # Need this to handle potential URL loading

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from pypdf import PdfReader
from langchain.schema import Document

# ---------------------- CONFIG ----------------------
PDF_DIR        = "pdfs"             # Folder containing PDFs
CHROMA_DIR     = "chroma_db_pdfss"    # Vector DB location (MUST match main.py)
EMBED_MODEL    = "sentence-transformers/all-MiniLM-L6-v2"  
PDF_LINKS_FILE = "found_pdf_links.txt" # File containing all public PDF URLs

BATCH_FILE_CT  = 50                 
CHUNK_SIZE     = 1200               
CHUNK_OVERLAP  = 150                
MAX_CHUNK_LEN  = 4000               
# -----------------------------------------------------

def create_url_map(links_file: str) -> Dict[str, str]:
    """Reads the links file and creates a mapping from filename (basename) to URL."""
    url_map = {}
    try:
        with open(links_file, 'r') as f:
            for line in f:
                url = line.strip()
                if url:
                    # Extracts the file name from the end of the URL (e.g., 'V23%20Syllabus%20Book_CSE%20&%20CST.pdf')
                    filename = os.path.basename(urlparse(url).path)
                    url_map[filename] = url
    except FileNotFoundError:
        print(f"❌ ERROR: URL map file '{links_file}' not found. URLs will be incorrect.")
    return url_map

def find_good_pdfs(pdf_dir: str) -> List[str]:
    """Return only valid, readable PDF paths."""
    pdf_paths = glob.glob(os.path.join(pdf_dir, "**/*.pdf"), recursive=True)
    good = []
    for p in pdf_paths:
        try:
            # Note: This approach assumes you have already downloaded the PDFs 
            # into the 'pdfs' folder, matching the filenames in found_pdf_links.txt.
            PdfReader(p)
            good.append(p)
        except Exception as e:
            print(f"⚠️  Skipping corrupt PDF: {p} ({e})")
    return good

def load_and_split(pdf_paths: List[str], url_map: Dict[str, str]) -> List[Document]:
    """Load PDFs, look up the correct URL, and split into clean text chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    documents: List[Document] = []
    for path in pdf_paths:
        filename = os.path.basename(path)
        
        # 💡 CRITICAL FIX: Get the actual public URL from the map
        actual_url = url_map.get(filename, f"URL NOT FOUND for {filename}")

        print(f"📄 Loading {path} (URL: {actual_url})")
        loader = PyPDFLoader(path)
        
        for doc in loader.load():
            text = doc.page_content.strip()
            if not text:
                continue
            if len(text) > MAX_CHUNK_LEN:
                text = text[:MAX_CHUNK_LEN]

            for chunk in splitter.split_text(text):
                if chunk.strip():
                    documents.append(Document(
                        page_content=chunk.strip(),
                        metadata={
                            "source": filename,
                            "url": actual_url # <-- USE THE ACTUAL URL
                        }
                    ))
    return documents

def build_vectorstore(all_pdf_paths: List[str]):
    """Embed documents in batches and write to Chroma incrementally."""
    
    # 1. Create the URL mapping
    url_map = create_url_map(PDF_LINKS_FILE)
    if not url_map:
        print("🛑 Cannot proceed. URL map is empty or missing. Check your found_pdf_links.txt.")
        return

    os.makedirs(CHROMA_DIR, exist_ok=True)
    embeddings = SentenceTransformerEmbeddings(model_name=EMBED_MODEL)

    # Note: If you want to clear the old database before running, uncomment the following:
    # try:
    #     import shutil
    #     shutil.rmtree(CHROMA_DIR)
    #     os.makedirs(CHROMA_DIR, exist_ok=True)
    # except Exception as e:
    #     print(f"Could not delete old Chroma DB: {e}. Proceeding...")
    
    vs = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    for i in range(0, len(all_pdf_paths), BATCH_FILE_CT):
        batch_paths = all_pdf_paths[i: i + BATCH_FILE_CT]
        print(f"\n🚀 Processing batch {i // BATCH_FILE_CT + 1} ({len(batch_paths)} PDFs)")

        # Pass the url_map to the loading function
        docs = load_and_split(batch_paths, url_map)
        print(f"   ➡️  {len(docs)} text chunks to embed")

        if docs:
            try:
                vs.add_documents(docs)
                print("   ✅ Batch committed to Chroma")
            except Exception as e:
                print(f"❌ Failed to embed batch: {e}")

        del docs
        gc.collect()

    print("\n🎯 Ingestion complete. **RESTART YOUR API SERVER**")

if __name__ == "__main__":
    print("🔍 Scanning PDFs…")
    # WARNING: This assumes your 'pdfs' folder contains the PDFs themselves.
    valid_pdfs = find_good_pdfs(PDF_DIR) 
    
    # For this to work, you must first download all PDFs listed in 
    # found_pdf_links.txt into the 'pdfs' folder.
    
    print(f"✅ {len(valid_pdfs)} valid PDFs found.")
    if not valid_pdfs:
        # Check if the URL map is the problem
        if not create_url_map(PDF_LINKS_FILE):
             raise SystemExit("No valid PDFs to ingest AND URL map failed. Check both 'pdfs' folder and 'found_pdf_links.txt'.")
        else:
            # If URLs exist but no PDFs are in the folder, you need to download them.
            raise SystemExit("No valid PDFs found in the 'pdfs' folder. Please download the files from your 'found_pdf_links.txt' into that folder first.")

    build_vectorstore(valid_pdfs)