"""Urpe Agent CLI - Typer commands."""

import asyncio
import os

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from typing_extensions import Annotated

from urpe.config import load_settings
from urpe.agent import Agent
from urpe.memory import memory
from urpe.tools import registry

console = Console()
app = typer.Typer(help="Urpe AI Agent CLI")


def run_async(coro):
    """Helper to run async functions in sync context."""
    return asyncio.get_event_loop().run_until_complete(coro)


@app.command()
def chat(
    model: Annotated[str, typer.Option(help="LLM model to use")] = None,
    no_tools: Annotated[bool, typer.Option("--no-tools", help="Disable tool usage")] = False,
):
    """
    Start an interactive chat session with the Urpe agent.
    """
    settings = load_settings(os.getenv("URPE_CONFIG_PATH"))
    
    if not settings.gemini_api_key:
        console.print("[bold red]Error:[/bold red] GEMINI_API_KEY environment variable not set.")
        raise typer.Exit(1)
    
    model = model or settings.default_model
    agent = Agent(model=model, enable_tools=not no_tools)
    agent.start_conversation()
    
    console.print(f"[bold green]Urpe Agent[/bold green] - Model: [cyan]{model}[/cyan]")
    console.print(f"Tools: {'[red]disabled[/red]' if no_tools else '[green]enabled[/green]'}")
    console.print("[dim]Type 'exit' or 'quit' to end the session.[/dim]\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
            
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break
            
            if not user_input.strip():
                continue
            
            console.print("[bold green]Agent[/bold green]: ", end="")
            
            async def stream_response():
                full_response = ""
                async for chunk in agent.process_message(user_input):
                    console.print(chunk, end="")
                    full_response += chunk
                return full_response
            
            run_async(stream_response())
            console.print("\n")
            
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Type 'exit' to quit.[/dim]")


@app.command()
def ask(
    question: Annotated[str, typer.Argument(help="Question to ask the Urpe agent")],
    model: Annotated[str, typer.Option(help="LLM model to use")] = None,
    no_tools: Annotated[bool, typer.Option("--no-tools", help="Disable tool usage")] = False,
):
    """
    Ask the Urpe agent a one-shot question.
    """
    settings = load_settings(os.getenv("URPE_CONFIG_PATH"))
    
    if not settings.gemini_api_key:
        console.print("[bold red]Error:[/bold red] GEMINI_API_KEY environment variable not set.")
        raise typer.Exit(1)
    
    model = model or settings.default_model
    agent = Agent(model=model, enable_tools=not no_tools)
    
    with console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
        async def get_response():
            full_response = ""
            async for chunk in agent.process_message(question):
                full_response += chunk
            return full_response
        
        response = run_async(get_response())
    
    console.print(Markdown(response))


@app.command()
def history(
    limit: Annotated[int, typer.Option(help="Number of conversations to show")] = 10,
    conversation_id: Annotated[str, typer.Option("--id", help="Show messages for a specific conversation ID")] = None,
):
    """
    View past conversations.
    """
    if conversation_id:
        conv = memory.get_conversation(conversation_id)
        if not conv:
            console.print(f"[red]Conversation not found: {conversation_id}[/red]")
            raise typer.Exit(1)
        
        console.print(f"[bold]Conversation:[/bold] {conv['id']}")
        console.print(f"[dim]Created: {conv['created_at']} | Model: {conv['model']}[/dim]\n")
        
        for msg in conv["messages"]:
            role_color = {"user": "blue", "assistant": "green", "tool": "yellow"}.get(msg["role"], "white")
            console.print(f"[bold {role_color}]{msg['role'].upper()}[/bold {role_color}]: {msg['content']}\n")
    else:
        conversations = memory.get_conversations(limit=limit)
        
        if not conversations:
            console.print("[dim]No conversations found.[/dim]")
            return
        
        console.print(f"[bold]Recent Conversations[/bold] (last {limit}):\n")
        
        for conv in conversations:
            console.print(f"  [cyan]{conv['id'][:8]}...[/cyan] | {conv['created_at'][:10]} | {conv['message_count']} messages | {conv['model'] or 'default'}")


@app.command()
def tools():
    """
    List available tools.
    """
    tool_list = registry.list_tools()
    
    if not tool_list:
        console.print("[dim]No tools registered.[/dim]")
        return
    
    console.print("[bold]Available Tools:[/bold]\n")
    
    for tool in tool_list:
        confirm_badge = "[yellow]! requires confirmation[/yellow]" if tool.requires_confirmation else "[green]* auto[/green]"
        console.print(f"  [cyan]{tool.name}[/cyan] {confirm_badge}")
        console.print(f"    {tool.description}\n")


if __name__ == "__main__":
    app()
