import os
import re
import faiss
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer

# Load API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found. Please ensure it is set in your .env file.")

# Configure the Groq client
client = Groq(api_key=GROQ_API_KEY)

# Sentence Transformer model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# FAISS index for similarity search
# The dimension of 'all-MiniLM-L6-v2' embeddings is 384
index = faiss.IndexFlatL2(384)


def call_groq_api(prompt: str) -> str:
    """Calls the Groq API using the groq SDK."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred while calling the Groq API: {str(e)}"


def clean_response(text: str) -> str:
    """Cleans AI response but keeps full MCQs (questions + options + answers)."""
    # Remove only common boilerplate prefixes
    text = re.sub(r"(?i)^here are.*?questions?[:\s]*", "", text.strip())
    text = re.sub(r"(?i)^based on the given text[:,]?", "", text)
    # Remove "Answer:" lines only if they repeat at the start of each MCQ
    # but keep question numbers and options intact
    text = re.sub(r"(?i)^answer\s*[:\-]\s*", "", text)
    return text.strip()



def chunk_text(text, chunk_size=500, chunk_overlap=50):
    """Splits text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks


def generate_response(query, pdf_text):
    """Generates a response using a RAG pipeline with Groq."""
    chunks = chunk_text(pdf_text)
    if not chunks:
        return "The PDF appears to be empty or text could not be extracted."
        
    embeddings = model.encode(chunks)
    faiss.normalize_L2(embeddings)

    index.reset()
    index.add(embeddings)

    query_emb = model.encode([query])
    faiss.normalize_L2(query_emb)
    
    D, I = index.search(query_emb, k=min(3, len(chunks)))

    if I.size > 0:
        context = ' '.join([chunks[i] for i in I[0] if i < len(chunks)])
    else:
        context = "No relevant information found in the document."

    prompt = f"""
You are an expert study assistant. Based ONLY on the provided context from the PDF, answer the user's query.

User Query: "{query}"
PDF Context: "{context}"

Answer clearly and concisely:
"""

    raw_response = call_groq_api(prompt)
    return clean_response(raw_response)


def generate_quiz(pdf_text):
    """Generates a multiple-choice quiz from the provided text using Groq."""
    prompt = f"""
Create 10 multiple-choice quiz questions with 4 options (A, B, C, D) and correct answers,
based strictly on the following text.
Do NOT include any introductory text like "Here are 10 questions" or explanations.

Text:
{pdf_text[:4000]}
"""
    raw_response = call_groq_api(prompt)
    return clean_response(raw_response)


def generate_mindmap(pdf_text):
    """Generates a mind map in JSON format from the provided text using Groq."""
    prompt = f"""
Analyze the following text. Identify the main topics and subtopics.
Return the output as a valid JSON object for a mind map (no code blocks or explanations).

Example:
{{"main_topic": "Central Idea", "children": [{{"main_topic": "Subtopic 1"}}, {{"main_topic": "Subtopic 2"}}]}}

Text:
{pdf_text[:4000]}
"""
    raw_response = call_groq_api(prompt)
    return clean_response(raw_response)


# For quick local testing
if __name__ == "__main__":
    print("🧠 Testing Groq connection...")
    print(generate_response("What is AI?", "Artificial intelligence is the study of creating machines that think."))

    print("\n📝 Testing quiz generation...")
    print(generate_quiz("Artificial intelligence helps in automation and smart systems."))

    print("\n🧩 Testing mind map generation...")
    print(generate_mindmap("AI includes subfields like machine learning, neural networks, and NLP."))
