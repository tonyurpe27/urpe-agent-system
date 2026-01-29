"""Shell command execution tool with human-in-the-loop confirmation."""

import subprocess
import shlex
from typing import Optional

from pydantic import BaseModel, Field
from rich.console import Console
from rich.prompt import Confirm

console = Console()


class ToolResult(BaseModel):
    """Result of a tool execution."""
    success: bool
    output: str
    error: Optional[str] = None


def run_command(
    command: str,
    require_confirmation: bool = True,
    timeout: int = 30,
) -> ToolResult:
    """
    Execute a shell command with optional human confirmation.
    
    Args:
        command: The shell command to execute
        require_confirmation: Whether to ask user before executing
        timeout: Maximum seconds to wait for command completion
    
    Returns:
        ToolResult with success status and output/error
    """
    if require_confirmation:
        console.print(f"\n[bold yellow]Tool Request:[/bold yellow] run_command")
        console.print(f"[dim]Command:[/dim] [cyan]{command}[/cyan]")
        
        if not Confirm.ask("[bold]Allow execution?[/bold]", default=False):
            return ToolResult(
                success=False,
                output="",
                error="User denied execution"
            )
    
    try:
        import sys
        # Use cmd /c on Windows to avoid shell=True permission issues
        if sys.platform == "win32":
            result = subprocess.run(
                ["cmd", "/c", command],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        
        output = result.stdout
        error = result.stderr if result.returncode != 0 else None
        
        return ToolResult(
            success=result.returncode == 0,
            output=output,
            error=error,
        )
        
    except subprocess.TimeoutExpired:
        return ToolResult(
            success=False,
            output="",
            error=f"Command timed out after {timeout} seconds"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            output="",
            error=str(e)
        )


# Tool schema for LLM
SHELL_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": "Execute a shell command on the local system. Requires user confirmation before execution.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute"
                }
            },
            "required": ["command"]
        }
    }
}
