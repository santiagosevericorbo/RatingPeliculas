from pathlib import Path

# Códigos ANSI
_RESET = "\033[0m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_GRAY = "\033[90m"
_BOLD = "\033[1m"


def _relative(path: str, root: str | None = None) -> str:
    """
    Intenta mostrar la ruta relativa al root dado.
    Si no puede, muestra solo los últimos 2 segmentos.
    """
    try:
        return str(Path(path).relative_to(root)) if root else path
    except ValueError:
        parts = Path(path).parts
        return str(Path(*parts[-2:])) if len(parts) >= 2 else path


def info(msg: str) -> None:
    print(f"{_CYAN}  ℹ {msg}{_RESET}")


def success(msg: str) -> None:
    print(f"{_GREEN}  ✔ {msg}{_RESET}")


def warning(msg: str) -> None:
    print(f"{_YELLOW}  ⚠ {msg}{_RESET}")


def skip(file_path: str, reason: str, root: str | None = None) -> None:
    relative = _relative(file_path, root)
    print(
        f"{_GRAY}  ↷ SKIP {_RESET}{_YELLOW}{relative}{_RESET}{_GRAY} → {reason}{_RESET}"
    )


def error(msg: str) -> None:
    print(f"{_RED}  ✖ ERROR {msg}{_RESET}")
