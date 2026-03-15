from src.rag import load_documents, retrieve_parking_info


def test_load_documents_returns_content():
    docs = load_documents()
    assert len(docs) == 1
    assert "XYZ Company" in docs[0].page_content


def test_retrieve_parking_info_returns_relevant_text():
    result = retrieve_parking_info("Where is the parking lot located?")
    assert "Vecsés" in result and "Lincoln út" in result