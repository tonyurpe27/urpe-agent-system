# urpe-agent-mvp Progress

## 2026-01-28

### Checkpoint 1: Project Setup ✅
- [x] pyproject.toml con dependencias
- [x] Estructura de carpetas (src/urpe/, tests/)
- [x] config.yaml

### Checkpoint 2: CLI Skeleton ✅
- [x] Comando `urpe chat`
- [x] Comando `urpe ask`
- [x] Comando `urpe history`
- [x] Comando `urpe tools`

### Checkpoint 3: LLM Integration ✅
- [x] LiteLLM wrapper (llm.py)
- [x] Streaming responses
- [x] Model selection

### Checkpoint 4: Memory ✅
- [x] SQLite models (Conversation, Message)
- [x] MemoryStore class
- [x] Save/retrieve conversations

### Checkpoint 5: Tools ✅
- [x] Tool base classes
- [x] Tool registry
- [x] `run_command` tool con confirmación
- [x] Tool schemas para LLM

### Checkpoint 6: Tests
- [x] test_tools.py
- [x] test_memory.py
- [x] test_agent.py
- [ ] Ejecutar tests

## Next Steps
1. Instalar dependencias: `uv sync`
2. Correr tests: `uv run pytest`
3. Probar CLI: `uv run urpe ask "Hello"`
