"""
Database module for chat history and session management.

This module provides a flexible database abstraction layer through the DBProvider
pattern, supporting multiple database backends (SQLite, PostgreSQL, MySQL, etc.).

Quick Start:
    >>> from db import init_db, save_message, get_history
    >>> init_db()
    >>> save_message("user_1", "user", "Hello")
    >>> history = get_history("user_1")

For advanced usage with multiple providers, see db.README.md
"""

# Import core provider classes
from .db_provider import (
    DBProvider,
    SQLiteProvider,
    PostgreSQLProvider,
    MySQLProvider,
    create_sqlite_provider,
    create_provider_from_config,
)

# Import high-level API functions
from .chat_history import (
    # Provider management
    register_provider,
    list_providers,
    set_default_provider,
    get_default_provider,
    # Database operations
    init_db,
    save_message,
    get_history,
    get_session_state,
    set_session_state,
)

__all__ = [
    # Provider classes
    "DBProvider",
    "SQLiteProvider",
    "PostgreSQLProvider",
    "MySQLProvider",
    # Provider factories
    "create_sqlite_provider",
    "create_provider_from_config",
    # Provider management
    "register_provider",
    "list_providers",
    "set_default_provider",
    "get_default_provider",
    # Database operations
    "init_db",
    "save_message",
    "get_history",
    "get_session_state",
    "set_session_state",
]

__version__ = "1.0.0"
__author__ = "EggsTech"
