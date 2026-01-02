"""
Configuration Module - MentorIA Core
Manages loading credentials from environment variables.
"""

import os
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain_tavily import TavilySearch
from pymongo import MongoClient

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """
    Loads the embedding model.

    Returns:
        GoogleGenerativeAIEmbeddings: Embedding model.
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", google_api_key=GOOGLE_API_KEY
    )


def get_mongodb_client() -> MongoClient:
    """
    Loads the MongoDB client.

    Returns:
        MongoClient: MongoDB client.
    """
    if not MONGODB_CONNECTION_STRING:
        raise ValueError("MONGODB_CONNECTION_STRING not found in environment variables")
    return MongoClient(MONGODB_CONNECTION_STRING)


def get_llm_model(temperature=0.3) -> ChatGoogleGenerativeAI:
    """
    Creates a configured LLM instance.

    Args:
        temperature: Temperature for the LLM (default: 0.3)

    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=temperature,
        response_mime_type="text/plain",
    )


def get_tavily_search_tool() -> TavilySearch:
    """
    Creates a Tavily search tool instance.

    Returns:
        TavilySearchResults: Configured search tool

    Raises:
        ValueError: If TAVILY_API_KEY is not set
    """
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not found in environment variables")
    return TavilySearch(
        max_results=3,
        api_key=TAVILY_API_KEY,
    )
