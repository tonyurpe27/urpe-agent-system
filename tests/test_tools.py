"""Tests for tools module."""

import pytest
from unittest.mock import patch, MagicMock

from urpe.tools import registry, run_command, ToolResult
from urpe.tools.base import Tool


def test_run_command_success_no_confirmation():
    """Test successful command execution without confirmation."""
    result = run_command("echo hello", require_confirmation=False)
    
    assert result.success is True
    assert "hello" in result.output
    assert result.error is None


def test_run_command_failure_no_confirmation():
    """Test failed command execution."""
    result = run_command("nonexistent_command_12345", require_confirmation=False)
    
    assert result.success is False


def test_run_command_timeout():
    """Test command timeout."""
    # This should timeout on Windows
    result = run_command("ping -n 10 localhost", require_confirmation=False, timeout=1)
    
    assert result.success is False
    assert "timed out" in result.error.lower()


@patch("urpe.tools.shell.Confirm.ask")
def test_run_command_user_denies(mock_confirm):
    """Test user denying command execution."""
    mock_confirm.return_value = False
    
    result = run_command("echo test", require_confirmation=True)
    
    assert result.success is False
    assert "denied" in result.error.lower()


def test_registry_list_tools():
    """Test tool registry listing."""
    tools = registry.list_tools()
    
    assert len(tools) >= 1
    assert any(t.name == "run_command" for t in tools)


def test_registry_get_schemas():
    """Test getting tool schemas for LLM."""
    schemas = registry.get_schemas()
    
    assert len(schemas) >= 1
    assert schemas[0]["type"] == "function"
    assert "name" in schemas[0]["function"]
