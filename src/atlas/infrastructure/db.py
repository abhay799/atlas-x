from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Record(Base):
    __tablename__ = "atlas_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(64), index=True)
    key: Mapped[str] = mapped_column(String(128), index=True)
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class SQLStore:
    def __init__(self, url: str = "sqlite+pysqlite:///:memory:") -> None:
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(self.engine)

    def append(self, kind: str, key: str, payload: dict[str, object]) -> None:
        with self.Session.begin() as s:
            s.add(
                Record(kind=kind, key=key, payload=json.dumps(payload, default=str, sort_keys=True))
            )

    def list(self, kind: str, key: str | None = None) -> list[dict[str, object]]:
        with self.Session() as s:
            q = select(Record).where(Record.kind == kind)
            if key is not None:
                q = q.where(Record.key == key)
            return [json.loads(r.payload) for r in s.scalars(q.order_by(Record.id)).all()]
