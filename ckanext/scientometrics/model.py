from __future__ import annotations

import logging
from typing import Any, TypedDict

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.ext.mutable import MutableDict

from ckan import model
from ckan.plugins import toolkit as tk

log = logging.getLogger(__name__)


class ExternalRef(TypedDict, total=False):
    id: str | None
    url: str | None


class _MetricBase(tk.BaseModel):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    source = Column(Text, nullable=False)
    external_id = Column(Text)
    external_url = Column(Text)
    status = Column(Text, nullable=False, default="pending")
    metrics = Column("metrics", MutableDict.as_mutable(JSONB), default=dict)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    extras = Column("extras", MutableDict.as_mutable(JSONB), default=dict)

    def dictize(self, _context: Any) -> dict[str, Any]:
        data = dict(self.metrics or {})
        data["status"] = self.status
        if self.external_id:
            data.setdefault("external_id", self.external_id)
        if self.external_url:
            data.setdefault("url", self.external_url)
            data.setdefault("external_url", self.external_url)
        return data


class UserMetric(_MetricBase):
    __tablename__ = "scim_user_metric"
    __table_args__ = (UniqueConstraint("user_id", "source", name="uq_scim_user_metric"),)
    user_id = Column(
        "user_id",
        Text,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    @classmethod
    def upsert(
        cls,
        user_id: str,
        source: str,
        metrics: dict[str, Any],
        external: ExternalRef | None = None,
        status: str = "pending",
    ) -> UserMetric:
        session = model.Session
        external = external or {}
        metrics = metrics or {}
        external_id = external.get("id")
        external_url = external.get("url")
        stmt = (
            insert(cls)
            .values(
                user_id=user_id,
                source=source,
                metrics=metrics,
                external_id=external_id,
                external_url=external_url,
                status=status,
            )
            .on_conflict_do_update(
                constraint="uq_scim_user_metric",
                set_={
                    "metrics": metrics,
                    "external_id": external_id,
                    "external_url": external_url,
                    "status": status,
                    "updated_at": func.now(),
                },
            )
            .returning(cls.id)
        )
        record_id = session.execute(stmt).scalar_one()
        session.flush()
        return session.get(cls, record_id)

    @classmethod
    def by_user_id(cls, user_id: str) -> list[UserMetric]:
        session = model.Session
        return session.query(cls).filter(cls.user_id == user_id).all()

    @classmethod
    def delete_by_user_id(cls, user_id: str) -> int:
        session = model.Session
        count = session.query(cls).filter(cls.user_id == user_id).delete(synchronize_session=False)
        session.flush()
        return count


class DatasetMetric(_MetricBase):
    __tablename__ = "scim_dataset_metric"
    __table_args__ = (UniqueConstraint("package_id", "source", name="uq_scim_dataset_metric"),)
    package_id = Column(
        "package_id",
        Text,
        ForeignKey("package.id", ondelete="CASCADE"),
        nullable=False,
    )

    @classmethod
    def upsert(
        cls,
        package_id: str,
        source: str,
        metrics: dict[str, Any],
        external: ExternalRef | None = None,
        status: str = "pending",
    ) -> DatasetMetric:
        session = model.Session
        external = external or {}
        metrics = metrics or {}
        external_id = external.get("id")
        external_url = external.get("url")
        stmt = (
            insert(cls)
            .values(
                package_id=package_id,
                source=source,
                metrics=metrics,
                external_id=external_id,
                external_url=external_url,
                status=status,
            )
            .on_conflict_do_update(
                constraint="uq_scim_dataset_metric",
                set_={
                    "metrics": metrics,
                    "external_id": external_id,
                    "external_url": external_url,
                    "status": status,
                    "updated_at": func.now(),
                },
            )
            .returning(cls.id)
        )
        record_id = session.execute(stmt).scalar_one()
        session.flush()
        return session.get(cls, record_id)

    @classmethod
    def by_package_id(cls, package_id: str) -> list[DatasetMetric]:
        session = model.Session
        return session.query(cls).filter(cls.package_id == package_id).all()

    @classmethod
    def delete_by_package_id(cls, package_id: str) -> int:
        session = model.Session
        count = session.query(cls).filter(cls.package_id == package_id).delete(synchronize_session=False)
        session.flush()
        return count


def init_tables() -> None:
    """Create extension tables if they are missing."""
    log.debug("Initializing scientometrics tables")
    engine = getattr(model.meta, "engine", None)
    if engine is None:
        log.warning("Scientometrics tables were not initialized: no engine bound yet")
        return
    model.meta.metadata.create_all(
        bind=engine,
        tables=[UserMetric.__table__, DatasetMetric.__table__],
        checkfirst=True,
    )
