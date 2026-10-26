from groq import AsyncGroq

from app.core.config import settings

_groq_client: AsyncGroq | None = None


def get_groq_client() -> AsyncGroq:
    global _groq_client

    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY must be set for Groq calls.")

    if _groq_client is None:
        _groq_client = AsyncGroq(api_key=settings.groq_api_key)

    return _groq_client
