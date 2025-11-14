"""
Example script demonstrating the DBProvider system.

Run this to see how to use multiple database providers and switch between them.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db.chat_history import (
    init_db,
    save_message,
    get_history,
    set_session_state,
    get_session_state,
    register_provider,
    set_default_provider,
    list_providers,
)
from db.db_provider import SQLiteProvider


def demo_basic_usage():
    """Demo 1: Basic usage with default provider."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Usage (Default Provider)")
    print("="*60)
    
    # Initialize default database
    db_path = init_db()
    print(f"✓ Initialized database at: {db_path}")
    
    # Save some messages
    save_message("user_demo1", "user", "Tôi cần tư vấn pháp lý về hợp đồng.")
    save_message("user_demo1", "assistant", "Tôi có thể giúp bạn. Bạn có thể mô tả vấn đề chi tiết hơn không?")
    print("✓ Saved 2 messages")
    
    # Retrieve history
    history = get_history("user_demo1", limit=10)
    print(f"✓ Retrieved {len(history)} messages:")
    for msg in history:
        print(f"  [{msg['role']}]: {msg['content'][:50]}...")
    
    # Session state
    set_session_state("user_demo1", state="calm", emotion="neutral", incident_type="civil")
    state = get_session_state("user_demo1")
    print(f"✓ Session state: emotion={state['emotion']}, incident={state['incident_type']}")


def demo_multiple_providers():
    """Demo 2: Using multiple providers."""
    print("\n" + "="*60)
    print("DEMO 2: Multiple Providers")
    print("="*60)
    
    # Create a test provider
    test_db_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_demo.db")
    test_provider = SQLiteProvider(test_db_path)
    register_provider("test", test_provider)
    print(f"✓ Registered 'test' provider at: {test_db_path}")
    
    # Initialize test database
    init_db(provider="test")
    print("✓ Initialized test database")
    
    # Save messages to test DB
    save_message("user_test", "user", "This is a test message", provider="test")
    save_message("user_test", "assistant", "Test reply", provider="test")
    print("✓ Saved messages to test provider")
    
    # Retrieve from test DB
    history = get_history("user_test", provider="test")
    print(f"✓ Retrieved {len(history)} messages from test DB")
    
    # List all providers
    providers = list_providers()
    print(f"✓ Available providers: {list(providers.keys())}")
    for name, info in providers.items():
        print(f"  - {name}: {info['type']} ({info.get('db_path', 'N/A')})")


def demo_provider_switching():
    """Demo 3: Switching default provider."""
    print("\n" + "="*60)
    print("DEMO 3: Switching Default Provider")
    print("="*60)
    
    # Create production and staging providers
    prod_provider = SQLiteProvider(os.path.join(os.path.dirname(__file__), "..", "data", "prod_demo.db"))
    staging_provider = SQLiteProvider(os.path.join(os.path.dirname(__file__), "..", "data", "staging_demo.db"))
    
    register_provider("production", prod_provider)
    register_provider("staging", staging_provider)
    print("✓ Registered 'production' and 'staging' providers")
    
    # Initialize both
    init_db(provider="production")
    init_db(provider="staging")
    print("✓ Initialized both databases")
    
    # Use staging
    set_default_provider("staging")
    print("✓ Switched to 'staging' as default")
    save_message("user_stg", "user", "Staging message (no provider specified)")
    history = get_history("user_stg")
    print(f"✓ Saved and retrieved from staging (implicit): {len(history)} messages")
    
    # Use production explicitly
    save_message("user_prod", "user", "Production message", provider="production")
    history = get_history("user_prod", provider="production")
    print(f"✓ Saved and retrieved from production (explicit): {len(history)} messages")
    
    # Switch back to default
    set_default_provider("default")
    print("✓ Switched back to 'default' provider")


def demo_explicit_path():
    """Demo 4: Using explicit path (no registration needed)."""
    print("\n" + "="*60)
    print("DEMO 4: Explicit Path (Ad-hoc Provider)")
    print("="*60)
    
    temp_db = os.path.join(os.path.dirname(__file__), "..", "data", "temp_adhoc.db")
    
    # Use explicit path without registering
    init_db(db_path=temp_db)
    save_message("user_adhoc", "user", "Ad-hoc message", db_path=temp_db)
    history = get_history("user_adhoc", db_path=temp_db)
    
    print(f"✓ Used ad-hoc DB at: {temp_db}")
    print(f"✓ Saved and retrieved {len(history)} messages without provider registration")


def demo_session_workflow():
    """Demo 5: Complete session workflow with emotion tracking."""
    print("\n" + "="*60)
    print("DEMO 5: Session Workflow with Emotion Tracking")
    print("="*60)
    
    user_id = "user_workflow"
    
    # Simulate angry user
    save_message(user_id, "user", "Tôi rất giận! Họ lừa đảo tôi!")
    set_session_state(user_id, state="charged", emotion="angry", incident_type="fraud")
    state = get_session_state(user_id)
    print(f"✓ User angry - State: {state['state']}, Emotion: {state['emotion']}")
    
    # Assistant response
    save_message(user_id, "assistant", "Tôi hiểu bạn đang rất giận. Bạn có an toàn không?")
    
    # User calms down
    save_message(user_id, "user", "Tôi bình tĩnh hơn rồi. Tôi cần làm gì?")
    set_session_state(user_id, state="calm", emotion="calm", incident_type="fraud")
    state = get_session_state(user_id)
    print(f"✓ User calmed - State: {state['state']}, Emotion: {state['emotion']}")
    
    # Show full history
    history = get_history(user_id)
    print(f"✓ Full conversation history ({len(history)} messages):")
    for i, msg in enumerate(history, 1):
        print(f"  {i}. [{msg['role']}]: {msg['content']}")


def main():
    """Run all demos."""
    print("\n" + "🔷"*30)
    print("DATABASE PROVIDER SYSTEM - DEMONSTRATION")
    print("🔷"*30)
    
    try:
        demo_basic_usage()
        demo_multiple_providers()
        demo_provider_switching()
        demo_explicit_path()
        demo_session_workflow()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nCheck the 'd:/eggstech/data/' folder to see the created database files.")
        print("Each demo created separate database files to show isolation.\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
