from __future__ import annotations

import os
from pathlib import Path


class EmpiricalDataError(RuntimeError):
    pass


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise EmpiricalDataError(
            "Install the data extra: uv pip install -e '.[data]'"
        ) from exc
    root = Path(__file__).resolve().parents[3]
    cwd = Path.cwd().resolve()
    cwd_env = cwd / ".env"
    if cwd_env.exists():
        load_dotenv(cwd_env)
    # Isolated tests chdir outside the repo; do not load the worktree .env then.
    in_repo = cwd == root or root in cwd.parents
    env = root / ".env"
    if in_repo and env.exists():
        load_dotenv(env)


def connect_wrds():
    _load_env()
    user = os.environ.get("WRDS_USERNAME") or os.environ.get("WRDS_USER")
    password = os.environ.get("WRDS_PASSWORD") or os.environ.get("WRDS_PASS")
    if not user or not password:
        raise EmpiricalDataError(
            "Missing WRDS_USERNAME / WRDS_PASSWORD in repo-root .env"
        )
    try:
        import wrds
    except ImportError as exc:
        raise EmpiricalDataError(
            "Install the data extra: uv pip install -e '.[data]'"
        ) from exc
    return wrds.Connection(wrds_username=user, wrds_password=password)
