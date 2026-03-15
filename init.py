from src.database import init_database
from src.rag import ingest_documents


def main() -> None:
    init_database()
    ingest_documents()
    print("Initialization completed.")


if __name__ == "__main__":
    main()