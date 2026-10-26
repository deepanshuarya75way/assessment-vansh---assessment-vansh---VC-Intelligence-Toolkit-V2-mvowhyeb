from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SwarmspaceApplication(Base):
    __tablename__ = "swarmspace_applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    founder_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    application_text: Mapped[str] = mapped_column(Text, nullable=False)
    github_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    arxiv_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
