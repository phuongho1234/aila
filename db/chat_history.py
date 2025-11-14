import os
import sqlite3
from typing import List, Dict, Optional
from .db_provider import DBProvider, SQLiteProvider, create_sqlite_provider

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chat_history.db")


# Simple provider registry: map logical provider names to DBProvider instances.
# Use `register_provider` to add alternate DB providers and `set_default_provider`
# to change which provider is used when callers don't pass an explicit provider.
_PROVIDERS: Dict[str, DBProvider] = {}
_DEFAULT_PROVIDER = "default"

# Initialize default SQLite provider
_PROVIDERS["default"] = create_sqlite_provider(DEFAULT_DB_PATH)


def register_provider(name: str, provider: DBProvider, make_default: bool = False) -> None:
    """Register a database provider under a logical name.

    Args:
        name: Logical name for the provider
        provider: DBProvider instance (SQLiteProvider, PostgreSQLProvider, etc.)
        make_default: If True, set this as the default provider

    Example:
        provider = SQLiteProvider('/tmp/test.db')
        register_provider('test', provider, make_default=True)
    """
    _PROVIDERS[name] = provider
    if make_default:
        set_default_provider(name)


def list_providers() -> Dict[str, Dict]:
    """Return information about all registered providers."""
    return {name: provider.get_connection_info() for name, provider in _PROVIDERS.items()}


def set_default_provider(name: str) -> None:
    """Set the default provider by name. Raises KeyError if name unknown."""
    if name not in _PROVIDERS:
        raise KeyError(f"Provider not registered: {name}")
    global _DEFAULT_PROVIDER
    _DEFAULT_PROVIDER = name


def get_default_provider() -> str:
    return _DEFAULT_PROVIDER


def _resolve_provider(db_path: Optional[str], provider: Optional[str]) -> DBProvider:
    """Resolve the database provider: explicit db_path > named provider > default provider.
    
    Args:
        db_path: If provided, create a temporary SQLiteProvider for this path
        provider: Named provider from registry
        
    Returns:
        DBProvider instance to use for the operation
    """
    if db_path:
        # Create temporary SQLite provider for explicit path
        return create_sqlite_provider(db_path)
    if provider:
        if provider not in _PROVIDERS:
            raise KeyError(f"Provider not registered: {provider}")
        return _PROVIDERS[provider]
    return _PROVIDERS[_DEFAULT_PROVIDER]


def init_db(db_path: Optional[str] = None, provider: Optional[str] = None) -> str:
    """Create the database file and messages table if they don't exist.

    Returns the path to the database file created/used.
    """
    db_provider = _resolve_provider(db_path, provider)
    
    # Create tables using provider
    db_provider.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))
        )
        """
    )
    
    # sessions table stores simple per-user session state (e.g. emotional state, inferred incident type)
    db_provider.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            state TEXT,
            incident_type TEXT,
            emotion TEXT,
            updated_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))
        )
        """
    )
    
    # Return path info
    info = db_provider.get_connection_info()
    return info.get('db_path', str(info))





def save_message(user_id: str, role: str, content: str, db_path: Optional[str] = None, provider: Optional[str] = None) -> None:
    """Save a single message to the database.

    role: typically 'user' or 'assistant'.
    """
    db_provider = _resolve_provider(db_path, provider)
    db_provider.execute(
        "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )


def get_history(user_id: str, limit: int = 100, db_path: Optional[str] = None, provider: Optional[str] = None) -> List[Dict]:
    """Return conversation history for a user ordered by `created_at` ascending.

    Returns list of dicts: {id, user_id, role, content, created_at}
    """
    db_provider = _resolve_provider(db_path, provider)
    rows = db_provider.fetch_all(
        "SELECT id, user_id, role, content, created_at FROM messages WHERE user_id = ? ORDER BY created_at ASC LIMIT ?",
        (user_id, limit)
    )

    return [
        {
            "id": r[0],
            "user_id": r[1],
            "role": r[2],
            "content": r[3],
            "created_at": r[4],
        }
        for r in rows
    ]


def get_session_state(user_id: str, db_path: Optional[str] = None, provider: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Return the session state record for a user. If not present, returns defaults.

    Returns dict: { 'user_id': str, 'state': Optional[str], 'incident_type': Optional[str], 'emotion': Optional[str], 'updated_at': Optional[str] }
    """
    db_provider = _resolve_provider(db_path, provider)
    row = db_provider.fetch_one(
        "SELECT user_id, state, incident_type, emotion, updated_at FROM sessions WHERE user_id = ?",
        (user_id,)
    )

    if not row:
        return {"user_id": user_id, "state": None, "incident_type": None, "emotion": None, "updated_at": None}

    return {"user_id": row[0], "state": row[1], "incident_type": row[2], "emotion": row[3], "updated_at": row[4]}


def set_session_state(user_id: str, state: Optional[str] = None, incident_type: Optional[str] = None, emotion: Optional[str] = None, db_path: Optional[str] = None, provider: Optional[str] = None) -> None:
    """Insert or update the session state for a user.

    state: e.g., 'charged' or 'calm'
    incident_type: inferred incident label
    emotion: canonical emotion label
    """
    db_provider = _resolve_provider(db_path, provider)
    db_provider.execute(
        "INSERT INTO sessions (user_id, state, incident_type, emotion, updated_at) VALUES (?, ?, ?, ?, (strftime('%Y-%m-%d %H:%M:%f','now')))"
        " ON CONFLICT(user_id) DO UPDATE SET state=excluded.state, incident_type=excluded.incident_type, emotion=excluded.emotion, updated_at=excluded.updated_at",
        (user_id, state, incident_type, emotion)
    )
