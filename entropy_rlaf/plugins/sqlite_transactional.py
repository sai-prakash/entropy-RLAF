"""SQLite transactional verifier plugin with savepoint rollback."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

from entropy_rlaf.core.interfaces import RollbackManager
from entropy_rlaf.core.models import VerificationResult


@dataclass
class SQLiteTransactionalVerifier(RollbackManager):
    """Executes SQL in-memory and rolls back each branch transactionally."""

    name: str = "sqlite_transactional"
    _connection: sqlite3.Connection = field(init=False)

    def __post_init__(self) -> None:
        self._connection = sqlite3.connect(":memory:")
        self._connection.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER, name TEXT);")
        self._connection.execute("INSERT INTO users VALUES (1, 'alice');")

    async def begin(self) -> None:
        self._connection.execute("SAVEPOINT rlaf_branch;")

    async def rollback(self) -> None:
        try:
            self._connection.execute("ROLLBACK TO SAVEPOINT rlaf_branch;")
            self._connection.execute("RELEASE SAVEPOINT rlaf_branch;")
        except sqlite3.Error:
            pass

    async def verify(self, payload: str) -> VerificationResult:
        await self.begin()
        try:
            self._connection.executescript(payload)
            row_count = self._connection.execute("SELECT COUNT(*) FROM users;").fetchone()[0]
            passed = row_count >= 1
            return VerificationResult(
                verifier_name=self.name,
                passed=passed,
                score=1.0 if passed else 0.0,
                rationale="SQL executed in isolated transaction",
                metadata={"row_count": str(row_count)},
            )
        except sqlite3.Error as exc:
            return VerificationResult(
                verifier_name=self.name,
                passed=False,
                score=0.0,
                rationale=f"SQLite execution failed: {exc}",
            )
        finally:
            await self.rollback()
