#!/usr/bin/env bash
set -euo pipefail

# Crea y activa un virtualenv local, instala Poetry y dependencias
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install poetry
# Instala dependencias dentro del mismo virtualenv
poetry config virtualenvs.create false
poetry install --no-interaction

echo "Entorno listo. Activa con: source .venv/bin/activate" 
