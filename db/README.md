# Database Module Documentation

## Overview

This module provides a flexible database abstraction layer through the `DBProvider` pattern, allowing you to switch between different database systems (SQLite, PostgreSQL, MySQL) without changing your application code.

## Architecture

```
db/
├── db_provider.py      # Abstract DBProvider + concrete implementations
├── chat_history.py     # High-level API using providers
└── README.md          # This file
```

## Quick Start

### Using the default SQLite database

```python
from db.chat_history import init_db, save_message, get_history

# Initialize database (creates tables if needed)
init_db()

# Save messages
save_message("user_123", "user", "Hello, I need legal advice")
save_message("user_123", "assistant", "I'm here to help. What happened?")

# Retrieve history
history = get_history("user_123", limit=50)
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

### Using multiple databases (providers)

```python
from db.chat_history import register_provider, init_db, save_message, get_history
from db.db_provider import SQLiteProvider

# Create and register a test database provider
test_provider = SQLiteProvider("d:/eggstech/data/test_chat.db")
register_provider("test", test_provider, make_default=False)

# Use the test provider for specific operations
init_db(provider="test")
save_message("user_456", "user", "Test message", provider="test")
history = get_history("user_456", provider="test")

# Or use explicit path (creates temporary provider)
save_message("user_789", "user", "Message", db_path="d:/temp/other.db")
```

### Switching default provider

```python
from db.chat_history import set_default_provider, list_providers

# List all registered providers
providers = list_providers()
print(providers)
# Output: {'default': {'type': 'sqlite', 'db_path': '...', 'exists': True},
#          'test': {'type': 'sqlite', 'db_path': '...', 'exists': False}}

# Switch default provider
set_default_provider("test")

# Now all operations without explicit provider use 'test'
save_message("user_123", "user", "Goes to test DB")
```

## DBProvider Class Usage

### Creating providers directly

```python
from db.db_provider import SQLiteProvider, create_sqlite_provider

# Method 1: Direct instantiation
provider1 = SQLiteProvider("d:/data/my_db.sqlite")

# Method 2: Factory function
provider2 = create_sqlite_provider("d:/data/my_db.sqlite", auto_create_dir=True)

# Use provider methods directly
provider1.execute("CREATE TABLE test (id INTEGER, name TEXT)")
provider1.execute("INSERT INTO test VALUES (?, ?)", (1, "Alice"))
row = provider1.fetch_one("SELECT * FROM test WHERE id = ?", (1,))
print(row)  # (1, 'Alice')
```

### Context manager support

```python
from db.db_provider import SQLiteProvider

with SQLiteProvider("d:/data/my_db.sqlite") as provider:
    provider.execute("INSERT INTO test VALUES (?, ?)", (2, "Bob"))
    rows = provider.fetch_all("SELECT * FROM test")
    print(rows)
# Connection automatically closed after context exit
```

### Connection info and debugging

```python
provider = SQLiteProvider("d:/data/my_db.sqlite")
info = provider.get_connection_info()
print(info)
# Output: {'type': 'sqlite', 'db_path': 'd:/data/my_db.sqlite', 'exists': True}
```

## Session State Management

```python
from db.chat_history import get_session_state, set_session_state

# Get current session state
state = get_session_state("user_123")
print(state)
# {'user_id': 'user_123', 'state': None, 'incident_type': None,
#  'emotion': None, 'updated_at': None}

# Update session state
set_session_state(
    "user_123",
    state="calm",
    incident_type="civil",
    emotion="neutral"
)

# Retrieve updated state
state = get_session_state("user_123")
print(state['emotion'])  # 'neutral'
```

## API Reference

### chat_history.py

#### Provider Management

- `register_provider(name, provider, make_default=False)` - Register a DBProvider instance
- `list_providers()` - Get info about all registered providers
- `set_default_provider(name)` - Switch default provider
- `get_default_provider()` - Get current default provider name

#### Database Operations

- `init_db(db_path=None, provider=None)` - Create tables if needed
- `save_message(user_id, role, content, db_path=None, provider=None)` - Save a message
- `get_history(user_id, limit=100, db_path=None, provider=None)` - Get conversation history
- `get_session_state(user_id, db_path=None, provider=None)` - Get user session state
- `set_session_state(user_id, state=None, incident_type=None, emotion=None, db_path=None, provider=None)` - Update session state

### db_provider.py

#### Abstract Base Class

- `DBProvider` - Abstract base class defining the provider interface

#### Concrete Providers

- `SQLiteProvider(db_path, auto_create_dir=True)` - SQLite implementation (ready to use)
- `PostgreSQLProvider(...)` - PostgreSQL implementation (placeholder, not yet implemented)
- `MySQLProvider(...)` - MySQL implementation (placeholder, not yet implemented)

#### Factory Functions

- `create_sqlite_provider(db_path, auto_create_dir=True)` - Create SQLite provider
- `create_provider_from_config(config)` - Create provider from config dict

## Extending to Other Databases

To add support for PostgreSQL or MySQL:

1. Install the required driver:

   ```powershell
   pip install psycopg2-binary  # For PostgreSQL
   # or
   pip install mysql-connector-python  # For MySQL
   ```

2. Implement the provider class in `db_provider.py` (follow the `DBProvider` interface)

3. Use it the same way:

   ```python
   from db.db_provider import PostgreSQLProvider
   from db.chat_history import register_provider

   pg_provider = PostgreSQLProvider(
       host="localhost",
       port=5432,
       database="chat_db",
       user="admin",
       password="secret"
   )
   register_provider("postgres", pg_provider, make_default=True)
   ```

## Best Practices

1. **Use named providers for different environments:**

   ```python
   register_provider("dev", SQLiteProvider("data/dev.db"))
   register_provider("test", SQLiteProvider("data/test.db"))
   register_provider("prod", SQLiteProvider("data/prod.db"))
   ```

2. **Always initialize the database before first use:**

   ```python
   init_db()  # or init_db(provider="test")
   ```

3. **Use explicit providers for multi-tenant scenarios:**

   ```python
   # Each tenant gets their own provider
   for tenant in tenants:
       provider = SQLiteProvider(f"data/{tenant}_chat.db")
       register_provider(tenant, provider)
       init_db(provider=tenant)
   ```

4. **Close providers when done (if managing lifecycle manually):**
   ```python
   provider = SQLiteProvider("data/temp.db")
   try:
       provider.execute("...")
   finally:
       provider.close()
   ```

## Migration Notes

If you have existing code using direct sqlite3 connections, all operations remain backward compatible:

```python
# Old code (still works)
from db.chat_history import save_message, get_history
save_message("user_1", "user", "Hello")
history = get_history("user_1")

# New code (provider-aware)
save_message("user_1", "user", "Hello", provider="test")
history = get_history("user_1", provider="test")
```

The default provider is automatically initialized on module import, so existing code continues to work without changes.
