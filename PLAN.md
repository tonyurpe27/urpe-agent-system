# Urpe Agent System - Plan Inicial

## Visión
Sistema de agentes AI local (CLI) con soporte para MCP, skills, tools, sub-agentes y memoria persistente. Flexible, modular, y optimizado para desarrolladores.

---

## Arquitectura (4 Capas)

### 1. Capa CLI (Interfaz)
- **Typer** + **Rich**: Comandos con autocompletado, output visual
- Confirmación human-in-the-loop para tools
- Modo interactivo y one-shot

### 2. Capa Orquestación (Núcleo)
- Loop principal del agente
- Gestión de contexto y estado
- Routing a tools/skills/sub-agentes
- **Opciones:** LangChain, CrewAI, OpenAI Agents SDK, Google ADK, o custom

### 3. Capa Capacidades
#### Tools
- Funciones modulares con schema Pydantic
- Soporte MCP Protocol (Anthropic spec)
- Confirmación antes de ejecutar (configurable)

#### Skills
- Carpetas con SKILL.md + assets
- Inyección de conocimiento al prompt
- Similar a Gemini CLI skills

#### Sub-Agentes
- Agentes especializados vía FastAPI
- Comunicación HTTP/async
- Pueden tener sus propias tools/skills

### 4. Capa Persistencia
- **Memoria conversacional:** SQLite + SQLAlchemy
- **Memoria semántica:** ChromaDB o FAISS (vectorial)
- **Config:** YAML/TOML

---

## Stack Tecnológico

| Componente | Tecnología | Notas |
|------------|-----------|-------|
| CLI | Typer + Rich | Python moderno |
| Orquestación | LangChain / Custom | Evaluar overhead |
| MCP | FastAPI + Pydantic | Async, tipado |
| LLMs | LiteLLM | Abstracción multi-provider |
| Memoria vectorial | ChromaDB | Local, fácil setup |
| Memoria relacional | SQLite | Sin dependencias |
| Validación | Pydantic v2 | Schemas tools/config |
| Config | YAML | Human-readable |
| Ejecución segura | E2B Sandboxes | Código AI aislado en cloud |

---

## E2B Integration

### ¿Qué es E2B?
- Infraestructura open-source para ejecutar código AI en sandboxes aislados
- VMs livianas (~150ms startup)
- SDKs: Python y JavaScript
- $100 créditos gratis al registrarse

### Beneficios
- **Seguridad:** Código AI nunca toca tu máquina local
- **Escalabilidad:** Miles de sandboxes paralelos
- **Aislamiento:** Cada agente/usuario su propio sandbox
- **Tools peligrosos:** File I/O, terminal, internet — todo en sandbox

### Ejemplo integración
```python
from e2b_code_interpreter import Sandbox

async def execute_code_tool(code: str):
    with Sandbox() as sbx:
        result = sbx.run_code(code)
        return result.text
```

### Casos de uso E2B
- Deep research agents
- Data analysis + visualización
- Coding agents
- Reinforcement learning (paralelo)
- Computer use (desktop virtual)

---

## Panorama Actual IA Agentes (Enero 2026)

| Capa | Opciones |
|------|----------|
| **Orquestación** | LangChain, CrewAI, OpenAI Agents SDK, Google ADK, Autogen |
| **Ejecución código** | E2B, Modal, Replicate, local Docker |
| **MCP/Tools** | Anthropic MCP, OpenAI functions, custom |
| **Memoria** | ChromaDB, Pinecone, Weaviate, pg_vector |
| **LLMs** | GPT-4.5, Claude Opus 4, Gemini 3, Llama 4 |
| **Deploy** | Railway, Fly.io, Lambda, self-hosted |

---

## Estructura Propuesta

```
urpe-agent-system/
├── src/
│   ├── cli/           # Typer commands
│   ├── core/          # Agent loop, orchestration
│   ├── tools/         # Built-in tools
│   ├── skills/        # Knowledge injection
│   ├── memory/        # Persistence layer
│   └── mcp/           # MCP server/client
├── agents/            # Sub-agent definitions
├── config/            # YAML configs
├── data/              # SQLite, ChromaDB storage
├── tests/
├── pyproject.toml
└── README.md
```

---

## Fases de Desarrollo

### Fase 1: MVP CLI (1-2 semanas)
- [ ] Setup proyecto Python (uv/poetry)
- [ ] CLI básica con Typer
- [ ] Integración LiteLLM (Gemini 3 Flash)
- [ ] Tool simple con confirmación
- [ ] Memoria conversacional SQLite

### Fase 2: Skills + MCP (2 semanas)
- [ ] Sistema de skills (SKILL.md parser)
- [ ] MCP client para tools externas
- [ ] ChromaDB para RAG básico

### Fase 3: Sub-Agentes (2 semanas)
- [ ] FastAPI para sub-agentes
- [ ] Orquestación multi-agente
- [ ] Comunicación async

### Fase 4: E2B + Seguridad (1 semana)
- [ ] Integración E2B para code execution
- [ ] Sandbox policies
- [ ] Error handling robusto

### Fase 5: Deploy + Webhooks (1 semana)
- [ ] FastAPI webhook endpoints
- [ ] Docker containerization
- [ ] Deploy a Railway/Fly.io
- [ ] Integraciones: WhatsApp, Telegram, Slack

### Fase 6: Polish (1 semana)
- [ ] Config YAML completa
- [ ] Logging/debugging
- [ ] Documentación
- [ ] Tests

---

## Modelos Recomendados

- **Principal:** Gemini 3 Flash (costo/beneficio)
- **Fallback:** Claude Sonnet 4 (vía LiteLLM)
- **Local opcional:** Ollama con Llama 3.3

---

## Referencias

- [E2B Docs](https://e2b.dev/docs)
- [Anthropic MCP Spec](https://github.com/anthropics/mcp)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [LangChain](https://python.langchain.com/)
- [CrewAI](https://github.com/crewAIInc/crewAI)
- [LiteLLM](https://github.com/BerriAI/litellm)

---

## Notas

- Priorizar simplicidad sobre features
- Mantener modular para swap de componentes
- Documentar decisiones técnicas
- Inspirarse en Clawdbot/Gemini CLI pero más flexible

---

*Creado: 28 enero 2026*
*Autor: Bruno + Tony @ Urpe*
