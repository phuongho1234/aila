"""
Database Provider Module

Provides an abstract DBProvider interface and concrete implementations for different
database systems (SQLite, PostgreSQL, MySQL, etc.). All database operations in the
application should go through a provider instance for consistency and flexibility.
"""

import os
import sqlite3
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager


class DBProvider(ABC):
    """Abstract base class for database providers.
    
    Subclasses must implement connection management and query execution methods.
    """

    @abstractmethod
    def connect(self):
        """Establish and return a database connection."""
        pass

    @abstractmethod
    def close(self):
        """Close the database connection."""
        pass

    @abstractmethod
    @contextmanager
    def get_connection(self):
        """Context manager that yields a connection and ensures cleanup."""
        pass

    @abstractmethod
    def execute(self, query: str, params: Optional[Tuple] = None) -> None:
        """Execute a query (INSERT, UPDATE, DELETE, CREATE, etc.)."""
        pass

    @abstractmethod
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """Execute a SELECT query and return one row."""
        pass

    @abstractmethod
    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """Execute a SELECT query and return all rows."""
        pass

    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """Return metadata about the connection (type, path/host, etc.)."""
        pass


class SQLiteProvider(DBProvider):
    """SQLite database provider with connection pooling and context management."""

    def __init__(self, db_path: str, auto_create_dir: bool = True):
        """Initialize SQLite provider.
        
        Args:
            db_path: Path to the SQLite database file
            auto_create_dir: If True, create parent directories if they don't exist
        """
        self.db_path = db_path
        self._connection = None
        
        if auto_create_dir:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def connect(self):
        """Establish a connection to the SQLite database."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    @contextmanager
    def get_connection(self):
        """Context manager for connection handling.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            # Keep connection alive for reuse (don't close here)
            pass

    def execute(self, query: str, params: Optional[Tuple] = None) -> None:
        """Execute a query and commit."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())

    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """Execute a SELECT query and return one row."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()

    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """Execute a SELECT query and return all rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def get_connection_info(self) -> Dict[str, Any]:
        """Return connection metadata."""
        return {
            "type": "sqlite",
            "db_path": self.db_path,
            "exists": os.path.exists(self.db_path),
        }

    def __enter__(self):
        """Support using provider as context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection when exiting context."""
        self.close()

    def __repr__(self):
        return f"SQLiteProvider(db_path='{self.db_path}')"


class PostgreSQLProvider(DBProvider):
    """PostgreSQL database provider (placeholder for future implementation).
    
    Requires psycopg2 or psycopg3 to be installed.
    """

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self._connection = None
        raise NotImplementedError("PostgreSQL provider not yet implemented. Install psycopg2 and implement connection logic.")

    def connect(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    @contextmanager
    def get_connection(self):
        raise NotImplementedError()

    def execute(self, query: str, params: Optional[Tuple] = None) -> None:
        raise NotImplementedError()

    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        raise NotImplementedError()

    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        raise NotImplementedError()

    def get_connection_info(self) -> Dict[str, Any]:
        return {
            "type": "postgresql",
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
        }


class MySQLProvider(DBProvider):
    """MySQL database provider (placeholder for future implementation).
    
    Requires mysql-connector-python or pymysql to be installed.
    """

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self._connection = None
        raise NotImplementedError("MySQL provider not yet implemented. Install mysql-connector-python and implement connection logic.")

    def connect(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    @contextmanager
    def get_connection(self):
        raise NotImplementedError()

    def execute(self, query: str, params: Optional[Tuple] = None) -> None:
        raise NotImplementedError()

    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        raise NotImplementedError()

    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        raise NotImplementedError()

    def get_connection_info(self) -> Dict[str, Any]:
        return {
            "type": "mysql",
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
        }


# Provider factory functions
def create_sqlite_provider(db_path: str, auto_create_dir: bool = True) -> SQLiteProvider:
    """Factory function to create a SQLite provider."""
    return SQLiteProvider(db_path, auto_create_dir)


def create_provider_from_config(config: Dict[str, Any]) -> DBProvider:
    """Create a provider from a configuration dictionary.
    
    Args:
        config: Dict with 'type' key and type-specific parameters
        
    Example:
        config = {'type': 'sqlite', 'db_path': '/path/to/db.sqlite'}
        provider = create_provider_from_config(config)
    """
    provider_type = config.get("type", "").lower()
    
    if provider_type == "sqlite":
        return SQLiteProvider(
            db_path=config["db_path"],
            auto_create_dir=config.get("auto_create_dir", True)
        )
    elif provider_type == "postgresql":
        return PostgreSQLProvider(
            host=config["host"],
            port=config.get("port", 5432),
            database=config["database"],
            user=config["user"],
            password=config["password"]
        )
    elif provider_type == "mysql":
        return MySQLProvider(
            host=config["host"],
            port=config.get("port", 3306),
            database=config["database"],
            user=config["user"],
            password=config["password"]
        )
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
