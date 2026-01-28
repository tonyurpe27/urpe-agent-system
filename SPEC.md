# PROJECT: urpe-agent-mvp

**Date**: 2026-01-28
**Author**: Bruno (delegated to Gemini CLI)
**Status**: In Progress

## GOAL

### What
CLI básica de agente AI con Typer + Rich que conecte a LLMs vía LiteLLM, con una tool simple que requiera confirmación del usuario, y memoria conversacional en SQLite.

### Why
MVP para validar la arquitectura del Urpe Agent System antes de agregar complejidad (MCP, skills, sub-agentes).

### Success Criteria
- [ ] CLI funcional con comando `urpe chat` que inicie conversación
- [ ] Integración LiteLLM funcionando con Gemini Flash
- [ ] Al menos 1 tool (ej: ejecutar comando shell) con confirmación human-in-the-loop
- [ ] Historial de conversación persistido en SQLite
- [ ] Tests unitarios pasando

## REQUIREMENTS

### Must Have (P0)
- Comando `urpe chat` para modo interactivo
- Comando `urpe ask "pregunta"` para one-shot
- Conexión a LLM vía LiteLLM (Gemini 2.0 Flash como default)
- Tool `run_command` que ejecute comandos shell con confirmación previa
- Memoria conversacional SQLite (guardar mensajes user/assistant)
- Output bonito con Rich (spinner, markdown, colores)

### Should Have (P1)
- Comando `urpe history` para ver conversaciones pasadas
- Config desde archivo YAML o env vars
- Streaming de respuestas

### Nice to Have (P2)
- Comando `urpe tools` para listar tools disponibles
- Export de conversación a markdown

### Out of Scope
- Skills system
- MCP protocol
- Sub-agentes
- Memoria vectorial/RAG
- Deploy/webhooks

## ARCHITECTURE

### Overview
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

### Components
| Component | Responsibility | Tech |
|-----------|---------------|------|
| CLI | User interface, commands | Typer + Rich |
| Agent Core | Orchestration, tool calling | Custom loop |
| LLM | Text generation | LiteLLM → Gemini |
| Tools | Executable functions | Pydantic schemas |
| Memory | Conversation persistence | SQLite + SQLAlchemy |
| Config | Settings management | YAML + Pydantic |

### Data Flow
1. User runs `urpe chat` or `urpe ask "..."`
2. CLI passes input to Agent Core
3. Agent loads conversation history from SQLite
4. Agent sends context + tools to LLM via LiteLLM
5. If LLM requests tool → prompt user for confirmation → execute → return result
6. Agent saves response to SQLite
7. CLI renders response with Rich

### Key Decisions
- **LiteLLM over direct SDK**: Abstracción multi-provider, fácil swap de modelos
- **SQLite over file**: Queries, integridad, escalable
- **Custom loop over LangChain**: Menos overhead, más control para MVP

## API

### CLI Commands

```bash
# Modo interactivo
urpe chat [--model MODEL] [--no-tools]

# One-shot
urpe ask "pregunta" [--model MODEL]

# Ver historial
urpe history [--limit N] [--conversation-id ID]

# Listar tools
urpe tools
```

### Tool Schema (internal)

```python
class Tool(BaseModel):
    name: str
    description: str
    parameters: dict  # JSON Schema
    requires_confirmation: bool = True
    
class ToolCall(BaseModel):
    tool_name: str
    arguments: dict
    
class ToolResult(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
```

### Database Schema

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model TEXT
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT REFERENCES conversations(id),
    role TEXT CHECK(role IN ('user', 'assistant', 'tool')),
    content TEXT,
    tool_calls TEXT,  -- JSON if assistant requested tools
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## TESTS

### Unit Tests
- [ ] Tool `run_command` returns correct output for simple command
- [ ] Tool `run_command` handles errors gracefully
- [ ] Memory saves and retrieves messages correctly
- [ ] Config loads from YAML and env vars
- [ ] Agent formats tool calls correctly for LLM

### Integration Tests
- [ ] Full chat flow: input → LLM → response → saved
- [ ] Tool flow: LLM requests tool → confirmation → execution → result back to LLM
- [ ] History retrieval shows correct messages

### Test Data
```python
# Valid tool call from LLM
{
    "tool_calls": [{
        "name": "run_command",
        "arguments": {"command": "echo hello"}
    }]
}

# Expected tool result
{
    "success": True,
    "output": "hello\n"
}
```

## CONSTRAINTS

### Technical
- **Language**: Python 3.11+
- **Package manager**: uv (fast, modern)
- **CLI**: Typer 0.9+
- **Output**: Rich
- **LLM**: LiteLLM (default model: gemini/gemini-2.0-flash)
- **Database**: SQLite via SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Config**: YAML via PyYAML

### Dependencies
```toml
[project]
dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
    "litellm>=1.0.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]
```

### Avoid
- LangChain (overkill para MVP)
- Async en CLI (innecesario, complica)
- ORMs complejos (SQLAlchemy core es suficiente)
- Classes everywhere (funciones simples primero)

### Environment Variables
```bash
GEMINI_API_KEY=xxx        # Required for Gemini
URPE_MODEL=gemini/gemini-2.0-flash  # Optional override
URPE_CONFIG_PATH=./config.yaml      # Optional config file
```

## CHECKPOINTS

1. **Project setup** - pyproject.toml, estructura de carpetas, deps instaladas
2. **CLI skeleton** - Comandos básicos funcionando (sin lógica)
3. **LLM integration** - `urpe ask` devuelve respuesta de Gemini
4. **Memory** - Conversaciones se guardan y recuperan
5. **Tools** - `run_command` funciona con confirmación
6. **Tests passing** - Todos los tests verdes

## CONTEXT

### Reference: PLAN.md
El archivo PLAN.md en el mismo directorio contiene la visión completa del sistema. Este spec implementa solo la Fase 1 (MVP CLI).

### Gemini API Key
```
GEMINI_API_KEY=AIzaSyBkDc-ymqEcL5_2YadQ8dCPFq5Hr04SBT8
```

### Estructura final esperada
```
urpe-agent-system/
├── src/
│   └── urpe/
│       ├── __init__.py
│       ├── cli.py          # Typer commands
│       ├── agent.py        # Core loop
│       ├── llm.py          # LiteLLM wrapper
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── base.py     # Tool base class
│       │   └── shell.py    # run_command tool
│       ├── memory/
│       │   ├── __init__.py
│       │   └── sqlite.py   # SQLAlchemy models + queries
│       └── config.py       # Settings
├── tests/
│   ├── test_tools.py
│   ├── test_memory.py
│   └── test_agent.py
├── config.yaml
├── pyproject.toml
├── PLAN.md
├── SPEC.md
└── README.md
```

## NOTES

- Usar `uv` para crear el proyecto: `uv init urpe-agent-system`
- El CLI debe ser instalable: `uv pip install -e .`
- Priorizar que funcione sobre que sea elegante
- Si algo no está claro en el spec, elegir la opción más simple
