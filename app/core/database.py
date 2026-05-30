"""
Database singleton.

``Database`` is a thread-safe singleton that owns the SQLAlchemy engine and
session factory.  It is initialised once at application startup and reused
for the lifetime of the process.

Usage
-----
FastAPI dependency (preferred)::

    from app.core.database import get_db
    from sqlalchemy.orm import Session

    def my_route(db: Session = Depends(get_db)):
        ...

Direct access (e.g. scripts / tests)::

    from app.core.database import Database

    db_instance = Database.get_instance()
    with db_instance.session() as db:
        ...
"""

from __future__ import annotations

import logging
import threading
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    """
    Singleton wrapper around the SQLAlchemy engine and session factory.

    The first call to ``Database.get_instance()`` creates the engine; every
    subsequent call returns the same object.
    """

    _instance: Database | None = None
    _lock: threading.Lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Singleton lifecycle                                                  #
    # ------------------------------------------------------------------ #

    def __init__(self) -> None:
        self._engine: Engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,   # drop stale connections automatically
            pool_size=10,
            max_overflow=20,
            echo=settings.DEBUG,
        )
        self._session_factory: sessionmaker[Session] = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,  # keep attributes accessible after commit
        )
        logger.info("Database engine created — %s", settings.DATABASE_URL)

    @classmethod
    def get_instance(cls) -> Database:
        """Return (and lazily create) the singleton ``Database`` instance."""
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking — guard against concurrent first calls.
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------ #
    # Engine access                                                        #
    # ------------------------------------------------------------------ #

    @property
    def engine(self) -> Engine:
        """Expose the underlying ``Engine`` (e.g. for Alembic migrations)."""
        return self._engine

    # ------------------------------------------------------------------ #
    # Session helpers                                                      #
    # ------------------------------------------------------------------ #

    def get_session(self) -> Session:
        """
        Return a raw ``Session``.  The caller is fully responsible for
        ``commit()``, ``rollback()``, and ``close()``.

        Prefer ``session()`` context manager or the ``get_db`` FastAPI
        dependency for managed lifecycle.
        """
        return self._session_factory()

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Context manager that yields a ``Session``, commits on clean exit,
        and rolls back + re-raises on any exception.

        Example::

            with Database.get_instance().session() as db:
                db.add(some_object)
        """
        db: Session = self._session_factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    # ------------------------------------------------------------------ #
    # Health                                                               #
    # ------------------------------------------------------------------ #

    def ping(self) -> bool:
        """Return ``True`` if the database is reachable, ``False`` otherwise."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as exc:
            logger.error("Database ping failed: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    # Teardown                                                             #
    # ------------------------------------------------------------------ #

    def dispose(self) -> None:
        """
        Close all pooled connections.  Call at application shutdown to
        release resources cleanly.
        """
        self._engine.dispose()
        logger.info("Database engine disposed.")


# --------------------------------------------------------------------------- #
# Module-level helpers (backwards-compatible with the original module API)    #
# --------------------------------------------------------------------------- #

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — yields a ``Session`` scoped to the HTTP request.

    Commits automatically on clean exit; rolls back on exception.
    """
    db = Database.get_instance().get_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
