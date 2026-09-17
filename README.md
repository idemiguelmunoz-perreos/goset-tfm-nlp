# GOSET. TFM. Componente A (extracción NLP) y Componente B (recomendador híbrido)

Extrae información estructurada (JSON validado con Pydantic) desde **cartillas
veterinarias** y **condicionados de pólizas de seguro de mascotas**, y compara
el método propuesto contra baselines.

## Alcance
- **Método propuesto:** LLM con *structured outputs* nativos + validación Pydantic.
- **Baselines:** (1) regex/reglas,  (2) LLM zero shot,  (3) LLM few shot.
- **Métricas:** F1 por campo, exact match, hallucination rate, null handling
  accuracy, latencia y coste por documento.

## Arranque en un comando
```bash
docker compose up --build
```
Levanta dos APIs REST con OpenAPI autogenerada:
- Componente A (extracción): http://localhost:8000/docs
- Componente B (recomendador): http://localhost:8001/docs

Sin Docker:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn goset_extraccion.api.main:app --port 8000 --app-dir src   # Componente A
uvicorn goset_recomendador.api.main:app --port 8001 --app-dir src # Componente B
```

## Endpoints
- Componente A: `GET /health`, `GET /methods`, `POST /extract`, `POST /end-to-end` (cartilla a extracción a recomendación).
- Componente B: `GET /health`, `POST /recomendar` (perfil a ranking explicable).

## Prueba end-to-end (sin API key, baseline regex)
```bash
pip install -r requirements.txt
PYTHONPATH=src python -m goset_extraccion.extractors.regex_extractor
pytest -q
```

## Reproducibilidad
- Seed fija (`GOSET_SEED`, por defecto 42) en `config.py`.
- Determinismo: temperatura 0 en los extractores LLM.
- **Datos reales fuera de git** (`data/raw`, `data/golden` en `.gitignore`).
  Las cartillas contienen datos personales: se trabajan localmente y anonimizados.

## Datos
- `data/raw/`,  documentos de entrada reales (NO versionado).
- `data/golden/`,  golden set anotado a mano (NO versionado).
- Condicionados públicos de pólizas: ver `scripts/download_polizas.py`.

## Estructura
```
src/goset_extraccion/
  schemas.py            # Modelos Pydantic (objetivo de extracción)
  config.py             # Settings + seed
  extractors/           # base + regex + zero shot + few shot + structured (propuesto)
  evaluation/metrics.py # F1, exact match, hallucination, null handling, latencia, coste
  api/main.py           # FastAPI + OpenAPI
  data_sources/polizas.py
tests/                  # pytest
```
