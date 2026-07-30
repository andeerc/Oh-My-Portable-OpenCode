"""
Hook pré-execução: verifica ambiente antes de iniciar o OpenCode.
"""
import os
import sys
import shutil
from pathlib import Path


def main():
    print("[HOOK] Verificando ambiente do OpenCode portátil...")

    # Verifica diretórios essenciais
    base_dir = Path(__file__).parent.parent.parent.resolve()
    bin_dir = base_dir / "bin"
    config_dir = base_dir / "config"

    for d in [bin_dir, config_dir]:
        if not d.exists():
            os.makedirs(d, exist_ok=True)
            print(f"[HOOK] Diretório criado: {d}")

    # Verifica dependências do sistema
    deps = {
        "git": shutil.which("git"),
        "node": shutil.which("node"),
        "npm": shutil.which("npm"),
        "python": shutil.which("python") or shutil.which("python3"),
    }

    presentes = [k for k, v in deps.items() if v is not None]
    ausentes = [k for k, v in deps.items() if v is None]

    print(f"[HOOK] Dependências presentes: {', '.join(presentes) if presentes else 'nenhuma'}")
    if ausentes:
        print(f"[HOOK] Dependências ausentes (não crítico): {', '.join(ausentes)}")

    # Verifica binário do OpenCode
    binary_name = "opencode.exe" if sys.platform == "win32" else "opencode"
    binary_path = bin_dir / binary_name
    if not binary_path.exists():
        print(f"[HOOK AVISO] Binário do OpenCode não encontrado em: {binary_path}")
        print("[HOOK AVISO] Coloque o binário na pasta bin/ antes de executar.")
    else:
        print(f"[HOOK] Binário do OpenCode encontrado: {binary_path}")

    print("[HOOK] Verificação concluída.")


if __name__ == "__main__":
    main()
