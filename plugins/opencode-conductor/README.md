# Conductor Plugin for OpenCode

> **Measure twice, code once.**

Conductor is a specialized OpenCode plugin designed to enforce a rigorous, **Context-Driven Development** lifecycle. It transforms OpenCode from a reactive coding tool into a proactive project architect that follows a strict protocol to specify, plan, and implement software features and bug fixes.

The philosophy is simple: **control your code by controlling your context.** By treating project requirements and plans as managed artifacts, Conductor ensures every agent interaction is grounded in deep, persistent project awareness.

---

## 🚀 Key Features

*   **Specialized `@conductor` Agent**: A dedicated subagent that acts as your Project Architect and Technical Lead.
*   **Native Slash Commands**: Integrated shortcuts like `/conductor:setup`, `/conductor:newTrack`, and `/conductor:implement` for frictionless project management.
*   **Modern Permissions**: Fully compatible with OpenCode v1.1.1 granular permission system.
*   **Protocol-Driven Workflow**: Automated enforcement of the **Context -> Spec -> Plan -> Implement** lifecycle.
*   **Smart Revert**: A Git-aware revert system that understands logical units of work (Tracks, Phases, Tasks) instead of just raw commit hashes.
*   **19+ Style Templates**: Built-in support for a vast range of languages including Rust, Solidity, Zig, Julia, Kotlin, Swift, and more.
*   **Zero-Config Bootstrap**: Automatically installs agents and commands to your global OpenCode configuration on first run.
*   **Sisyphus Synergy**: Optimized to work alongside [OhMyOpenCode](https://github.com/code-yeongyu/oh-my-opencode) for a multi-agent team experience.
*   **Agent Agnostic**: Commands can be invoked by any agent, giving you the freedom to choose your primary interface.

---

## 🛠️ The Conductor Lifecycle

Conductor organizes your work into **Tracks** (features or bug fixes). Every Track follows three mandatory phases:

### 1. Project Initialization (`/conductor:setup`)
Run this once per project. The agent will interview you to define:
*   **Product Vision**: Target users, core goals, and primary features.
*   **Tech Stack**: Languages, frameworks, and databases.
*   **Workflow Rules**: Testing standards (e.g., TDD), commit strategies, and documentation patterns.

### 2. Track Planning (`/conductor:newTrack`)
When you're ready for a new task, tell the agent what you want to build.
*   **Specification (`spec.md`)**: Conductor asks 3-5 targeted questions to clarify the "What" and "Why".
*   **Implementation Plan (`plan.md`)**: Once the spec is approved, Conductor generates a step-by-step checklist adhering to your project's workflow rules.

### 3. Autonomous Implementation (`/conductor:implement`)
The agent works through the `plan.md` checklist, executing tasks, running tests, and making semantic commits automatically until the Track is complete.

---

## 📦 Installation

Add the plugin to your global OpenCode configuration file. OpenCode will automatically fetch and install it from NPM.

**File:** `~/.config/opencode/opencode.json`

```json
{
  "plugin": [
    "opencode-conductor-plugin"
  ]
}
```

*Note: Please restart OpenCode after the first run to enable the global slash commands.*

---

## ⚙️ Configuration

We highly recommend pinning the `@conductor` agent to a "flash" model for optimal performance during planning phases.

### Standard OpenCode Config
**File:** `~/.config/opencode/opencode.json`
```json
{
  "agent": {
    "conductor": {
      "model": "google/gemini-3-flash"
    }
  }
}
```

### OhMyOpenCode Config
**File:** `~/.config/opencode/oh-my-opencode.json`
```json
{
  "agents": {
    "conductor": {
      "model": "google/gemini-3-flash"
    }
  }
}
```

---

## 📋 Commands Reference

| Command | Description |
| :--- | :--- |
| `/conductor:setup` | Initialize the `conductor/` directory and project "Constitution". |
| `/conductor:newTrack "desc"` | Start a new feature/bug Track with spec and plan generation. |
| `/conductor:implement` | Start implementing the next pending task in the current track. |
| `/conductor:status` | Get a high-level overview of project progress and active tracks. |
| `/conductor:revert` | Interactively select a task, phase, or track to undo via Git. |

---

## 🤝 Synergy with OhMyOpenCode

If you use the **OhMyOpenCode** suite, `@conductor` acts as your Technical Lead. While **Sisyphus** manages the general conversation and orchestration, he can delegate complex architectural planning and protocol enforcement to the `@conductor` agent. 

Conductor includes built-in "Loop Protection" to ensure it never conflicts with OhMyOpenCode's continuation enforcers during interactive Q&A sessions.

---

## 📈 Automated Versioning

This project follows **Conventional Commits**. Releases are automated via Semantic Release:
- `feat:` -> Minor version bump
- `fix:` -> Patch version bump
- `BREAKING CHANGE:` -> Major version bump

---

## 📜 License

Distributed under the [Apache License 2.0](LICENSE).