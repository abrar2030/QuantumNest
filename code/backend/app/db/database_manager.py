import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, Generator

from app.core.config import get_database_url, get_settings
from app.core.logging import get_logger
from app.core.time_utils import utc_now
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

logger = get_logger(__name__)


class DatabaseManager:
    """
    Advanced database manager with connection pooling and monitoring.

    Works with both SQLite (dev/test) and PostgreSQL (staging/production).
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.database_url = get_database_url(self.settings)
        self.engine = None
        self.SessionLocal = None
        self._is_sqlite = self.database_url.startswith("sqlite")
        self._lock = threading.Lock()
        self._stats: Dict[str, Any] = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "query_count": 0,
            "slow_queries": 0,
            "last_reset": utc_now(),
        }
        self._slow_query_threshold = 1.0  # seconds

    # ── Initialisation ────────────────────────────────────────────────────────

    def initialize(self) -> None:
        """Create the engine and session factory."""
        try:
            if self._is_sqlite:
                engine_kwargs: Dict[str, Any] = {
                    "poolclass": StaticPool,
                    "connect_args": {"check_same_thread": False, "timeout": 20},
                    "echo": self.settings.DEBUG,
                }
            else:
                engine_kwargs = {
                    "poolclass": QueuePool,
                    "pool_size": self.settings.DATABASE_POOL_SIZE,
                    "max_overflow": self.settings.DATABASE_MAX_OVERFLOW,
                    "pool_timeout": self.settings.DATABASE_POOL_TIMEOUT,
                    "pool_recycle": self.settings.DATABASE_POOL_RECYCLE,
                    "pool_pre_ping": True,
                    "echo": self.settings.DEBUG,
                }

            self.engine = create_engine(self.database_url, **engine_kwargs)
            self._setup_event_listeners()

            if self._is_sqlite:
                self._configure_sqlite()

            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
            logger.info(
                "DatabaseManager initialised — %s",
                "sqlite" if self._is_sqlite else self.database_url.split("@")[-1],
            )
        except Exception as exc:
            logger.error("Failed to initialise DatabaseManager: %s", exc, exc_info=True)
            raise

    def _setup_event_listeners(self) -> None:
        @event.listens_for(self.engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            with self._lock:
                self._stats["total_connections"] += 1
                self._stats["active_connections"] += 1

        @event.listens_for(self.engine, "close")
        def on_close(dbapi_connection, connection_record):
            with self._lock:
                self._stats["active_connections"] = max(
                    0, self._stats["active_connections"] - 1
                )

        @event.listens_for(self.engine, "before_cursor_execute")
        def before_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault("query_start_time", []).append(time.monotonic())
            with self._lock:
                self._stats["query_count"] += 1

        @event.listens_for(self.engine, "after_cursor_execute")
        def after_execute(conn, cursor, statement, parameters, context, executemany):
            times = conn.info.get("query_start_time", [])
            if times:
                total = time.monotonic() - times.pop()
                if total > self._slow_query_threshold:
                    with self._lock:
                        self._stats["slow_queries"] += 1
                    logger.warning(
                        "Slow query (%.3fs): %s",
                        total,
                        statement[:120].replace("\n", " "),
                    )
                else:
                    logger.debug(
                        "DB %s %.3fs",
                        statement.split()[0] if statement else "QUERY",
                        total,
                    )

    def _configure_sqlite(self) -> None:
        @event.listens_for(self.engine, "connect")
        def set_pragmas(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA cache_size=-64000")  # 64 MB
            cursor.close()

    # ── Session helpers ───────────────────────────────────────────────────────

    def get_session(self) -> Generator[Session, None, None]:
        """FastAPI dependency — yields a DB session and ensures cleanup."""
        if self.SessionLocal is None:
            raise RuntimeError(
                "DatabaseManager not initialised. Call initialize() first."
            )
        session: Session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context-manager that auto-commits or rolls back."""
        if self.SessionLocal is None:
            raise RuntimeError("DatabaseManager not initialised.")
        session: Session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── Health & stats ────────────────────────────────────────────────────────

    def health_check(self) -> Dict[str, Any]:
        """Return a dict describing the database connection health."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"status": "healthy", "stats": self._stats.copy()}
        except Exception as exc:
            return {"status": "unhealthy", "error": str(exc)}

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return self._stats.copy()

    def reset_stats(self) -> None:
        with self._lock:
            self._stats.update(
                {
                    "total_connections": 0,
                    "active_connections": self._stats["active_connections"],
                    "failed_connections": 0,
                    "query_count": 0,
                    "slow_queries": 0,
                    "last_reset": utc_now(),
                }
            )
