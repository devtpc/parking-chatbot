from src.rag import get_vectorstore


queries = {
    "Where is the parking lot located?": ["Vecsés", "Lincoln út"],
    "What vehicles are allowed in the parking lot?": ["3.5", "buses"],
    "What information is required for a reservation?": ["name", "car", "reservation"],
}


def evaluate(k=3):
    vectorstore = get_vectorstore()

    for query, expected_keywords in queries.items():
        docs = vectorstore.similarity_search(query, k=k)

        combined_text = " ".join(doc.page_content.lower() for doc in docs)

        found = sum(
            1 for keyword in expected_keywords if keyword.lower() in combined_text
        )

        recall = found / len(expected_keywords)
        precision = found / k

        print("Query:", query)
        print(f"Recall@{k}: {recall:.2f}")
        print(f"Precision@{k}: {precision:.2f}")
        print("-" * 40)


if __name__ == "__main__":
    evaluate()