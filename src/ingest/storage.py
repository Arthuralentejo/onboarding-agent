"""
Storage Module - MentorIA Ingest
Responsible for MongoDB Atlas operations, including collection creation
and vector search indexes.
"""

from typing import List
import os
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from src.config import get_mongodb_client

DATABASE_NAME = os.getenv("DATABASE")
COLLECTION_NAME = os.getenv("COLLECTION")


def ensure_collection(
    client: MongoClient,
    database_name: str,
    collection_name: str,
    embedding_dimensions: int = 768,
) -> Collection:
    """
    Ensures that the collection and vector search index exist.

    Args:
        client: Connected MongoDB client
        database_name: Database name
        collection_name: Collection name
        embedding_dimensions: Embedding dimensions (default: 768)

    Returns:
        Collection: Ensured MongoDB collection
    """
    db: Database = client[database_name]

    # Check if collection exists, if not, create it
    if collection_name not in db.list_collection_names():
        print(f"Creating collection '{collection_name}'...")
        db.create_collection(collection_name)
        print(f"Collection '{collection_name}' created successfully")
    else:
        print(f"Collection '{collection_name}' already exists")

    collection: Collection = db[collection_name]

    # Check if vector search index exists
    # Note: Creating vector search indexes in MongoDB Atlas
    # usually requires the Atlas API or web interface.
    # Here we check if the index exists and inform if it doesn't.
    try:
        # List vector search indexes (if available via API)
        indexes = collection.list_search_indexes()
        vector_index_exists = False

        for index in indexes:
            if index.get("name") == "vector_index":
                vector_index_exists = True
                print("Index 'vector_index' already exists")
                break

        if not vector_index_exists:
            print("WARNING: Index 'vector_index' not found.")
            print("To create the vector search index, use the MongoDB Atlas UI or API:")
            print("  - Name: vector_index")
            print("  - Field: embedding")
            print("  - Type: vector")
            print(f"  - Dimensions: {embedding_dimensions}")
            print("  - Similarity: cosine")
            print(
                "\nThe system will continue, but vector searches may not "
                "work until the index is created."
            )

    except Exception as e:
        # If list_search_indexes is not available
        # (old driver version) or if there is an error, just inform
        print(f"WARNING: Could not check vector search indexes automatically: {e}")
        print("Make sure the 'vector_index' is configured in MongoDB Atlas.")

    return collection


def store_in_mongodb(
    chunks: List,
):
    """
    Stores chunks with embeddings in MongoDB Atlas.

    Args:
        chunks: List of chunks with embeddings
        mongodb_connection_string: MongoDB connection string
        database_name: Database name
        collection_name: Collection name
    """
    client = get_mongodb_client()

    if not COLLECTION_NAME:
        raise ValueError("COLLECTION not found in environment variables")

    if not DATABASE_NAME:
        raise ValueError("DATABASE not found in environment variables")

    collection = ensure_collection(client, DATABASE_NAME, COLLECTION_NAME)

    # Prepare documents for insertion
    documents_to_insert = []
    for chunk in chunks:
        doc = {
            "text": chunk.page_content,
            "embedding": chunk.metadata.get("embedding"),
            "metadata": {k: v for k, v in chunk.metadata.items() if k != "embedding"},
            "source": chunk.metadata.get("source", "unknown"),
        }
        documents_to_insert.append(doc)

    # Insert documents
    if documents_to_insert:
        result = collection.insert_many(documents_to_insert)
        print(f"{len(result.inserted_ids)} documents inserted into collection")
    else:
        print("No documents to insert")

    client.close()
