"""
Retrieval Module - MentorIA Core
Responsible for vector search in MongoDB Atlas.
"""

import os
from typing import List

from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from src.config import get_embedding_model, get_mongodb_client


DATABASE_NAME = os.getenv("DATABASE")
COLLECTION_NAME = os.getenv("COLLECTION")


def retrieve_context(
    question: str,
    k: int = 5,
) -> List[str]:
    """
    Retrieves the k most relevant chunks for a
    question using vector search.

    Args:
        question: User's question
        google_api_key: Google API key
        mongodb_connection_string: MongoDB connection string
        database_name: Database name
        collection_name: Collection name
        k: Number of chunks to retrieve (default: 5)

    Returns:
        List[str]: List of retrieved chunk texts
    """
    try:
        embeddings_model = get_embedding_model()
        question_embedding = embeddings_model.embed_query(question)

        client = get_mongodb_client()

        if not COLLECTION_NAME:
            raise ValueError("COLLECTION not found in environment variables")

        if not DATABASE_NAME:
            raise ValueError("DATABASE not found in environment variables")

        db = client[DATABASE_NAME]
        collection: Collection = db[COLLECTION_NAME]

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": question_embedding,
                    "numCandidates": k * 10,
                    "limit": k,
                }
            },
            {
                "$project": {
                    "text": 1,
                    "metadata": 1,
                    "source": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        results = list(collection.aggregate(pipeline))
        client.close()

        if not results:
            print(
                "Warning: Vector search returned no results. "
                "Check if the 'vector_index' is configured "
                "in MongoDB Atlas."
            )
            return []
    except PyMongoError as e:
        print(f"Error connecting to MongoDB or executing the query: {e}")
        raise

    return [result["text"] for result in results]
