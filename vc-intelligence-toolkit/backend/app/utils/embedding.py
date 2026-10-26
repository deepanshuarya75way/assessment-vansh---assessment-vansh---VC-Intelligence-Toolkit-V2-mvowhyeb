from typing import Any

from app.core.config import settings

_embedding_model: Any | None = None


def get_embedding_model() -> Any:
    global _embedding_model

    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer

        _embedding_model = SentenceTransformer(settings.embedding_model)

    return _embedding_model


def embed_text(text: str) -> list[float]:
    embedding = get_embedding_model().encode(text)
    return embedding.tolist()
