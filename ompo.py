def sync_all():
    """Sincroniza tudo do GitHub (público sem token). Fallback pra arquivos locais."""
    token = _get_github_token()

    print("\n▸ Sincronizando do GitHub")
    if token:
        ok = _sync_from_github(token)
    else:
        # Tenta sem token (funciona em repo público)
        ok = _sync_from_github(None)

    if not ok:
        # Fallback: usa os arquivos que já tão no clone
        if token:
            print("  x Falha na sincronização — usando arquivos locais")
        else:
            print("  (sem token) — arquivos locais do repositório")
        for item_path in SYNC_ITEMS:
            local = BASE_DIR / item_path
            if local.exists():
                if local.is_file():
                    print(f"  * {item_path} ({local.stat().st_size} bytes)")
                else:
                    files = sum(1 for _ in local.rglob("*") if _.is_file())
                    print(f"  * {item_path}/ ({files} arquivos)")
            else:
                print(f"  x {item_path}/ — não encontrado")


def _sync_from_github(token):
    """Tenta sincronizar do GitHub. Retorna True se conseguiu, False se falhou."""
    headers = {"User-Agent": "ompo", "Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        for item_path in SYNC_ITEMS:
            local_target = BASE_DIR / item_path
            api_url = (
                f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/"
                f"contents/{item_path}?ref={GITHUB_BRANCH}"
            )

            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            if isinstance(data, list):
                # É diretório — sincroniza cada arquivo
                total = 0
                for item in data:
                    if item["type"] == "file":
                        dest = BASE_DIR / item["path"]
                        raw_url = item["download_url"]
                        if _download_file(raw_url, dest, token):
                            total += 1
                    elif item["type"] == "dir":
                        # Recurse para subdiretórios
                        total += _recurse_dir(item["path"], headers, token)
                print(f"  * {item_path} — {total} arquivos")
            elif isinstance(data, dict) and data.get("type") == "file":
                # Arquivo único
                dest = local_target
                dest.parent.mkdir(parents=True, exist_ok=True)
                raw_url = data["download_url"]
                if _download_file(raw_url, dest, token):
                    print(f"  * {item_path}")

        return True
    except urllib.error.HTTPError as e:
        if e.code in (401, 403) and not token:
            # Repo privado sem token
            return False
        if e.code == 404:
            print(f"  x Repositório {GITHUB_OWNER}/{GITHUB_REPO} não encontrado")
            return False
        print(f"  x HTTP {e.code}")
        return False
    except Exception as e:
        print(f"  x {e}")
        return False


def _recurse_dir(prefix, headers, token, indent=1):
    """Baixa recursivamente um diretório do GitHub."""
    url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"contents/{prefix}?ref={GITHUB_BRANCH}"
    )
    total = 0
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            items = json.loads(resp.read().decode())
        for item in items:
            if item["type"] == "file":
                dest = BASE_DIR / item["path"]
                raw_url = item["download_url"]
                if _download_file(raw_url, dest, token):
                    total += 1
            elif item["type"] == "dir":
                total += _recurse_dir(item["path"], headers, token, indent + 1)
    except Exception:
        pass
    return total


def _download_file(url, dest, token):
    """Download raw do GitHub. Funciona sem token em repo público."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "ompo")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(resp.read())
                return True
    except Exception:
        pass
    return False
