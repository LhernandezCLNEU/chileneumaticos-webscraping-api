#!/usr/bin/env bash
set -euo pipefail

#!/usr/bin/env bash
set -euo pipefail

# Ejecuta migraciones y arranca uvicorn en modo desarrollo.
# Si no existe, crea el virtualenv en `.venv` e instala `poetry` localmente.

cp .env.dev .env 2>/dev/null || true

# Crear venv si falta
if [ ! -d ".venv" ]; then
	echo "Creando virtualenv .venv..."
	python3 -m venv .venv
fi

# Activar venv
source .venv/bin/activate

# Instalar poetry en el venv si no está disponible
if ! command -v poetry >/dev/null 2>&1; then
	echo "Instalando poetry en el virtualenv..."
	pip install --upgrade pip
	pip install poetry
fi

poetry config virtualenvs.create false || true

# Aplicar migraciones (usará sqlite en development)
poetry run alembic upgrade head

# Ejecutar servidor en modo autoreload
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
