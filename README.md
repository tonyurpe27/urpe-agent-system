# urpe-agent-system

A modular CLI AI agent with conversational memory and tool use. Built for [Urpe AI Lab](https://urpeailab.com).

## Features

- 🤖 **Conversational AI** - Chat mode with context retention
- 🔧 **Tool Use** - Execute shell commands with human-in-the-loop confirmation
- 💾 **Persistent Memory** - SQLite-backed conversation history
- ⚡ **Fast** - Uses Gemini 2.0 Flash via LiteLLM
- 🎨 **Beautiful CLI** - Rich output with spinners, markdown, and colors

## Installation

```bash
# Clone the repo
git clone https://github.com/tonyurpe27/urpe-agent-system.git
cd urpe-agent-system

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

## Configuration

Set your Gemini API key:

```bash
export GEMINI_API_KEY=your_api_key_here
```

Or create a `config.yaml`:

```yaml
model: gemini/gemini-2.0-flash
```

## Usage

### Interactive Chat

```bash
urpe chat
```

### One-shot Question

```bash
urpe ask "What's the weather like today?"
```

### View History

```bash
urpe history
urpe history --limit 10
```

### List Available Tools

```bash
urpe tools
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Typer     │────▶│   Agent     │────▶│   LiteLLM   │
│    CLI      │     │    Core     │     │   (Gemini)  │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │  Tools  │ │ Memory  │ │ Config  │
        │ (shell) │ │(SQLite) │ │ (YAML)  │
        └─────────┘ └─────────┘ └─────────┘
```

## Tools

### `run_command`

Executes shell commands with user confirmation (human-in-the-loop).

```
Agent: I'll check the current directory.
Tool: run_command("ls -la")
Confirm? [y/N]: y
Output: drwxr-xr-x  5 user  staff  160 Jan 28 10:00 .
...
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src
```

## Project Structure

```
urpe-agent-system/
├── src/urpe/
│   ├── cli.py        # Typer commands
│   ├── agent.py      # Core loop
│   ├── llm.py        # LiteLLM wrapper
│   ├── config.py     # Settings
│   ├── tools/
│   │   ├── base.py   # Tool base class
│   │   └── shell.py  # run_command tool
│   └── memory/
│       └── sqlite.py # SQLAlchemy models
├── tests/
├── config.yaml
├── PLAN.md           # Future roadmap
└── SPEC.md           # Technical spec
```

## Roadmap

- [x] MVP CLI with chat, ask, history, tools
- [x] Human-in-the-loop tool confirmation
- [x] SQLite memory persistence
- [ ] Skills system (plugin architecture)
- [ ] MCP protocol support
- [ ] Sub-agents
- [ ] RAG/vector memory

## License

MIT

## Credits

Built by [Urpe AI Lab](https://urpeailab.com) 🧪
