import argparse
import os
import sys
import importlib.util


# Ensure project root is first on sys.path so local `db` package is preferred
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _import_local_init_db():
    """Import `init_db` from the local `db/chat_history.py` reliably.

    This avoids name collisions with a third-party `db` package installed in site-packages.
    """
    try:
        # Normal import should work now that PROJECT_ROOT is on sys.path
        from db.chat_history import init_db as _init_db
        return _init_db
    except Exception:
        # Fallback: load the module directly from file path
        path = os.path.join(PROJECT_ROOT, "db", "chat_history.py")
        spec = importlib.util.spec_from_file_location("db.chat_history", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.init_db


def main():
    parser = argparse.ArgumentParser(description="Initialize the chat history SQLite database.")
    parser.add_argument("--db", dest="db", help="Path to sqlite db file (optional)", default=None)
    args = parser.parse_args()
    init_db = _import_local_init_db()
    db_path = init_db(args.db)
    print(f"Initialized chat history DB at: {db_path}")


if __name__ == "__main__":
    main()
