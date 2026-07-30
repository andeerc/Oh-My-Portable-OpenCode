# 🚀 Oh-My-Portable-OpenCode (ompo)

**ompo** transforma o [OpenCode](https://opencode.chat/) em uma solução **100% portátil, isolada e auto-sincronizada** entre máquinas (Windows/Linux).

Sem containers. O OpenCode é instalado localmente via npm — portátil entre máquinas.

---

## Testar direto do GitHub

```bash
git clone https://github.com/andeerc/Oh-My-Portable-OpenCode.git
cd Oh-My-Portable-OpenCode

# Opção A — Python direto (precisa de Python 3.12+)
python ompo.py install

# Opção B — Download do binário compilado (vá em Releases > baixar ompo.exe)
ompo install
```

O pipeline em `.github/workflows/build.yml` compila o binário automaticamente. Releases com `ompo.exe` prontos em Tags `v*`.

---

## 📁 Estrutura

```
Oh-My-Portable-OpenCode/
├── ompo.exe              # Gerenciador (install/sync/status/env)
├── ompo.py               # Código fonte
├── opencode.bat          # Launcher Windows (seta env vars + exec opencode)
├── opencode              # Launcher Linux/Mac
├── .token                # Token GitHub (sync de configurações)
├── node_modules/
│   ├── opencode-ai/      # OpenCode instalado localmente
│   └── opencode-omniroute-auth/  # Plugin (symlink)
├── config/               # XDG_CONFIG_HOME
│   └── opencode/
│       ├── opencode.json      # Config principal (model, mcp, formatter, plugins)
│       ├── agent/             # Agentes OpenCode (review, docs, test, etc.)
│       └── command/           # Comandos customizados (batch, simplify, etc.)
├── skills/               # Skills OpenCode (cada uma com SKILL.md)
│   ├── adr/
│   ├── code-review/
│   ├── tdd/
│   └── ...
├── plugins/              # Plugins fonte
│   └── opencode-omniroute-auth/
└── data/                 # Cache e históricos (XDG_DATA_HOME)
```

---

## 🚦 Comandos

| Comando | O que faz |
|---------|-----------|
| `ompo install` | **Instalação única**: npm install opencode-ai, cria dirs, registra env vars, sincroniza configs/agents/commands/skills/plugins do GitHub, compila plugins |
| `ompo sync` | Re-sincroniza tudo do GitHub e reconstrói plugins |
| `ompo status` | Mostra status (env vars, plugins, opencode-ai, config) |
| `ompo env` | Exibe variáveis de ambiente |
| `opencode` | Executa o OpenCode (leve, sem sync) |

---

## ⚡ Fluxo

### 1. Preparar

```bash
cd Oh-My-Portable-OpenCode

# (Opcional) Token para sincronizar configs do GitHub
echo "seu_token_github" > .token
```

### 2. Instalar (uma vez em cada máquina)

```bash
ompo install
```

Isso:
- Instala `opencode-ai` localmente via npm (em `node_modules/`)
- Cria estrutura de diretórios
- Registra `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `NODE_PATH` como variáveis persistentes
- Adiciona a pasta ao `PATH`
- Baixa configs/agents/commands/skills/plugins do GitHub
- Compila e linka plugins

**Reinicie o terminal** após o install.

### 3. Usar

```bash
opencode            # Rápido, sem overhead
ompo sync           # Quando quiser atualizar configs/plugins
ompo status         # Verificar tudo
```

---

## 🔄 Sincronização via GitHub

Configure em `ompo.py`:

```python
GITHUB_OWNER = "seu-usuario"
GITHUB_REPO = "seu-repo-configs"
```

Token em `.token` ou env var `OPENCODE_GH_TOKEN` (permissão `Contents: Read-only`).

Estrutura esperada no repositório:

```
seu-repo-configs/
├── config/
│   └── opencode/
│       ├── opencode.json
│       ├── agent/
│       ├── command/
├── skills/
│   ├── adr/
│   ├── code-review/
│   └── ...
└── plugins/
    └── opencode-omniroute-auth/
```

---

## 🧩 Skills inclusas (do [jellydn/my-ai-tools](https://github.com/jellydn/my-ai-tools))

| Skill | Descrição |
|-------|-----------|
| `adr` | Architecture Decision Records |
| `blindspot-pass` | Blindspot analysis |
| `capability-experiments` | Capability experiments |
| `code-quality-review` | Code quality review |
| `code-review` | Code review |
| `codemap` | Codebase mapping |
| `commit-atomic` | Atomic commits |
| `context-discovery` | Context discovery |
| `doc-search` | Documentation search |
| `docs-update` | Documentation updates |
| `draft-pull-request` | Draft PRs |
| `git-context` | Git context |
| `handoffs` | Handoffs between sessions |
| `implementation-logger` | Implementation logging |
| `llm-wiki` | LLM wiki |
| `pickup` | Pick up context |
| `plannotator-setup-goal` | Plan annotation |
| `portless-local` | Portless local dev |
| `pr-review` | PR review |
| `prd` | PRD generation |
| `qmd-knowledge` | QMD knowledge base |
| `quiz-me` | Quiz generation |
| `ralph` | Ralph |
| `slop` | SLOP |
| `spec-interview` | Spec interview |
| `tdd` | TDD workflow |
| `tmux` | Tmux integration |

## 📦 Plugins

Plugin incluído: [`opencode-omniroute-auth`](https://github.com/Alph4d0g/opencode-omniroute-auth) — autenticação OmniRoute com `/connect omniroute`.

---

## 🛠️ Compilar ompo.exe do zero

```bash
pip install pyinstaller
pyinstaller --onefile --name=ompo ompo.py
# exe em dist/ompo.exe
```

CI já configurado (`.github/workflows/build.yml`): a cada push no `main` ou tag `v*`, GitHub Actions compila `ompo.exe` (Windows + Linux) e disponibiliza como artefato. Tags `v*` geram release com os binários. É só baixar da página de Releases.
# Oh-My-Portable-OpenCode
