"""Base tool definitions and registry."""

from typing import Dict, Any, Callable, Optional
from pydantic import BaseModel


class Tool(BaseModel):
    """Tool definition for LLM integration."""
    name: str
    description: str
    parameters: Dict[str, Any]
    requires_confirmation: bool = True
    handler: Optional[Callable] = None
    
    class Config:
        arbitrary_types_allowed = True


class ToolCall(BaseModel):
    """A tool call request from the LLM."""
    tool_name: str
    arguments: Dict[str, Any]


class ToolRegistry:
    """Registry for available tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._handlers: Dict[str, Callable] = {}
    
    def register(self, tool: Tool, handler: Callable):
        """Register a tool with its handler."""
        self._tools[tool.name] = tool
        self._handlers[tool.name] = handler
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_handler(self, name: str) -> Optional[Callable]:
        """Get a tool's handler by name."""
        return self._handlers.get(name)
    
    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def get_schemas(self) -> list[Dict[str, Any]]:
        """Get OpenAI-compatible tool schemas for all registered tools."""
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            })
        return schemas


# Global registry instance
registry = ToolRegistry()
