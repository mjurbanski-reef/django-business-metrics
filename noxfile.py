import os
from pathlib import Path

import nox

CI = os.environ.get("CI") is not None

ROOT = Path(".")
PYTHON_VERSIONS = ["3.9", "3.10", "3.11"][::-1]
DJANGO_VERSIONS = ["3.2", "4.2"][::-1]
PYTHON_DEFAULT_VERSION = PYTHON_VERSIONS[-1]
DEMO_APP_DIR = ROOT / "demo"

nox.options.default_venv_backend = "venv"
nox.options.stop_on_first_error = True
nox.options.reuse_existing_virtualenvs = True

# In CI, use Python interpreter provided by GitHub Actions
if CI:
    nox.options.force_venv_backend = "none"


def run_readable(session, mode="fmt"):
    session.run(
        "docker",
        "run",
        "--rm",
        "-v",
        f"{ROOT.absolute()}:/data",
        "-w",
        "/data",
        "-u",
        f"{os.geteuid()}:{os.getegid()}",
        "ghcr.io/bobheadxi/readable:v0.5.0@sha256:423c133e7e9ca0ac20b0ab298bd5dbfa3df09b515b34cbfbbe8944310cc8d9c9",
        mode,
        "![.]**/*.md",
    )


@nox.session(name="format", python=PYTHON_DEFAULT_VERSION)
def format_(session):
    session.run("pip", "install", "-e", ".[dev]")
    session.run("black", ".")
    session.run("ruff", "check", "--fix", ".")
    run_readable(session, mode="fmt")


@nox.session(python=PYTHON_DEFAULT_VERSION)
def lint(session):
    session.run("pip", "install", "-e", ".[dev]")
    session.run("black", "--diff", ".")
    session.run("ruff", "check", "--diff", ".")
    run_readable(session, mode="check")


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("django", DJANGO_VERSIONS)
def test(session, django: str):
    session.run("pip", "install", f"django~={django}.0", "-e", ".[test]")
    session.run("pytest", "-vv")
