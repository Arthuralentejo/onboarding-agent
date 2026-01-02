"""
Document Loading Module - MentorIA Ingest
Responsible for loading documents of different formats (PDF, TXT).
"""

from pathlib import Path
from typing import List
import sys

from langchain_community.document_loaders import PyPDFLoader, TextLoader


def load_documents(documents_path: str) -> List:
    """
    Loads documents from a directory.

    Args:
        documents_path: Path to the directory containing documents

    Returns:
        List: List of loaded documents

    Raises:
        FileNotFoundError: If the directory does not exist
        ValueError: If no documents are found
    """
    documents = []
    path = Path(documents_path)

    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {documents_path}")

    # Process PDF files
    pdf_files = list(path.glob("*.pdf"))
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded: {pdf_file.name} ({len(docs)} pages)")
        except Exception as e:
            print(f"Error loading {pdf_file.name}: {e}", file=sys.stderr)

    # Process TXT files
    txt_files = list(path.glob("*.txt"))
    for txt_file in txt_files:
        try:
            loader = TextLoader(str(txt_file), encoding="utf-8")
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded: {txt_file.name}")
        except Exception as e:
            print(f"Error loading {txt_file.name}: {e}", file=sys.stderr)

    if not documents:
        raise ValueError(f"No documents found in {documents_path}")

    return documents
