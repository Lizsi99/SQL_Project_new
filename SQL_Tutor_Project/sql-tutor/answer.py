"""
SQL Tutor — RAG Answer Module

Retrieves relevant knowledge-base chunks for a student's question and uses
a local Ollama LLM to generate a clear, pedagogically-focused answer.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, convert_to_messages
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

load_dotenv(override=True)

DB_NAME = str(Path(__file__).parent / "vector_db")
RETRIEVAL_K = 8

OLLAMA_LLM_MODEL   = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL    = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
HF_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

SYSTEM_PROMPT = """STRICT RULE: You must answer ONLY using the retrieved context provided below.
If the retrieved context does not contain enough information to answer the question, you MUST respond with exactly:
"I don't have information about that in my knowledge base."
Never use your pre-trained knowledge. Never guess or infer beyond what the context states.

You are a SQL tutor. When the context does contain the answer, apply this teaching style:
- Give clear, step-by-step explanations — don't just show the answer
- Always include a working SQL example when explaining a concept
- Point out common mistakes and pitfalls
- If the student's question contains a SQL error, explain what is wrong and why
- Keep answers focused: cover the concept fully but don't overwhelm beginners
- When showing SQL code, format it in markdown code blocks using ```sql

Retrieved context:
{context}

REMINDER: Use ONLY the above context. If it does not answer the question, say "I don't have information about that in my knowledge base." Do not use outside knowledge."""

print(f"[answer] Using local HuggingFace embeddings: {HF_EMBEDDING_MODEL}")
print(f"[answer] Using Ollama LLM: {OLLAMA_LLM_MODEL} @ {OLLAMA_BASE_URL}")

embeddings  = HuggingFaceEmbeddings(model_name=HF_EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=DB_NAME, embedding_function=embeddings)
retriever   = vectorstore.as_retriever(search_kwargs={"k": RETRIEVAL_K})
llm         = ChatOllama(model=OLLAMA_LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.2)


def fetch_context(question: str, history: list[dict]) -> list[Document]:
    """
    Build a combined query from the current question and prior user messages
    so that follow-up questions retrieve relevant context even when they are
    short (e.g. "Can you show an example?").
    """
    prior_user_msgs = " ".join(
        m["content"] for m in history if m["role"] == "user"
    )
    combined_query = f"{prior_user_msgs} {question}".strip()
    return retriever.invoke(combined_query)


def format_context(docs: list[Document]) -> str:
    """Concatenate retrieved chunks into a single context string."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def answer_question(
    question: str,
    history: list[dict] | None = None,
) -> tuple[str, list[Document]]:
    """
    Generate a tutoring answer for the student's question.

    Args:
        question:  The student's current message.
        history:   Prior conversation turns as a list of
                   {"role": "user"|"assistant", "content": "..."} dicts.

    Returns:
        (answer_text, retrieved_docs)
    """
    if history is None:
        history = []

    docs = fetch_context(question, history)
    context = format_context(docs)

    system_prompt = SYSTEM_PROMPT.format(context=context)
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(content=f"{question}\n\n(Answer using ONLY the retrieved context. If it doesn't contain the answer, say so.)"))

    response = llm.invoke(messages)
    return response.content, docs
