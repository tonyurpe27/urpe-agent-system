"""Tests for agent module."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from urpe.agent import Agent
from urpe.config import Settings


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("urpe.agent.settings") as mock:
        mock.default_model = "test-model"
        mock.gemini_api_key = "test-key"
        yield mock


@pytest.fixture
def agent(mock_settings):
    """Create an agent for testing."""
    return Agent(model="test-model", enable_tools=True)


def test_agent_init(mock_settings):
    """Test agent initialization."""
    agent = Agent(model="custom-model", enable_tools=False)
    
    assert agent.model == "custom-model"
    assert agent.enable_tools is False
    assert agent.conversation_id is None


def test_agent_default_model(mock_settings):
    """Test agent uses default model from settings."""
    agent = Agent()
    
    assert agent.model == "test-model"


def test_start_conversation(agent):
    """Test starting a new conversation."""
    with patch("urpe.agent.memory") as mock_memory:
        mock_memory.create_conversation.return_value = "test-conv-id"
        
        conv_id = agent.start_conversation()
        
        assert conv_id == "test-conv-id"
        assert agent.conversation_id == "test-conv-id"
        mock_memory.create_conversation.assert_called_once()


def test_get_tools_schema_enabled(agent):
    """Test getting tool schemas when tools enabled."""
    schemas = agent._get_tools_schema()
    
    assert schemas is not None
    assert len(schemas) >= 1


def test_get_tools_schema_disabled(mock_settings):
    """Test getting tool schemas when tools disabled."""
    agent = Agent(enable_tools=False)
    schemas = agent._get_tools_schema()
    
    assert schemas is None
