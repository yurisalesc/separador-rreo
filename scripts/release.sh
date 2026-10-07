#!/usr/bin/env bash
# Build e upload do separador-rreo.
#
# Uso:
#   ./scripts/release.sh test     # TestPyPI
#   ./scripts/release.sh pypi     # PyPI oficial
#   ./scripts/release.sh build    # só gera dist/
#
# Pré-requisitos:
#   - ~/.pypirc configurado (veja .pypirc.example)
#   - versão em pyproject.toml ainda não publicada

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET="${1:-build}"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install -U pip build twine
pip install -e ".[dev]"

echo "==> Testes"
pytest -q

echo "==> Limpando dist/"
rm -rf dist/ build/ *.egg-info src/*.egg-info

echo "==> Build"
python -m build

echo "==> Checagem"
twine check dist/*

case "$TARGET" in
  build)
    echo "Artefatos em dist/ — nada publicado."
    ;;
  test|testpypi)
    echo "==> Upload TestPyPI"
    twine upload --repository testpypi dist/*
    echo "Instale com:"
    echo "  pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ separador-rreo"
    ;;
  pypi|prod)
    echo "==> Upload PyPI"
    twine upload dist/*
    echo "Instale com: pip install separador-rreo"
    ;;
  *)
    echo "Uso: $0 {build|test|pypi}" >&2
    exit 1
    ;;
esac
