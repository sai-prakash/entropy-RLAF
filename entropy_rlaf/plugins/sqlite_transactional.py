"""SQLite transactional verifier with savepoint-based rollback."""

from __future__ import annotations

import sqlite3

from entropy_rlaf.core.base import RollbackManager
from entropy_rlaf.core.models import CandidateAction, VerificationResult


class SQLiteRollbackManager(RollbackManager):
    """Rollback manager backed by SQLite savepoints."""

    def __init__(self, connection: sqlite3.Connection, savepoint: str = "entropy_sp") -> None:
        self.connection = connection
        self.savepoint = savepoint

    def begin(self) -> None:
        self.connection.execute(f"SAVEPOINT {self.savepoint}")

    def rollback(self) -> None:
        self.connection.execute(f"ROLLBACK TO {self.savepoint}")
        self.connection.execute(f"RELEASE {self.savepoint}")


class SQLiteTransactionalVerifier:
    """Runs SQL safely in-memory, rolling back mutations after each branch."""

    name = "sqlite_transactional"

    def __init__(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        self.connection.execute("INSERT INTO users (name) VALUES ('alice'), ('bob')")
        self.connection.commit()
        self.rollback_manager = SQLiteRollbackManager(self.connection)

    async def verify(self, action: CandidateAction) -> VerificationResult:
        if action.language.lower() != "sql":
            return VerificationResult(
                verifier_name=self.name,
                passed=True,
                score=1.0,
                rationale="Language not SQL; transactional execution skipped.",
            )

        self.rollback_manager.begin()
        try:
            self.connection.execute(action.content)
            rows = self.connection.execute("SELECT COUNT(*) FROM users").fetchone()
            count = int(rows[0]) if rows else 0
            passed = count >= 2
            return VerificationResult(
                verifier_name=self.name,
                passed=passed,
                score=1.0 if passed else 0.0,
                rationale="SQL executed in isolated transaction."
                if passed
                else "SQL changed protected dataset unexpectedly.",
            )
        except sqlite3.Error as error:
            return VerificationResult(
                verifier_name=self.name,
                passed=False,
                score=0.0,
                rationale=f"SQLite error: {error}",
            )
        finally:
            self.rollback_manager.rollback()
