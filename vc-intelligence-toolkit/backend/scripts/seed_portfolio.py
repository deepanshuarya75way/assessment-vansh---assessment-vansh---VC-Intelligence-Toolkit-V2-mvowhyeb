import asyncio
import sys
from pathlib import Path

from sqlalchemy import func, select

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.database.session import get_sessionmaker
from app.models.portfolio import PortfolioCompany
from app.utils.embedding import embed_text
from app.utils.logger import get_logger

logger = get_logger(__name__)

PORTFOLIO_COMPANIES = [
    {
        "name": "Composio",
        "description": "Agent tooling and integration infrastructure for AI agents to reliably call external tools and APIs",
    },
    {
        "name": "Confido Health",
        "description": "AI voice agents for healthcare patient engagement and clinical workflows",
    },
    {
        "name": "Coreworks",
        "description": "Natural language query engine for enterprise financial data",
    },
    {
        "name": "Dhiwise",
        "description": "AI platform that converts product ideas directly into working application code",
    },
    {
        "name": "Emergent",
        "description": "Agentic AI-powered IDE for autonomous software development",
    },
    {
        "name": "Gibran",
        "description": "AI reasoning and small language model research for enterprise applications",
    },
    {
        "name": "Hunar",
        "description": "AI-powered recruiter automating frontline hiring workflows",
    },
    {
        "name": "Metaforms",
        "description": "AI-driven market research and survey platform",
    },
    {
        "name": "Spendflo",
        "description": "AI-powered SaaS spend management and procurement platform",
    },
    {
        "name": "Architect",
        "description": "AI infrastructure and tooling for enterprise engineering teams",
    },
    {
        "name": "Sentra",
        "description": "AI-native data security and governance platform",
    },
    # Placeholder AI-native enterprise/infra companies to round out seed coverage.
    {
        "name": "VectorPlane",
        "description": "AI-native infrastructure for vector search, retrieval evaluation, and enterprise RAG observability",
    },
    {
        "name": "OpsPilot",
        "description": "Autonomous AI operations platform for cloud incident response and infrastructure remediation",
    },
    {
        "name": "LedgerMind",
        "description": "AI financial operations copilot for enterprise accounting workflows and audit preparation",
    },
    {
        "name": "SecureFlow AI",
        "description": "Agentic security workflow automation for enterprise SOC triage and compliance evidence collection",
    },
    {
        "name": "SchemaForge",
        "description": "AI data engineering platform for schema mapping, warehouse documentation, and pipeline generation",
    },
]


async def seed_portfolio() -> int:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL must be set before seeding portfolio data.")

    inserted = 0
    skipped = 0
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        for company in PORTFOLIO_COMPANIES:
            name = company["name"]
            existing = await session.scalar(
                select(PortfolioCompany).where(PortfolioCompany.name == name)
            )
            if existing is not None:
                logger.info("Skipping %s; already exists", name)
                skipped += 1
                continue

            logger.info("Embedding %s...", name)
            embedding = embed_text(company["description"])
            session.add(
                PortfolioCompany(
                    name=name,
                    description=company["description"],
                    embedding=embedding,
                )
            )
            inserted += 1

        await session.commit()
        total_rows = await session.scalar(select(func.count()).select_from(PortfolioCompany))

    logger.info(
        "Inserted %s companies; skipped %s existing companies; portfolio row count is %s",
        inserted,
        skipped,
        total_rows,
    )
    return int(total_rows or 0)


if __name__ == "__main__":
    row_count = asyncio.run(seed_portfolio())
    print(f"Portfolio row count: {row_count}")
