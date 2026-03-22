# import os
# import gc
# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List, Any
# from starlette.middleware.cors import CORSMiddleware
# import asyncio

# from langchain_chroma import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.chains import RetrievalQA
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema import BaseRetriever, Document
# from langchain.schema.runnable import RunnableParallel, RunnablePassthrough, RunnableLambda

# # Load environment variables
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# # ---------------- CONFIG ----------------
# PDF_CHROMA_DIR = "chroma_db_pdfss"
# WEB_CHROMA_DIR = "chroma_db_webss"
# EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# # ----------------------------------------

# # ---------------- GLOBALS ----------------
# pdf_retriever = None
# web_retriever = None
# llm_chain = None

# # ----------- Combined Retriever (CRITICAL UPDATE HERE) ---------
# class CombinedRetriever(BaseRetriever):
#     pdf_retriever: BaseRetriever
#     web_retriever: BaseRetriever
#     k: int = 4

#     def _get_relevant_documents(self, query: str, **kwargs) -> List[Document]:
#         # --- LOGIC: Prioritize PDFs for document keywords ---
#         query_lower = query.lower()
#         is_document_query = any(keyword in query_lower for keyword in ["syllabus", "pdf", "file", "document", "regulations", "brochure", "fees"])
        
#         pdf_docs = self.pdf_retriever.get_relevant_documents(query)
#         web_docs = self.web_retriever.get_relevant_documents(query)

#         if is_document_query:
#             # If it's a document query, prioritize 3 PDF results and 1 Web result
#             combined = pdf_docs[:3] + web_docs[:1]
#         else:
#             # For general queries, take 2 from each (default)
#             k_half = max(1, self.k // 2)
#             combined = pdf_docs[:k_half] + web_docs[:k_half]
            
#         return combined

#     async def _aget_relevant_documents(self, query: str, **kwargs) -> List[Document]:
#         query_lower = query.lower()
#         is_document_query = any(keyword in query_lower for keyword in ["syllabus", "pdf", "file", "document", "regulations", "brochure", "fees"])
        
#         pdf_docs, web_docs = await asyncio.gather(
#             self.pdf_retriever.aget_relevant_documents(query),
#             self.web_retriever.aget_relevant_documents(query)
#         )
        
#         if is_document_query:
#             combined = pdf_docs[:3] + web_docs[:1]
#         else:
#             k_half = max(1, self.k // 2)
#             combined = pdf_docs[:k_half] + web_docs[:k_half]
            
#         return combined

#     @property
#     def InputType(self) -> Any:
#         return str

#     @property
#     def OutputType(self) -> Any:
#         return List[Document]

# # ------------- FastAPI ----------------
# app = FastAPI(title="College Chatbot API")
# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class QueryModel(BaseModel):
#     question: str

# @app.on_event("startup")
# async def startup_event():
#     global llm_chain, pdf_retriever, web_retriever

#     if not GOOGLE_API_KEY:
#         raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")

#     try:
#         # 1️⃣ Initialize embeddings
#         embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

#         # 2️⃣ Load Chroma vectorstores
#         pdf_db = Chroma(persist_directory=PDF_CHROMA_DIR, embedding_function=embeddings)
#         web_db = Chroma(persist_directory=WEB_CHROMA_DIR, embedding_function=embeddings)
        
#         pdf_retriever = pdf_db.as_retriever(search_kwargs={"k": 2})
#         web_retriever = web_db.as_retriever(search_kwargs={"k": 2})

#         # 3️⃣ Combined retriever
#         combined_retriever = CombinedRetriever(pdf_retriever=pdf_retriever, web_retriever=web_retriever, k=4)

#         # 4️⃣ LLM setup (Gemini)
#         llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             temperature=0.2,
#             api_key=GOOGLE_API_KEY
#         )

#         # 5️⃣ Prompt template (CRITICAL UPDATE HERE)
#         QA_PROMPT = ChatPromptTemplate.from_messages([
#             ("system", f"""
#                 You are a helpful assistant for Sri Vasavi Engineering College.
#                 Use ONLY the provided context to answer questions concisely and accurately.
                
#                 **CRITICAL INSTRUCTION: If the user explicitly asks for a document (e.g., 'v23 syllabus pdf', 'fee structure'), or if the answer is sourced from a single, short document, YOU MUST PROVIDE A CLICKABLE MARKDOWN LINK to the document URL found in the context.**
                
#                 **REQUIRED OUTPUT FORMAT:**
#                 1. Answer the user's question.
#                 2. If documents were used, append a list of the sources used, formatted as: 
#                    **Source:** [Document Filename](Public URL)
#                    *Example: Source: [v23_syllabus.pdf](https://www.srivasaviengg.ac.in/path/to/v23_syllabus.pdf)*
                
#                 If no answer is found in the context, say clearly that the information is not available.
                
#                 Context (Sources and Content):
#                 {{context}}
#             """),
#             ("human", "{question}"),
#         ])

#         # 6️⃣ Format docs: Structured Source Info (CRITICAL UPDATE HERE)
#         def format_docs(docs):
#             formatted = []
#             for i, doc in enumerate(docs):
#                 # Retrieve the URL exactly as stored by the ingestion script
#                 url = doc.metadata.get("url", "URL Not Provided")
#                 source = doc.metadata.get('source', 'Unknown')
                
#                 # Structure the context clearly for the LLM
#                 formatted.append(f"""
# ---
# DOCUMENT CHUNK {i+1}
# FILENAME: {source}
# PUBLIC_URL_FOR_LINK: {url}
# CONTENT: {doc.page_content}
# ---
#                 """)
#             return "\n\n".join(formatted)

#         # 7️⃣ Build chain
#         llm_chain = (
#             RunnableParallel({
#                 "context": combined_retriever | format_docs, 
#                 "question": RunnablePassthrough()
#             })
#             | QA_PROMPT
#             | llm
#             | RunnableLambda(lambda x: x.content)
#         )

#         print("🤖 Chatbot service started and models loaded.")

#     except Exception as e:
#         print(f"❌ Initialization Error: {e}. Ensure ingest.py was run successfully and the Chroma directories exist.")
#         llm_chain = None 

# @app.post("/chat")
# async def get_answer(query: QueryModel):
#     if llm_chain is None:
#         raise HTTPException(status_code=503, detail="Service not ready. Check logs for initialization errors.")
    
#     try:
#         response = await llm_chain.ainvoke(query.question)
#         return {"answer": response}
#     except Exception as e:
#         print(f"Error during chain invocation: {e}")
#         raise HTTPException(status_code=500, detail="Internal error during chat processing.")

# @app.get("/")
# def health_check():
#     return {"status": "ok", "service": "College Chatbot RAG API"}
import os
import gc
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
from starlette.middleware.cors import CORSMiddleware
import asyncio

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseRetriever, Document
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough, RunnableLambda

# ---------------- ENV ----------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------- CONFIG ----------------
PDF_CHROMA_DIR = "chroma_db_pdfss"
WEB_CHROMA_DIR = "chroma_db_webss"
HTML_CHROMA_DIR = "chroma_html"   # New HTML DB
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------- GLOBALS ----------------
pdf_retriever = None
web_retriever = None
html_retriever = None
llm_chain = None

# ----------- Combined Retriever (updated to include HTML) ---------
class CombinedRetriever(BaseRetriever):
    pdf_retriever: BaseRetriever
    web_retriever: BaseRetriever
    html_retriever: BaseRetriever
    k: int = 4

    def _get_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        query_lower = query.lower()
        is_document_query = any(keyword in query_lower for keyword in ["syllabus", "pdf", "file", "document", "regulations", "brochure", "fees"])
        
        pdf_docs = self.pdf_retriever.get_relevant_documents(query)
        web_docs = self.web_retriever.get_relevant_documents(query)
        html_docs = self.html_retriever.get_relevant_documents(query)

        if is_document_query:
            combined = pdf_docs[:3] + web_docs[:1] + html_docs[:1]
        else:
            k_third = max(1, self.k // 3)
            combined = pdf_docs[:k_third] + web_docs[:k_third] + html_docs[:k_third]

        return combined

    async def _aget_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        query_lower = query.lower()
        is_document_query = any(keyword in query_lower for keyword in ["syllabus", "pdf", "file", "document", "regulations", "brochure", "fees"])
        
        pdf_docs, web_docs, html_docs = await asyncio.gather(
            self.pdf_retriever.aget_relevant_documents(query),
            self.web_retriever.aget_relevant_documents(query),
            self.html_retriever.aget_relevant_documents(query)
        )

        if is_document_query:
            combined = pdf_docs[:3] + web_docs[:1] + html_docs[:1]
        else:
            k_third = max(1, self.k // 3)
            combined = pdf_docs[:k_third] + web_docs[:k_third] + html_docs[:k_third]

        return combined

    @property
    def InputType(self) -> Any:
        return str

    @property
    def OutputType(self) -> Any:
        return List[Document]

# ------------- FastAPI ----------------
app = FastAPI(title="College Chatbot API")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryModel(BaseModel):
    question: str

@app.on_event("startup")
async def startup_event():
    global llm_chain, pdf_retriever, web_retriever, html_retriever

    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")

    try:
        # 1️⃣ Initialize embeddings
        embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

        # 2️⃣ Load Chroma vectorstores
        pdf_db = Chroma(persist_directory=PDF_CHROMA_DIR, embedding_function=embeddings)
        web_db = Chroma(persist_directory=WEB_CHROMA_DIR, embedding_function=embeddings)
        html_db = Chroma(persist_directory=HTML_CHROMA_DIR, embedding_function=embeddings)

        pdf_retriever = pdf_db.as_retriever(search_kwargs={"k": 2})
        web_retriever = web_db.as_retriever(search_kwargs={"k": 2})
        html_retriever = html_db.as_retriever(search_kwargs={"k": 2})

        # 3️⃣ Combined retriever (with HTML)
        combined_retriever = CombinedRetriever(
            pdf_retriever=pdf_retriever,
            web_retriever=web_retriever,
            html_retriever=html_retriever,
            k=4
        )

        # 4️⃣ LLM setup (Gemini)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            api_key=GOOGLE_API_KEY
        )

        # 5️⃣ Prompt template
       # 5️⃣ Prompt template
        QA_PROMPT = ChatPromptTemplate.from_messages([
               ("system", """
            You are an assistant for Sri Vasavi Engineering College.
            Use only the provided context to answer questions.

            If the user asks for information like "Who is the HOD of Civil department",
            look for department abbreviations (e.g., CE, EEE, CSE) and return the **HOD's name, department name, and contact info** from the context.

            If the user asks for a document (e.g., syllabus, fee structure), include a clickable Markdown link:
            [Document Name] https://example.com/path.pdf

            If no relevant information is found in the context, say:
            "The requested information is not available in the current data."

            Context:
            {context}
            """),
                ("human", "{question}")
            ])
        # 6️⃣ Format docs
        def format_docs(docs):
            formatted = []
            for i, doc in enumerate(docs):
                url = doc.metadata.get("url", "URL Not Provided")
                source = doc.metadata.get("source", "Unknown")
                formatted.append(f"""
---
DOCUMENT CHUNK {i+1}
FILENAME: {source}
PUBLIC_URL: {url}
CONTENT: {doc.page_content}
---
                """)
            return "\n\n".join(formatted)

        # 7️⃣ Build chain
        llm_chain = (
            RunnableParallel({
                "context": combined_retriever | format_docs,
                "question": RunnablePassthrough()
            })
            | QA_PROMPT
            | llm
            | RunnableLambda(lambda x: x.content)
        )

        print("🤖 Chatbot service started and ready.")

    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        llm_chain = None

@app.post("/chat")
async def get_answer(query: QueryModel):
    if llm_chain is None:
        raise HTTPException(status_code=503, detail="Service not ready. Check logs.")
    
    try:
        response = await llm_chain.ainvoke(query.question)
        return {"answer": response}
    except Exception as e:
        print(f"❌ Chain invocation error: {e}")
        raise HTTPException(status_code=500, detail="Internal error during chat processing.")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "College Chatbot RAG API"}