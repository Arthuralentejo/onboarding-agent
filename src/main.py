"""
MentorIA Main File
Command-line interface to run ingestion and RAG queries.
"""

import argparse
import sys

from src.core.agent_orchestrator import generate_response
from ingest.ingest import ingest_documents


def interactive_query_mode():
    """
    Interactive mode for making RAG queries.
    """
    print("\n=== MentorIA - Interactive Mode ===")
    print("Enter your questions (or 'exit' to quit)\n")

    while True:
        try:
            question = input("Question: ").strip()

            if not question:
                continue

            if question.lower() in ["sair", "exit", "quit"]:
                print("Exiting...")
                break

            print("\nProcessing...")
            response = generate_response(question)
            print(f"\nResponse:\n{response}\n")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}\n", file=sys.stderr)


def single_query_mode(question: str):
    """
    Single query mode.
    """
    try:
        print("Processing...")
        response = generate_response(question)
        print(f"\nQuestion: {question}")
        print(f"\nResponse:\n{response}")
    except Exception as e:
        print(f"Error processing query: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main function that manages the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="MentorIA - RAG System for Intelligent Queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:

  # Interactive mode
  python src/main.py query

  # Single query
  python src/main.py query "What is the vacation policy?"

  # Document ingestion
  python src/main.py ingest ./documents

  # Ingestion with custom parameters
  python src/main.py ingest ./documents --chunk-size 1500 --chunk-overlap 300
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Subparser for queries
    query_parser = subparsers.add_parser("query", help="Make queries to the RAG system")
    query_parser.add_argument(
        "question",
        nargs="?",
        type=str,
        help="Question to ask (optional - if omitted, enters interactive mode)",
    )

    # Subparser for ingestion
    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest documents into the knowledge base"
    )
    ingest_parser.add_argument(
        "documents_path",
        type=str,
        help="Path to the directory containing documents (PDF and TXT)",
    )
    ingest_parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size in characters (default: 1000)",
    )
    ingest_parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks in characters (default: 200)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "query":
        if args.question:
            single_query_mode(args.question)
        else:
            interactive_query_mode()

    elif args.command == "ingest":
        # Run ingestion using the main function
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
