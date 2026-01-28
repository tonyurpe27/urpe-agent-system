"""Tools module - executable functions for the agent."""

from urpe.tools.base import Tool, ToolCall, ToolRegistry, registry
from urpe.tools.shell import run_command, SHELL_TOOL_SCHEMA, ToolResult

# Register built-in tools
_shell_tool = Tool(
    name="run_command",
    description="Execute a shell command on the local system. Requires user confirmation.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute"
            }
        },
        "required": ["command"]
    },
    requires_confirmation=True,
)
registry.register(_shell_tool, run_command)

__all__ = [
    "Tool",
    "ToolCall", 
    "ToolResult",
    "ToolRegistry",
    "registry",
    "run_command",
    "SHELL_TOOL_SCHEMA",
]
