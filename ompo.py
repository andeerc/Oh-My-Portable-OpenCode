import os
import sys
import json
import subprocess
import shutil
import urllib.request
import urllib.error
import argparse
import stat
from pathlib import Path

# Força UTF-8 na saída (Windows cp1252 não suporta acentos)
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ==============================================================================
# CONFIG
# ==============================================================================
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent.resolve()
else:
    BASE_DIR = Path(__file__).parent.resolve()

PLUGINS_DIR = BASE_DIR / "plugins"
NODE_MODULES = BASE_DIR / "node_modules"
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
HOOKS_DIR = BASE_DIR / "hooks" / "pre-run"

# Onde o opencode-ai fica instalado localmente
OPENCODE_BIN = NODE_MODULES / ".bin" / ("opencode.cmd" if sys.platform == "win32" else "opencode")

# GitHub
GITHUB_OWNER = "seu-usuario"
GITHUB_REPO = "seu-repo-configs"
GITHUB_BRANCH = "main"

# Paths dentro do repo GitHub para sincronizar
SYNC_ITEMS = [
    "config/opencode/opencode.json",
    "config/opencode/agent",
    "config/opencode/command",
    "skills",
    "plugins",
]


# ==============================================================================
# HELPERS
# ==============================================================================
def _get_github_token():
    token = os.environ.get("OPENCODE_GH_TOKEN")
    token_file = BASE_DIR / ".token"
    if not token and token_file.exists():
        token = token_file.read_text().strip()
    return token


def _npm(args_list, cwd, capture=False):
    npm = shutil.which("npm") or "npm"
    kwargs = dict(cwd=str(cwd))
    if capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    if sys.platform == "win32":
        kwargs["shell"] = True
        return subprocess.run(f'"{npm}" {" ".join(args_list)}', **kwargs)
    return subprocess.run([npm] + args_list, **kwargs)


def _setx(name, value):
    try:
        subprocess.run(["setx", name, value], capture_output=True, text=True, check=True)
        print(f"  * {name}")
    except Exception as e:
        print(f"  x {name} — {e}")


def _get_shell_rc():
    home = Path.home()
    for rc in [".bashrc", ".zshrc", ".profile", ".bash_profile"]:
        p = home / rc
        if p.exists():
            return p
    return home / ".bashrc"  # fallback


# ==============================================================================
# COMMANDS
# ==============================================================================
def install_opencode():
    """Instala o opencode-ai localmente via npm."""
    print("\n▸ Instalando OpenCode")
    if OPENCODE_BIN.exists():
        print("  * opencode-ai já instalado")
        return
    print("  → npm install opencode-ai...")
    result = _npm(["install", "opencode-ai"], BASE_DIR, capture=True)
    if result and result.returncode == 0:
        print("  * opencode-ai instalado com sucesso")
    else:
        print("  x Falha ao instalar opencode-ai. Execute 'npm install opencode-ai' manualmente.")


def cmd_install(args):
    """Instalação completa."""
    print("=== ompo install ===\n")

    ensure_dirs()
    install_opencode()
    register_env()
    sync_all()
    build_plugins()

    print(f"""
---
  [*] Instalação concluída!

  Comandos:
    opencode        - Executar OpenCode
    ompo sync       - Sincronizar configs
    ompo status     - Ver status
    ompo env        - Ver variáveis

  Reinicie o terminal se necessário.
---""")


def cmd_sync(args):
    """Sincroniza configs, plugins e reconstrói."""
    print("=== ompo sync ===\n")
    if not OPENCODE_BIN.exists():
        install_opencode()
    token = _get_github_token()
    if not token:
        print("[SYNC] Token não encontrado. Configure .token ou OPENCODE_GH_TOKEN.")
        return
    sync_all()
    build_plugins()
    print("\n[*] Sincronização concluída!")


def cmd_status(args):
    """Mostra status da instalação."""
    print("=== ompo status ===\n")

    # Env vars
    for name in ["XDG_CONFIG_HOME", "XDG_DATA_HOME", "NODE_PATH"]:
        val = os.environ.get(name, "")
        expected = str(CONFIG_DIR) if name == "XDG_CONFIG_HOME" else (
            str(DATA_DIR) if name == "XDG_DATA_HOME" else str(NODE_MODULES)
        )
        ok = val == expected
        print(f"  {'*' if ok else 'x'} {name}={val or '(não definida)'}")
        if not ok and not val:
            print(f"     esperado: {expected}")

    # PATH
    base_dir_str = str(BASE_DIR)
    in_path = base_dir_str in os.environ.get("PATH", "")
    print(f"  {'*' if in_path else 'x'} BASE_DIR no PATH ({base_dir_str})")

    # Plugins
    print()
    plugins = discover_plugins()
    if plugins:
        print(f"  Plugins ({len(plugins)}):")
        for d, pkg in plugins:
            name = pkg.get("name", d.name)
            has_dist = (d / "dist").exists()
            linked = (NODE_MODULES / name).exists()
            print(f"    {'*' if has_dist else 'o'} {name}" + (" -> node_modules" if linked else ""))
    else:
        print("  Nenhum plugin encontrado.")

    # Config
    print()
    config_file = CONFIG_DIR / "opencode" / "opencode.json"
    if config_file.exists():
        print(f"  * opencode.json ({config_file})")
        try:
            data = json.loads(config_file.read_text())
            plugins_list = data.get("plugin", [])
            if plugins_list:
                print(f"    plugins configurados: {', '.join(plugins_list)}")
        except Exception:
            print("    (erro ao ler)")
    else:
        print(f"  x opencode.json não encontrado")

    # OpenCode instalado?
    print()
    opencode_exists = OPENCODE_BIN.exists()
    print(f"  {'*' if opencode_exists else 'x'} opencode-ai: {OPENCODE_BIN}")
    if opencode_exists:
        try:
            v = subprocess.run([str(OPENCODE_BIN), "--version"], capture_output=True, text=True, timeout=5)
            print(f"    versão: {v.stdout.strip() or v.stderr.strip()}")
        except Exception:
            pass


def cmd_env(args):
    """Exibe variáveis de ambiente relevantes."""
    print("=== ompo env ===\n")
    for name in ["XDG_CONFIG_HOME", "XDG_DATA_HOME", "NODE_PATH", "OPENCODE_GH_TOKEN"]:
        val = os.environ.get(name, "")
        if name == "OPENCODE_GH_TOKEN" and val:
            val = val[:8] + "..." if len(val) > 8 else "***"
        print(f"  {name}={val or '(não definida)'}")
    print(f"  PATH contém BASE_DIR: {str(BASE_DIR) in os.environ.get('PATH', '')}")


# ==============================================================================
# CORE
# ==============================================================================
def ensure_dirs():
    print("▸ Diretórios")
    for d in [CONFIG_DIR / "opencode", CONFIG_DIR / "opencode" / "agent", CONFIG_DIR / "opencode" / "command",
              DATA_DIR, PLUGINS_DIR, HOOKS_DIR, NODE_MODULES, BASE_DIR / "skills"]:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  * {d.relative_to(BASE_DIR)}")


def register_env():
    """Registra variáveis de ambiente persistentes."""
    print("\n▸ Variáveis de ambiente")

    if sys.platform == "win32":
        _setx("XDG_CONFIG_HOME", str(CONFIG_DIR))
        _setx("XDG_DATA_HOME", str(DATA_DIR))
        _setx("NODE_PATH", str(NODE_MODULES))

        # Adiciona BASE_DIR ao PATH se necessário
        current = os.environ.get("PATH", "")
        base_str = str(BASE_DIR)
        if base_str not in current:
            _setx("PATH", base_str + ";" + current)
            print("  ! Reinicie o terminal para ativar PATH")
        else:
            print("  * BASE_DIR já está no PATH")
    else:
        rc = _get_shell_rc()
        exports = [
            f'export XDG_CONFIG_HOME="{CONFIG_DIR}"',
            f'export XDG_DATA_HOME="{DATA_DIR}"',
            f'export NODE_PATH="{NODE_MODULES}"',
            f'export PATH="{BASE_DIR}:$PATH"',
        ]
        try:
            existing = rc.read_text()
            new_lines = []
            for line in exports:
                if line not in existing:
                    new_lines.append(line)
            if new_lines:
                with open(rc, "a") as f:
                    f.write("\n# Oh-My-Portable-OpenCode\n")
                    for line in new_lines:
                        f.write(line + "\n")
                print(f"  * Adicionado a {rc}")
                print(f"  ! Execute: source {rc}")
            else:
                print(f"  * Já configurado em {rc}")
        except Exception as e:
            print(f"  x Erro ao atualizar {rc}: {e}")


_FORBIDDEN_PATHS = [".git", "node_modules", "dist", "build"]  # skip em tree sync


def _download_file(url, dest, token):
    """Download um arquivo raw do GitHub."""
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {token}")
    req.add_header("User-Agent", "ompo")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(resp.read())
                return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False  # path não existe no repo
    except Exception:
        pass
    return False


def _sync_tree(api_url, local_dir, token):
    """Sincroniza recursivamente usando Git Trees API."""
    req = urllib.request.Request(api_url)
    req.add_header("Authorization", f"token {token}")
    req.add_header("User-Agent", "ompo")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            tree_data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  x Erro ao listar árvore: {e}")
        return

    items = tree_data.get("tree", []) if "tree" in tree_data else tree_data
    # Se for resposta direta da API Contents
    if isinstance(items, list) and items and "path" in items[0]:
        tree = items
    elif "tree" in tree_data:
        tree = tree_data["tree"]
    else:
        print("  x Formato de resposta inesperado")
        return

    total = 0
    for item in tree:
        path_parts = item["path"].split("/")
        # Pula diretórios de sistema/build
        if any(seg in _FORBIDDEN_PATHS for seg in path_parts):
            continue
        if item["type"] == "blob":
            dest = local_dir / item["path"]
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{item['path']}"
            if _download_file(raw_url, dest, token):
                total += 1
    print(f"  * {total} arquivos sincronizados -> {local_dir.relative_to(BASE_DIR)}")


def sync_all():
    """Sincroniza todos os itens configurados do GitHub."""
    token = _get_github_token()
    if not token:
        print("\n▸ Sync: Token não encontrado. Configure .token ou OPENCODE_GH_TOKEN.")
        return

    print("\n▸ Sincronizando do GitHub")

    for item_path in SYNC_ITEMS:
        local_target = BASE_DIR / item_path
        api_url = (
            f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/"
            f"contents/{item_path}?ref={GITHUB_BRANCH}"
        )

        # Primeiro tenta como arquivo único
        req = urllib.request.Request(api_url)
        req.add_header("Authorization", f"token {token}")
        req.add_header("User-Agent", "ompo")
        req.add_header("Accept", "application/vnd.github.v3+json")

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"  o {item_path} — não encontrado no repo")
            else:
                print(f"  x {item_path} — HTTP {e.code}")
            continue
        except Exception as e:
            print(f"  x {item_path} — {e}")
            continue

        if isinstance(data, list):
            # É um diretório — sincroniza via Tree API
            tree_url = (
                f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/"
                f"git/trees/{GITHUB_BRANCH}?recursive=1"
            )
            # Precisamos pegar a tree e filtrar por este path
            try:
                req2 = urllib.request.Request(tree_url)
                req2.add_header("Authorization", f"token {token}")
                req2.add_header("User-Agent", "ompo")
                with urllib.request.urlopen(req2, timeout=10) as resp2:
                    tree_full = json.loads(resp2.read().decode())
                relevant = [i for i in tree_full.get("tree", []) if i["path"].startswith(item_path)]
                total = 0
                for item in relevant:
                    rel_path = item["path"][len(item_path) + 1:] if len(item["path"]) > len(item_path) else ""
                    if not rel_path:
                        continue
                    if any(seg in _FORBIDDEN_PATHS for seg in rel_path.split("/")):
                        continue
                    if item["type"] == "blob":
                        dest = local_target / rel_path
                        raw_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{item['path']}"
                        if _download_file(raw_url, dest, token):
                            total += 1
                print(f"  * {item_path} — {total} arquivos")
            except Exception as e:
                print(f"  x {item_path} — {e}")
        elif isinstance(data, dict) and data.get("type") == "file":
            # É um arquivo único
            dest = local_target
            dest.parent.mkdir(parents=True, exist_ok=True)
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{item_path}"
            if _download_file(raw_url, dest, token):
                print(f"  * {item_path}")


def discover_plugins():
    """Descobre plugins na pasta plugins/."""
    plugins = []
    if not PLUGINS_DIR.exists():
        return plugins
    for entry in sorted(PLUGINS_DIR.iterdir()):
        pkg_json = entry / "package.json"
        if entry.is_dir() and pkg_json.exists():
            try:
                pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
                plugins.append((entry, pkg))
            except Exception:
                continue
    return plugins


def build_plugins():
    """Constrói e instala todos os plugins."""
    plugins = discover_plugins()
    if not plugins:
        print("\n▸ Plugins: nenhum encontrado")
        return

    print(f"\n▸ Plugins ({len(plugins)})")
    for plugin_dir, pkg in plugins:
        name = pkg.get("name", plugin_dir.name)
        has_build = "build" in pkg.get("scripts", {})
        dist_dir = plugin_dir / "dist"

        # Build se necessário
        if has_build and not dist_dir.exists():
            print(f"  -> {name}: instalando dependências...")
            _npm(["install"], plugin_dir)
            print(f"  -> {name}: compilando...")
            _npm(["run", "build"], plugin_dir)
            print(f"  * {name} compilado")

        # Link no node_modules
        NODE_MODULES.mkdir(parents=True, exist_ok=True)
        link = NODE_MODULES / name
        if not link.exists():
            print(f"  -> {name}: instalando...")
            try:
                if sys.platform == "win32":
                    subprocess.run(
                        ["cmd", "/c", "mklink", "/J", str(link), str(plugin_dir.resolve())],
                        capture_output=True, text=True, check=True, shell=True
                    )
                else:
                    link.symlink_to(plugin_dir.resolve())
                print(f"  * {name} instalado")
            except Exception as e:
                print(f"  x {name}: erro ao criar link: {e}")
        else:
            print(f"  * {name}")

    # Injeta plugins no opencode.json
    config_file = CONFIG_DIR / "opencode" / "opencode.json"
    if config_file.exists():
        try:
            config_data = json.loads(config_file.read_text(encoding="utf-8"))
            existing = config_data.get("plugin", [])
            if isinstance(existing, str):
                existing = [existing]
            changed = False
            for _, pkg in plugins:
                name = pkg.get("name")
                if name and name not in existing:
                    existing.append(name)
                    changed = True
            if changed:
                config_data["plugin"] = existing
                config_file.write_text(json.dumps(config_data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"  * Config atualizado com plugins: {', '.join(existing)}")
        except Exception:
            pass


# ==============================================================================
# MAIN
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        prog="ompo",
        description="Oh-My-Portable-OpenCode — Gerenciador portátil do OpenCode",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("install", help="Instalação completa (diretórios, env, sync, build)")
    sub.add_parser("sync", help="Sincroniza configs/plugins do GitHub e reconstrói")
    sub.add_parser("status", help="Exibe status da instalação")
    sub.add_parser("env", help="Exibe variáveis de ambiente")

    args = parser.parse_args()

    if args.command == "install":
        cmd_install(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "env":
        cmd_env(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
