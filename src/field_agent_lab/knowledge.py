from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .models import Citation


TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]", re.IGNORECASE)
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "do",
    "does",
    "for",
    "how",
    "i",
    "in",
    "is",
    "me",
    "much",
    "of",
    "on",
    "the",
    "to",
    "what",
    "when",
    "you",
    "your",
}


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOPWORDS]


@dataclass(frozen=True)
class KnowledgeDocument:
    document_id: str
    title: str
    text: str
    locale: str


class KnowledgeBase:
    """Small deterministic retriever suitable for repeatable local evaluation."""

    def __init__(self, documents: list[KnowledgeDocument]):
        self.documents = documents
        self._tokens = [tokenize(document.title + " " + document.text) for document in documents]
        self._document_frequency = Counter(
            token for tokens in self._tokens for token in set(tokens)
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "KnowledgeBase":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls([KnowledgeDocument(**item) for item in raw])

    def search(self, query: str, *, locale: str = "en-US", limit: int = 3) -> list[Citation]:
        query_terms = Counter(tokenize(query))
        if not query_terms:
            return []

        total_docs = max(len(self.documents), 1)
        ranked: list[tuple[float, KnowledgeDocument]] = []
        for document, tokens in zip(self.documents, self._tokens, strict=True):
            if document.locale != locale and document.locale.split("-")[0] != locale.split("-")[0]:
                continue
            counts = Counter(tokens)
            score = 0.0
            for term, query_count in query_terms.items():
                if counts[term] == 0:
                    continue
                inverse_document_frequency = math.log(
                    1 + (total_docs + 1) / (self._document_frequency[term] + 1)
                )
                score += query_count * (1 + math.log(counts[term])) * inverse_document_frequency
            if score > 0:
                ranked.append((score, document))

        ranked.sort(key=lambda item: (-item[0], item[1].document_id))
        return [
            Citation(
                document_id=document.document_id,
                title=document.title,
                excerpt=document.text[:280],
                score=round(score, 4),
            )
            for score, document in ranked[:limit]
        ]
