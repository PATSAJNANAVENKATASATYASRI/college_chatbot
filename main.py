from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# LangChain and Google Gemini Imports
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document

# --- Load Environment Variables ---
load_dotenv()

# --- Debugging Output ---
print("--- Environment Variables ---")
for key, value in os.environ.items():
    if "KEY" in key.upper() or "TOKEN" in key.upper():
        print(f"{key}: {'*' * 8} (hidden)")
    else:
        print(f"{key}: {value}")
print("----------------------------------")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in your .env file.")

# --- Vector DB Path ---
VECTOR_DB_PATH = "chroma_db_web/"

# --- FastAPI Setup ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Model for Chat Request ---
class ChatRequest(BaseModel):
    query: str

# --- Global LLM Components ---
vectorstore = None
conversation_chain = None
memory = None

# --- Helper: Load and Split Web Pages ---
def load_and_process_web_documents(urls: list):
    print(f"Loading from: {urls}")
    loader = WebBaseLoader(urls)
    documents = loader.load()

    # OPTIONAL: Print preview of content
    for i, doc in enumerate(documents):
        print(f"\n--- Document {i+1} ---\n{doc.page_content[:500]}\n")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(documents)

# --- Startup Initialization ---
@app.on_event("startup")
async def startup_event():
    global vectorstore, conversation_chain, memory

    print("🔧 Initializing RAG components...")

    # College URLs
    urls = [
        "https://srivasaviengg.ac.in/",
        "https://srivasaviengg.ac.in/templates/DEPT/cse.html",
        "https://srivasaviengg.ac.in/templates/DEPT/ece.html",
        "https://srivasaviengg.ac.in/templates/DEPT/eee.html",
        "https://srivasaviengg.ac.in/templates/DEPT/cst.html",
        "https://srivasaviengg.ac.in/templates/DEPT/cai.html",
        "https://srivasaviengg.ac.in/templates/DEPT/ds.html",
        "https://srivasaviengg.ac.in/templates/DEPT/aiml.html",
        "https://srivasaviengg.ac.in/templates/DEPT/ect.html",
        "https://srivasaviengg.ac.in/templates/DEPT/mech.html",
        "https://srivasaviengg.ac.in/templates/DEPT/civil.html",
        "https://srivasaviengg.ac.in/templates/DEPT/bsh.html",
        "https://srivasaviengg.ac.in/templates/DEPT/mba.html"
    ]

    docs = load_and_process_web_documents(urls)

    # Manual info (Optional fallback)
    manual_info = """
    The Head of the Department (HOD) of Computer Science and Engineering (CSE) at Sri Vasavi Engineering College is Dr. XYZ.
    He has extensive experience in teaching and research in the field of Computer Science.
    """
    docs.append(Document(page_content=manual_info))

    # Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Vector Store
    if os.path.exists(VECTOR_DB_PATH) and os.listdir(VECTOR_DB_PATH):
        print("✅ Loading existing Chroma vector DB.")
        vectorstore = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)
    else:
        print("📚 Creating new Chroma vector DB.")
        vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=VECTOR_DB_PATH)
        vectorstore.persist()

    # Gemini LLM (use gemini-1.5-pro-latest)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    print("🧠 Using Gemini 1.5 Pro")

    # Memory and Chain
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        return_source_documents=False  # set True for debugging
    )

    print("✅ RAG system initialized.")

import re

@app.post("/chat")
async def chat_with_assistant(request: ChatRequest):
    try:
        query = request.query.lower()

        # Simple check for navigation intent
        if re.search(r"\b(how do i go|get to|directions|route|navigate|way to)\b", query):
            # Extract origin and destination (very simple heuristic)
            # Example: "how do i go from CSE Department to ECE Department"
            if " from " in query and " to " in query:
                origin = query.split(" from ")[1].split(" to ")[0].strip()
                destination = query.split(" to ")[1].strip()
                base_url = "https://www.google.com/maps/dir/?api=1"
                url = f"{base_url}&origin={origin}+Sri+Vasavi+Engineering+College&destination={destination}+Sri+Vasavi+Engineering+College"
                return {"response": f"Here is the route: {url}"}

        # Otherwise, use RAG system
        result = conversation_chain.invoke({"question": query})
        return {"response": result["answer"]}

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

class RouteRequest(BaseModel):
    origin: str
    destination: str

# Common landmarks inside Sri Vasavi Engineering College
LOCATION_MAP = {
    "library": "Sri Vasavi Engineering College Library, Tadepalligudem",
    "bsh": "Sri Vasavi Engineering College Basic Sciences and Humanities Block, Tadepalligudem",
    "cse": "Sri Vasavi Engineering College Computer Science & Engineering Block, Tadepalligudem",
    "ece": "Sri Vasavi Engineering College Electronics & Communication Engineering Block, Tadepalligudem",
    "eee": "Sri Vasavi Engineering College Electrical & Electronics Engineering Block, Tadepalligudem",
    "mech": "Sri Vasavi Engineering College Mechanical Engineering Block, Tadepalligudem",
    "civil": "Sri Vasavi Engineering College Civil Engineering Block, Tadepalligudem",
    "mba": "Sri Vasavi Engineering College MBA Block, Tadepalligudem",
    "hostel": "Sri Vasavi Engineering College Hostel, Tadepalligudem",
    "canteen": "Sri Vasavi Engineering College Canteen, Tadepalligudem",
    "ground": "Sri Vasavi Engineering College Playground, Tadepalligudem"
}

@app.post("/route")
async def get_route(request: RouteRequest):
    base_url = "https://www.google.com/maps/dir/?api=1"

    # Resolve short names using LOCATION_MAP
    origin = LOCATION_MAP.get(request.origin.lower(), request.origin)
    destination = LOCATION_MAP.get(request.destination.lower(), request.destination)

    url = f"{base_url}&origin={origin}&destination={destination}"
    return {"map_url": url}


