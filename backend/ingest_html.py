# import os
# import glob
# import hashlib
# import gc
# from math import ceil
# from typing import List
# from bs4 import BeautifulSoup
# from collections import defaultdict

# from langchain.schema import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings

# # ---------------- CONFIG ---------------- #
# HTML_DIR = "html_files"
# CHROMA_DIR = "chroma_html"
# EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# CHUNK_SIZE = 1000
# CHUNK_OVERLAP = 100
# CHROMA_MAX_BATCH = 5000
# # ---------------------------------------- #

# def file_hash(path: str) -> str:
#     with open(path, "rb") as f:
#         return hashlib.md5(f.read()).hexdigest()

# def find_html_files(directory: str) -> List[str]:
#     return glob.glob(os.path.join(directory, "**", "*.html"), recursive=True)

# # def extract_faculty_items(soup: BeautifulSoup, filename: str, filehash: str) -> List[Document]:
# #     documents = []
# #     faculty_items = soup.select(".faculty-item")
# #     if not faculty_items:
# #         return []

# #     for item in faculty_items:
# #         name = item.select_one(".faculty-name")
# #         desig = item.select_one(".faculty-designation")
# #         link = item.select_one(".profile-link a")

# #         # name_text = name.get_text(strip=True) if name else "Unknown"
# #         # desig_text = desig.get_text(strip=True) if desig else "Unknown"
# #         # link_url = link["href"] if link and link.has_attr("href") else "URL Not Provided"

# #         # content = f"Name: {name_text}\nDesignation: {desig_text}\nProfile: {link_url}"
# #         # documents.append(Document(
# #         #     page_content=content,
# #         #     metadata={
# #         #         "source": filename,
# #         #         "faculty_name": name_text,
# #         #         "designation": desig_text,
# #         #         "url": link_url,
# #         #         "file_hash": filehash,
# #         #         "type": "faculty"
# #         #     }
# #         # ))
# #         subject = item.select_one(".faculty-subject")
# #         subject_text = subject.get_text(strip=True) if subject else "Unknown"

# #         content = f"Name: {name_text}\nDesignation: {desig_text}\nSubject: {subject_text}"
# #         documents.append(Document(
# #             page_content=content,
# #             metadata={
# #                 "source": filename,
# #                 "faculty_name": name_text,
# #                 "designation": desig_text,
# #                 "subject": subject_text,
# #                 "file_hash": filehash,
# #                 "type": "faculty"
# #             }
# #         ))
# #     return documents
# # def extract_faculty_items(soup: BeautifulSoup, filename: str, filehash: str) -> List[Document]:
# #     documents = []
# #     faculty_items = soup.select(".faculty-item")
# #     if not faculty_items:
# #         return []

# #     for item in faculty_items:
# #         name = item.select_one(".faculty-name")
# #         desig = item.select_one(".faculty-designation")
# #         subject = item.select_one(".faculty-subject")
# #         link = item.select_one(".profile-link a")

# #         # Safely extract text
# #         name_text = name.get_text(strip=True) if name else "Unknown"
# #         desig_text = desig.get_text(strip=True) if desig else "Unknown"
# #         subject_text = subject.get_text(strip=True) if subject else "Unknown"
# #         link_url = link["href"] if link and link.has_attr("href") else "URL Not Provided"

# #         content = f"Name: {name_text}\nDesignation: {desig_text}\nSubject: {subject_text}"
# #         documents.append(Document(
# #             page_content=content,
# #             metadata={
# #                 "source": filename,
# #                 "faculty_name": name_text,
# #                 "designation": desig_text,
# #                 "subject": subject_text,
# #                 "url": link_url,
# #                 "file_hash": filehash,
# #                 "type": "faculty"
# #             }
# #         ))
# #     return documents
# def extract_faculty_items(soup: BeautifulSoup, filename: str, filehash: str) -> List[Document]:
#     documents = []
#     faculty_items = soup.select(".faculty-item")
#     if not faculty_items:
#         return []

#     for item in faculty_items:
#         name = item.select_one(".faculty-name")
#         desig = item.select_one(".faculty-designation")
#         branch = item.select_one(".branch-info")
#         link = item.select_one("a")  # Can be email or placement PDF

#         name_text = name.get_text(strip=True) if name else "Unknown"
#         desig_text = desig.get_text(strip=True) if desig else "Unknown"
#         branch_text = branch.get_text(strip=True) if branch else "Unknown"
#         link_url = link["href"] if link and link.has_attr("href") else "URL Not Provided"

#         # Detect if this is a placement report (no designation)
#         if "Placement Details" in name_text:
#             content = f"Placement Report: {name_text}\nLink: {link_url}"
#             doc_type = "placement_report"
#             documents.append(Document(
#                 page_content=content,
#                 metadata={
#                     "source": filename,
#                     "report_name": name_text,
#                     "url": link_url,
#                     "file_hash": filehash,
#                     "type": doc_type
#                 }
#             ))
#         else:
#             # Regular faculty
#             content = f"Name: {name_text}\nDesignation: {desig_text}\nSubject/Branch: {branch_text}\nLink: {link_url}"
#             documents.append(Document(
#                 page_content=content,
#                 metadata={
#                     "source": filename,
#                     "faculty_name": name_text,
#                     "designation": desig_text,
#                     "subject": branch_text,
#                     "url": link_url,
#                     "file_hash": filehash,
#                     "type": "faculty"
#                 }
#             ))

#     return documents

# def extract_placement_reports(soup: BeautifulSoup, filename: str, filehash: str) -> List[Document]:
#     documents = []
#     report_items = soup.select(".content-section h2 + .coordinator-list .faculty-item")
#     if not report_items:
#         return []

#     for item in report_items:
#         name = item.select_one(".faculty-name")
#         link = item.select_one(".branch-info a")

#         report_name = name.get_text(strip=True) if name else "Unknown"
#         url = link["href"] if link and link.has_attr("href") else "URL Not Provided"

#         content = f"Report: {report_name}\nLink: {url}"
#         documents.append(Document(
#             page_content=content,
#             metadata={
#                 "source": filename,
#                 "report_name": report_name,
#                 "url": url,
#                 "file_hash": filehash,
#                 "type": "placement_report"
#             }
#         ))
#     return documents



# def extract_generic_chunks(soup: BeautifulSoup, filename: str, filehash: str) -> List[Document]:
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=CHUNK_SIZE,
#         chunk_overlap=CHUNK_OVERLAP
#     )
#     for tag in soup(["script", "style", "noscript"]):
#         tag.decompose()
#     text = " ".join(soup.stripped_strings).strip()
#     if not text:
#         return []

#     chunks = splitter.split_text(text)
#     return [
#         Document(
#             page_content=chunk.strip(),
#             metadata={
#                 "source": filename,
#                 "file_hash": filehash,
#                 "type": "generic"
#             }
#         )
#         for chunk in chunks if len(chunk.strip()) > 50
#     ]

# def load_and_split(html_files: List[str]) -> List[Document]:
#     documents: List[Document] = []

#     for path in html_files:
#         filename = os.path.relpath(path, HTML_DIR)
#         filehash = file_hash(path)
#         try:
#             try:
#                 html_content = open(path, "r", encoding="utf-8").read()
#             except UnicodeDecodeError:
#                 html_content = open(path, "r", encoding="latin1").read()

#             soup = BeautifulSoup(html_content, "html.parser")
#             faculty_docs = extract_faculty_items(soup, filename, filehash)
#             if faculty_docs:
#                 documents.extend(faculty_docs)
#             else:
#                 generic_docs = extract_generic_chunks(soup, filename, filehash)
#                 if generic_docs:
#                     documents.extend(generic_docs)
#                 else:
#                     print(f"⚠️ Skipping empty or unprocessable file: {filename}")

#         except Exception as e:
#             print(f"❌ Error reading {filename}: {e}")

#     print(f"✅ Extracted {len(documents)} total chunks.")
#     return documents

# def already_ingested(vs: Chroma) -> dict:
#     existing = {}
#     try:
#         stored = vs.get(include=["metadatas"])
#         for meta in stored.get("metadatas", []):
#             if meta and "source" in meta and "file_hash" in meta:
#                 existing[meta["source"]] = meta["file_hash"]
#     except Exception:
#         pass
#     return existing

# def build_vectorstore():
#     os.makedirs(CHROMA_DIR, exist_ok=True)

#     embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
#     vectorstore = Chroma(
#         persist_directory=CHROMA_DIR,
#         embedding_function=embeddings
#     )

#     html_files = find_html_files(HTML_DIR)
#     if not html_files:
#         print("❌ No HTML files found in folder:", HTML_DIR)
#         return

#     existing = already_ingested(vectorstore)
#     to_process = [p for p in html_files if file_hash(p) != existing.get(os.path.relpath(p, HTML_DIR))]

#     if not to_process:
#         print("✅ All HTML files are already up to date. Nothing new to ingest.")
#         return

#     print(f"🆕 Found {len(to_process)} new or modified HTML files.")
#     docs = load_and_split(to_process)
#     total_docs = len(docs)
#     print(f"📄 Total {total_docs} chunks prepared for embedding.")

#     # Optional: Chunk count per file
#     file_chunk_count = defaultdict(int)
#     for doc in docs:
#         file_chunk_count[doc.metadata["source"]] += 1

#     print("\n📊 Chunk count per file:")
#     for file, count in file_chunk_count.items():
#         print(f"   - {file}: {count} chunks")

#     num_batches = ceil(total_docs / CHROMA_MAX_BATCH)
#     for i in range(num_batches):
#         start, end = i * CHROMA_MAX_BATCH, min((i + 1) * CHROMA_MAX_BATCH, total_docs)
#         batch = docs[start:end]
#         print(f"\n🚀 Embedding batch {i + 1}/{num_batches} ({len(batch)} chunks)...")
#         try:
#             vectorstore.add_documents(batch)
#             print("✅ Batch committed successfully.")
#         except Exception as e:
#             print(f"❌ Error while embedding batch {i + 1}: {e}")
#         finally:
#             del batch
#             gc.collect()

#     print("\n🎯 Ingestion completed successfully.")
#     print(f"📦 Vector store saved at: {CHROMA_DIR}")

# if __name__ == "__main__":
#     build_vectorstore()
import os
import glob
import hashlib
import gc
from math import ceil
from typing import List
from bs4 import BeautifulSoup
from collections import defaultdict

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ---------------- CONFIG ---------------- #
HTML_DIR = "html_files"
CHROMA_DIR = "chroma_html"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
CHROMA_MAX_BATCH = 5000
# ---------------------------------------- #

def file_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def find_html_files(directory: str) -> List[str]:
    return glob.glob(os.path.join(directory, "**", "*.html"), recursive=True)

# -------------------- Extraction -------------------- #

def extract_faculty_items(soup: BeautifulSoup, filename: str, filehash: str) -> List[Document]:
    documents = []
    faculty_items = soup.select(".faculty-item")
    if not faculty_items:
        return []

    for item in faculty_items:
        name = item.select_one(".faculty-name")
        desig = item.select_one(".faculty-designation")
        subject = item.select_one(".faculty-subject")
        link = item.select_one(".profile-link a")

        name_text = name.get_text(strip=True) if name else "Unknown"
        desig_text = desig.get_text(strip=True) if desig else "Unknown"
        subject_text = subject.get_text(strip=True) if subject else "Unknown"
        link_url = link["href"] if link and link.has_attr("href") else "URL Not Provided"

        content = f"Name: {name_text}\nDesignation: {desig_text}\nSubject: {subject_text}\nProfile: {link_url}"
        documents.append(Document(
            page_content=content,
            metadata={
                "source": filename,
                "faculty_name": name_text,
                "designation": desig_text,
                "subject": subject_text,
                "url": link_url,
                "file_hash": filehash,
                "type": "faculty"
            }
        ))
    return documents

def extract_placement_reports(soup: BeautifulSoup, filename: str, filehash: str) -> List[Document]:
    documents = []
    # Select placement report items
    report_items = soup.select(".content-section h2:contains('Downloadable Placement Reports') + .coordinator-list .faculty-item")
    
    if not report_items:
        # fallback: try all .coordinator-list .faculty-item
        report_items = soup.select(".coordinator-list .faculty-item")

    for item in report_items:
        name_tag = item.select_one(".faculty-name")
        link_tag = item.select_one(".branch-info a")

        report_name = name_tag.get_text(strip=True) if name_tag else "Unknown"
        url = link_tag["href"] if link_tag and link_tag.has_attr("href") else "URL Not Provided"

        content = f"Report: {report_name}\nLink: {url}"
        documents.append(Document(
            page_content=content,
            metadata={
                "source": filename,
                "report_name": report_name,
                "url": url,
                "file_hash": filehash,
                "type": "placement_report"
            }
        ))
    return documents


def extract_generic_chunks(soup: BeautifulSoup, filename: str, filehash: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.stripped_strings).strip()
    if not text:
        return []

    chunks = splitter.split_text(text)
    return [
        Document(
            page_content=chunk.strip(),
            metadata={
                "source": filename,
                "file_hash": filehash,
                "type": "generic"
            }
        )
        for chunk in chunks if len(chunk.strip()) > 50
    ]

# -------------------- Loader -------------------- #

def load_and_split(html_files: List[str]) -> List[Document]:
    documents: List[Document] = []

    for path in html_files:
        filename = os.path.relpath(path, HTML_DIR)
        filehash = file_hash(path)
        try:
            try:
                html_content = open(path, "r", encoding="utf-8").read()
            except UnicodeDecodeError:
                html_content = open(path, "r", encoding="latin1").read()

            soup = BeautifulSoup(html_content, "html.parser")

            # Extract faculty
            faculty_docs = extract_faculty_items(soup, filename, filehash)
            if faculty_docs:
                documents.extend(faculty_docs)

            # Extract placement reports
            placement_docs = extract_placement_reports(soup, filename, filehash)
            if placement_docs:
                documents.extend(placement_docs)

            # Extract generic text if nothing else
            if not faculty_docs and not placement_docs:
                generic_docs = extract_generic_chunks(soup, filename, filehash)
                if generic_docs:
                    documents.extend(generic_docs)
                else:
                    print(f"⚠️ Skipping empty or unprocessable file: {filename}")

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

    print(f"✅ Extracted {len(documents)} total chunks.")
    return documents

# -------------------- Vectorstore -------------------- #

def already_ingested(vs: Chroma) -> dict:
    existing = {}
    try:
        stored = vs.get(include=["metadatas"])
        for meta in stored.get("metadatas", []):
            if meta and "source" in meta and "file_hash" in meta:
                existing[meta["source"]] = meta["file_hash"]
    except Exception:
        pass
    return existing

def build_vectorstore():
    os.makedirs(CHROMA_DIR, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    html_files = find_html_files(HTML_DIR)
    if not html_files:
        print("❌ No HTML files found in folder:", HTML_DIR)
        return

    existing = already_ingested(vectorstore)
    to_process = [p for p in html_files if file_hash(p) != existing.get(os.path.relpath(p, HTML_DIR))]

    if not to_process:
        print("✅ All HTML files are already up to date. Nothing new to ingest.")
        return

    print(f"🆕 Found {len(to_process)} new or modified HTML files.")
    docs = load_and_split(to_process)
    total_docs = len(docs)
    print(f"📄 Total {total_docs} chunks prepared for embedding.")

    # Optional: Chunk count per file
    file_chunk_count = defaultdict(int)
    for doc in docs:
        file_chunk_count[doc.metadata["source"]] += 1

    print("\n📊 Chunk count per file:")
    for file, count in file_chunk_count.items():
        print(f"   - {file}: {count} chunks")

    num_batches = ceil(total_docs / CHROMA_MAX_BATCH)
    for i in range(num_batches):
        start, end = i * CHROMA_MAX_BATCH, min((i + 1) * CHROMA_MAX_BATCH, total_docs)
        batch = docs[start:end]
        print(f"\n🚀 Embedding batch {i + 1}/{num_batches} ({len(batch)} chunks)...")
        try:
            vectorstore.add_documents(batch)
            print("✅ Batch committed successfully.")
        except Exception as e:
            print(f"❌ Error while embedding batch {i + 1}: {e}")
        finally:
            del batch
            gc.collect()

    print("\n🎯 Ingestion completed successfully.")
    print(f"📦 Vector store saved at: {CHROMA_DIR}")

if __name__ == "__main__":
    build_vectorstore()
