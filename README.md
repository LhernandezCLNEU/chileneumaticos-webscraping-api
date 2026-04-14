# chileneumaticos-webscraping-api

API backend para almacenar y postprocesar productos scrapeados de una tienda de neumáticos.

Instrucciones rápidas:

- Copiar `.env.example` a `.env` y ajustar variables.
- Construir y levantar con Docker Compose:

```bash
docker-compose up --build
```

- Servidor de desarrollo:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Estructura inicial creada y archivos base para continuar con el desarrollo.

Pasos rápidos para desarrollo (macOS / Linux):

1) Crear y activar el entorno virtual local:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Instalar Poetry (dentro del venv) y dependencias:

```bash
pip install --upgrade pip
pip install poetry
poetry config virtualenvs.create false
# Usar Python 3.11 y pedir a Poetry que use ese intérprete antes de instalar
python3.11 -m pip install --upgrade --user poetry
python3.11 -m poetry env use /opt/homebrew/bin/python3.11 || python3.11 -m poetry env use $(which python3.11)
python3.11 -m poetry install
```

O usa el helper creado:

```bash
./scripts/setup_dev.sh
```

Consejos rápidos:

- Asegúrate de usar `python3.11` en este proyecto (el archivo `pyproject.toml` requiere `^3.11`).
- Si `poetry install` falla por el paquete del proyecto, añade la sección `packages = [{ include = "app" }]` en `pyproject.toml` (ya aplicada en este repositorio) o ejecuta `python3.11 -m poetry install --no-root` para instalar sólo dependencias.
- Para desarrollo normal usa el helper `./scripts/run_dev.sh`, que crea/activa `.venv`, instala `poetry` si hace falta, aplica migraciones y arranca `uvicorn`.

3) Preparar entorno y ejecutar (copia `.env.dev` a `.env` si no lo hiciste):

```bash
cp .env.dev .env
./scripts/run_dev.sh
```

4) Alternativa con Docker Compose (arranca MySQL + Redis + app):

```bash
docker-compose up --build
```

Notas:
- En desarrollo `ENVIRONMENT=development` (usa SQLite). En producción, pon `ENVIRONMENT=production` y configura `MYSQL_*`.
- Para ejecutar las migraciones localmente: `poetry run alembic upgrade head`.

Selenium (opcional, para scrapers que usan navegador)
-----------------------------------------------

Si quieres ejecutar scrapers que renderizan con un navegador (Selenium), sigue estos pasos en tu entorno de desarrollo (macOS / Linux):

1) Activar tu entorno virtual:

```bash
source .venv/bin/activate
```

2) Instalar dependencias Python necesarias:

```bash
pip install selenium webdriver-manager
```

3) Instalar un navegador (Chrome/Chromium) si no lo tienes. En macOS con Homebrew:

```bash
brew install --cask google-chrome
# o para chromium
brew install --cask chromium
```

4) (Opcional) Si tu entorno da errores de certificado, habilita temporalmente `SKIP_SSL_VERIFY` en `.env` o exportando la variable:

```bash
export SKIP_SSL_VERIFY=true
# o en .env:
SKIP_SSL_VERIFY=true
```

5) Ejecutar el scraper de ejemplo:

```bash
python scripts/run_example_scraper.py --url https://example.com/ --dry-run
```

Notas de seguridad:
- No actives `SKIP_SSL_VERIFY` en producción.
- `webdriver-manager` descargará el driver compatible automáticamente.

