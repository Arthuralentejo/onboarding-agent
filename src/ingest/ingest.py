"""
Main Ingestion Module - MentorIA
Orchestrates the complete document ingestion process.
"""

import argparse
import sys

from src.ingest.loaders import load_documents
from src.ingest.processing import split_documents, generate_embeddings
from src.ingest.storage import store_in_mongodb


def ingest_documents(
    documents_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
):
    """
    Main ingestion function that can be called externally.

    Args:
        documents_path: Path to the directory containing documents
        chunk_size: Chunk size in characters (default: 1000)
        chunk_overlap: Overlap between chunks in characters (default: 200)
        database_name: Database name (optional, uses DATABASE env)
        collection_name: Collection name (optional, uses COLLECTION env)

    Raises:
        ValueError: If credentials or settings are not defined
        FileNotFoundError: If the document directory does not exist
    """

    # Load documents
    documents = load_documents(documents_path)

    # Split into chunks
    chunks = split_documents(
        documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Generate embeddings
    chunks_with_embeddings = generate_embeddings(chunks)

    # Store in MongoDB
    store_in_mongodb(chunks_with_embeddings)

    print("Ingestion completed successfully!")


def main():
    """
    Main function of the ingestion script (for standalone use).
    Maintains command-line compatibility via argparse.
    """
    parser = argparse.ArgumentParser(
        description=("Document ingestion for MentorIA knowledge base")
    )
    parser.add_argument(
        "documents_path",
        type=str,
        help="Path to the directory containing documents (PDF and TXT)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size in characters (default: 1000)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks in characters (default: 200)",
    )
    parser.add_argument(
        "--database",
        type=str,
        default=None,
        help="MongoDB database name (optional, uses DATABASE env)",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="MongoDB collection name (optional, uses COLLECTION env)",
    )

    args = parser.parse_args()

    try:
        ingest_documents(
            documents_path=args.documents_path,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
    except Exception as e:
        print(f"Error during ingestion: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
