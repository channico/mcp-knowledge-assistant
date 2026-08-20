import pytest

from mcp_knowledge_assistant.knowledge_base import fetch_document, search_documents


def test_search_finds_relevant_documents() -> None:
    output = search_documents("MCP tools and protocol")

    assert output.results
    assert output.results[0].id == "mcp-basics"


def test_search_with_blank_query_returns_no_results() -> None:
    assert search_documents("   ").results == []


def test_fetch_returns_complete_document() -> None:
    document = fetch_document("retrieval-workflow")

    assert document.title == "Search and Fetch Retrieval"
    assert "search tool" in document.text.lower()
    assert document.url


def test_fetch_rejects_unknown_id() -> None:
    with pytest.raises(ValueError, match="Document not found"):
        fetch_document("missing")
