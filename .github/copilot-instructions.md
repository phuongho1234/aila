# AI Coding Agent Instructions

## Project Overview
This is a **Vietnamese legal counseling chatbot** that uses OpenAI's API to provide empathetic psychological support and legal guidance. The system stores conversation history in SQLite using a flexible provider pattern for potential multi-database support.

## Architecture

### Database Layer (`db/`)
**Provider Pattern**: All database operations go through `DBProvider` abstract base class
- `db_provider.py`: Abstract `DBProvider` + concrete `SQLiteProvider` (PostgreSQL/MySQL stubs exist)
- `chat_history.py`: High-level API with provider registry (`_PROVIDERS` dict, `_DEFAULT_PROVIDER`)
- Default provider auto-initialized at module import: `d:/eggstech/data/chat_history.db`

**Key Pattern**: 3 ways to specify database in any operation:
```python
save_message("user1", "user", "text")  # Uses default provider
save_message("user1", "user", "text", provider="test")  # Uses named registered provider
save_message("user1", "user", "text", db_path="/custom/path.db")  # Creates temp provider
```

**Session State**: Each user has optional `state`, `emotion`, `incident_type` fields (see `get_session_state`/`set_session_state`)

### Notebook Import Workaround (CRITICAL)
**Problem**: Name collision between local `db/` package and installed `db` package in site-packages

**Solution Pattern** (used in `main.ipynb`, `main_2.ipynb`, `scripts/init_db.py`):
```python
import importlib.util, os
PROJECT_ROOT = os.path.abspath(os.getcwd())  # or dirname(__file__) for scripts
module_path = os.path.join(PROJECT_ROOT, 'db', 'chat_history.py')
spec = importlib.util.spec_from_file_location('local_chat_history', module_path)
local_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local_db)
# Now use: local_db.init_db(), local_db.save_message(), etc.
```

**Always use this pattern** when importing `db` module in notebooks or scripts. Standard `from db import ...` will fail.

### OpenAI Integration (`main.ipynb`, `main_2.ipynb`)
- Model: `gpt-5-mini` (configurable via `MODEL` constant)
- API key loaded from `.env` file (`OPENAI_API_KEY`)
- System prompt in `SYSTEM_PROMPT` defines counselor personality (warm, empathetic, Vietnamese-focused)

**Conversation Pattern**:
1. Save user message: `save_message(user_id, "user", text)`
2. Retrieve history: `get_history(user_id, limit=100)`
3. Build messages: `[{"role": "system", "content": SYSTEM_PROMPT}, ...history]`
4. Optional: Inject session memory (concatenated prior user messages) as system note
5. Call OpenAI API
6. Save assistant response: `save_message(user_id, "assistant", response)`

## Database Schema
```sql
-- messages table (in chat_history.py:init_db)
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- session_state table
CREATE TABLE session_state (
    user_id TEXT PRIMARY KEY,
    state TEXT,
    incident_type TEXT,
    emotion TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Key APIs

### High-Level Database API (from `db.chat_history`)
- `init_db(db_path=None, provider=None)` → str: Create tables, return path
- `save_message(user_id, role, content, db_path=None, provider=None)`: Store message
- `get_history(user_id, limit=100, db_path=None, provider=None)` → List[Dict]: Chronological messages
- `get_session_state(user_id, ...)` → Dict: Returns `{"state": ..., "emotion": ..., "incident_type": ...}`
- `set_session_state(user_id, state=None, emotion=None, incident_type=None, ...)`

### Provider Management
- `register_provider(name, provider, make_default=False)`: Register named DBProvider
- `list_providers()` → Dict: Show all registered providers with metadata
- `set_default_provider(name)`: Switch default provider globally

### Low-Level Provider API (`db.db_provider.DBProvider`)
- `execute(query, params)`: INSERT/UPDATE/DELETE/CREATE
- `fetch_one(query, params)` → Optional[Tuple]
- `fetch_all(query, params)` → List[Tuple]
- Context manager: `with provider: ...` (auto-cleanup)

## Development Workflows

### Running Notebooks
- Use VS Code with Jupyter extension
- Execute `main.ipynb` or `main_2.ipynb` cells sequentially
- **First cell always loads DB module** using `importlib.util` pattern

### Initializing Database
```bash
# From project root
python scripts/init_db.py
# Or custom path:
python scripts/init_db.py --db d:/custom/path.db
```

### Testing Provider System
Run examples: `python db/example_provider_usage.py`
- Demo 1: Basic default provider
- Demo 2: Multiple providers (test, production, staging)
- Demo 3: Provider switching
- Demo 4: Direct provider usage
- Demo 5: Error handling

## Project Conventions

### File Organization
- `data/`: SQLite database files (`.db` extension)
- `db/`: Database abstraction layer (package with `__init__.py`)
- `scripts/`: Utility scripts (DB init, etc.)
- Root: Jupyter notebooks (`main.ipynb`, `main_2.ipynb`)

### Code Style
- Type hints used extensively (Python 3.7+ `typing` module)
- Docstrings follow Google style (Args, Returns, Example sections)
- Optional parameters: `db_path` and `provider` consistently last in signatures

### Naming Conventions
- Provider names: lowercase strings (`"default"`, `"test"`, `"production"`)
- User IDs: arbitrary strings, typically `"user_123"` format
- Roles: `"user"` or `"assistant"` (stored in messages table)

## Common Pitfalls

1. **Import Errors**: Always use `importlib.util` workaround in notebooks/scripts
2. **Provider Not Registered**: Call `register_provider()` before using named provider
3. **Missing Tables**: Always call `init_db()` before first use of a database
4. **Path Issues**: Use absolute paths or ensure `PROJECT_ROOT` is correctly set
5. **Context Manager**: When using providers directly, prefer `with provider:` to avoid connection leaks

## Extension Points

### Adding New Database Backend
1. Subclass `DBProvider` in `db_provider.py`
2. Implement abstract methods: `connect`, `close`, `get_connection`, `execute`, `fetch_one`, `fetch_all`, `get_connection_info`
3. Add factory function (e.g., `create_postgres_provider`)
4. Update `create_provider_from_config` switch statement

### Adding Session Fields
Modify `session_state` table in `chat_history.py:init_db()`, then update `get_session_state`/`set_session_state` signatures and queries.

## Vietnamese Language Support
- All user-facing prompts and messages support Vietnamese (UTF-8)
- System prompt specifically tailored for Vietnamese legal/psychological context
- Database stores UTF-8 text natively (SQLite TEXT type)
