import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from .models import FetchOutput, SearchOutput, SearchResult


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "documents.json"


@lru_cache(maxsize=1)
def load_documents() -> list[dict[str, Any]]:
    with DATA_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def search_documents(query: str) -> SearchOutput:
    query_tokens = _tokens(query)
    if not query_tokens:
        return SearchOutput(results=[])

    ranked: list[tuple[int, dict[str, Any]]] = []
    for document in load_documents():
        searchable_text = " ".join(
            [
                document["title"],
                document["text"],
                " ".join(str(value) for value in document["metadata"].values()),
            ]
        )
        score = len(query_tokens & _tokens(searchable_text))
        if score:
            ranked.append((score, document))

    ranked.sort(key=lambda item: (-item[0], item[1]["title"]))
    return SearchOutput(
        results=[
            SearchResult(
                id=document["id"],
                title=document["title"],
                url=document["url"],
            )
            for _, document in ranked
        ]
    )


def fetch_document(document_id: str) -> FetchOutput:
    for document in load_documents():
        if document["id"] == document_id:
            return FetchOutput(**document)
    raise ValueError(f"Document not found: {document_id}")

