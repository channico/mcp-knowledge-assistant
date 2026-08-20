from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import pytest
from openai import OpenAI

from mcp_knowledge_assistant.vector_store_server import (
    fetch_vector_store_document,
    search_vector_store,
)


def openai_client_mock() -> tuple[OpenAI, MagicMock]:
    mock = MagicMock()
    return cast(OpenAI, mock), mock


def test_search_returns_each_matching_document_once() -> None:
    client, mock = openai_client_mock()
    mock.vector_stores.search.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(file_id="file-123", filename="cats.pdf"),
            SimpleNamespace(file_id="file-123", filename="cats.pdf"),
            SimpleNamespace(file_id="file-456", filename="dogs.pdf"),
        ]
    )

    output = search_vector_store("pet care", client, "vs-test")

    assert [result.id for result in output.results] == ["file-123", "file-456"]
    mock.vector_stores.search.assert_called_once_with(
        vector_store_id="vs-test",
        query="pet care",
    )


def test_blank_search_does_not_call_openai() -> None:
    client, mock = openai_client_mock()

    assert search_vector_store("   ", client, "vs-test").results == []
    mock.vector_stores.search.assert_not_called()


def test_fetch_combines_content_and_metadata() -> None:
    client, mock = openai_client_mock()
    mock.vector_stores.files.content.return_value = SimpleNamespace(
        data=[SimpleNamespace(text="First section"), SimpleNamespace(text="Second section")]
    )
    mock.vector_stores.files.retrieve.return_value = SimpleNamespace(
        attributes={"topic": "cats"}
    )
    mock.files.retrieve.return_value = SimpleNamespace(filename="cats.pdf")

    output = fetch_vector_store_document("file-123", client, "vs-test")

    assert output.title == "cats.pdf"
    assert output.text == "First section\nSecond section"
    assert output.metadata == {"topic": "cats"}


def test_fetch_requires_a_document_id() -> None:
    client, _ = openai_client_mock()

    with pytest.raises(ValueError, match="Document ID is required"):
        fetch_vector_store_document("", client, "vs-test")
