import os

import psycopg2
import pytest
from cybsuite.cyberdb import CyberDB
from psycopg2 import sql

temp_db_name = "_cybsuite_cyberdb_"
user = os.environ.get("CYBSUITE_DB_USER", "postgres")
password = os.environ.get("CYBSUITE_DB_PASSWORD", "postgres")
host = os.environ.get("CYBSUITE_DB_HOST", "127.0.0.1")

_cyberdb = None


@pytest.fixture
def new_cyberdb() -> CyberDB:
    """Return a new PentestDB instance and clean the DB after tests."""
    global _cyberdb
    if _cyberdb is None:
        _cyberdb = CyberDB(temp_db_name, user=user, password=password, host=host)
        _cyberdb.migrate()
    yield _cyberdb
    _cyberdb.cleardb()


def pytest_sessionfinish(session, exitstatus):
    """Remove the PostgreSQL database after all tests have been run."""
    try:
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(
            dbname="postgres", user=user, password=password, host=host
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Drop the test database
        cursor.execute(
            sql.SQL("DROP DATABASE {} WITH (FORCE)").format(
                sql.Identifier(temp_db_name)
            )
        )

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to drop the database: {e}")
