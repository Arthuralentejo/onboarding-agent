"""
Text Processing Module - MentorIA Ingest
Responsible for splitting documents into chunks and generating embeddings.
"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import get_embedding_model


def split_documents(
    documents: List, chunk_size: int = 1000, chunk_overlap: int = 200
) -> List:
    """
    Splits documents into smaller chunks.

    Args:
        documents: List of documents to be split
        chunk_size: Chunk size in characters
        chunk_overlap: Overlap between chunks in characters

    Returns:
        List: List of document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Documents split into {len(chunks)} chunks")

    return chunks


def generate_embeddings(chunks: List) -> List:
    """
    Generates embeddings for each chunk using Google Gemini.

    Args:
        chunks: List of document chunks
        google_api_key: Google API key

    Returns:
        List: List of chunks with generated embeddings
    """
    embeddings_model = get_embedding_model()

    print("Generating embeddings...")
    texts = [chunk.page_content for chunk in chunks]
    embedding_vectors = embeddings_model.embed_documents(texts)

    # Add embeddings to chunk metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["embedding"] = embedding_vectors[i]

    print(f"Embeddings generated for {len(chunks)} chunks")

    return chunks
