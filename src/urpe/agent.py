"""Core agent loop with tool calling support."""

import json
from typing import List, Dict, Any, Optional, AsyncGenerator

from rich.console import Console

from urpe.llm import get_llm_response
from urpe.tools import registry, ToolResult
from urpe.memory import memory
from urpe.config import settings

console = Console()


class Agent:
    """AI Agent with tool calling and memory."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        enable_tools: bool = True,
    ):
        self.model = model or settings.default_model
        self.enable_tools = enable_tools
        self.conversation_id: Optional[str] = None
    
    def start_conversation(self) -> str:
        """Start a new conversation and return its ID."""
        self.conversation_id = memory.create_conversation(model=self.model)
        return self.conversation_id
    
    def _get_tools_schema(self) -> Optional[List[Dict[str, Any]]]:
        """Get tool schemas if tools are enabled."""
        if not self.enable_tools:
            return None
        return registry.get_schemas()
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool and return its result."""
        handler = registry.get_handler(tool_name)
        if not handler:
            return ToolResult(
                success=False,
                output="",
                error=f"Unknown tool: {tool_name}"
            )
        
        try:
            # Handle both sync and async handlers
            result = handler(**arguments)
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )
    
    async def process_message(
        self,
        user_message: str,
        stream: bool = True,
    ) -> AsyncGenerator[str, None]:
        """
        Process a user message and yield response chunks.
        
        Handles tool calls in a loop until the model produces a final response.
        """
        if not self.conversation_id:
            self.start_conversation()
        
        # Save user message
        memory.add_message(self.conversation_id, "user", user_message)
        
        # Get conversation history
        messages = memory.get_messages(self.conversation_id)
        
        # Convert to LiteLLM format
        llm_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        tools = self._get_tools_schema()
        
        while True:
            # Call LLM
            response = await get_llm_response(
                model=self.model,
                messages=llm_messages,
                tools=tools,
            )
            
            full_content = ""
            tool_calls = []
            
            # Process streaming response
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    
                    # Accumulate content
                    if delta.content:
                        full_content += delta.content
                        yield delta.content
                    
                    # Accumulate tool calls
                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            if tc.index >= len(tool_calls):
                                tool_calls.append({
                                    "id": tc.id,
                                    "name": tc.function.name if tc.function else "",
                                    "arguments": ""
                                })
                            if tc.function and tc.function.arguments:
                                tool_calls[tc.index]["arguments"] += tc.function.arguments
            
            # If no tool calls, we're done
            if not tool_calls:
                # Save assistant response
                memory.add_message(self.conversation_id, "assistant", full_content)
                break
            
            # Process tool calls
            memory.add_message(
                self.conversation_id,
                "assistant",
                full_content,
                tool_calls=tool_calls
            )
            
            for tc in tool_calls:
                try:
                    args = json.loads(tc["arguments"])
                except json.JSONDecodeError:
                    args = {}
                
                yield f"\n[Tool: {tc['name']}]\n"
                
                result = self._execute_tool(tc["name"], args)
                
                # Add tool result to messages
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result.output if result.success else f"Error: {result.error}"
                }
                llm_messages.append(tool_message)
                memory.add_message(
                    self.conversation_id,
                    "tool",
                    tool_message["content"]
                )
                
                yield f"{tool_message['content']}\n"
            
            # Continue loop to get model's response to tool results
