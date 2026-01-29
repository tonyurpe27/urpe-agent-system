"""Tests for memory module."""

import pytest
import tempfile
import os

from urpe.memory.sqlite import MemoryStore


@pytest.fixture
def memory_store():
    """Create a temporary memory store for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        store = MemoryStore(db_path=db_path)
        yield store
        store.close()  # Close SQLite connection before cleanup (Windows requires this)


def test_create_conversation(memory_store):
    """Test creating a new conversation."""
    conv_id = memory_store.create_conversation(model="test-model")
    
    assert conv_id is not None
    assert len(conv_id) > 0


def test_add_and_get_messages(memory_store):
    """Test adding and retrieving messages."""
    conv_id = memory_store.create_conversation()
    
    memory_store.add_message(conv_id, "user", "Hello!")
    memory_store.add_message(conv_id, "assistant", "Hi there!")
    
    messages = memory_store.get_messages(conv_id)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello!"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there!"


def test_add_message_with_tool_calls(memory_store):
    """Test adding messages with tool calls."""
    conv_id = memory_store.create_conversation()
    
    tool_calls = [{"name": "run_command", "arguments": {"command": "ls"}}]
    memory_store.add_message(conv_id, "assistant", "", tool_calls=tool_calls)
    
    messages = memory_store.get_messages(conv_id)
    
    assert len(messages) == 1
    assert messages[0]["tool_calls"] == tool_calls


def test_get_conversations(memory_store):
    """Test listing conversations."""
    memory_store.create_conversation(model="model-1")
    memory_store.create_conversation(model="model-2")
    
    convs = memory_store.get_conversations(limit=10)
    
    assert len(convs) == 2


def test_get_conversation_by_id(memory_store):
    """Test getting a specific conversation."""
    conv_id = memory_store.create_conversation(model="test-model")
    memory_store.add_message(conv_id, "user", "Test message")
    
    conv = memory_store.get_conversation(conv_id)
    
    assert conv is not None
    assert conv["id"] == conv_id
    assert conv["model"] == "test-model"
    assert len(conv["messages"]) == 1


def test_get_nonexistent_conversation(memory_store):
    """Test getting a conversation that doesn't exist."""
    conv = memory_store.get_conversation("nonexistent-id")
    
    assert conv is None
