# Backend (FastAPI)

## Setup rápido
1) Crear entorno y dependencias:
```
make dev-install
```
2) Levantar stack local (api+db+redis):
```
docker compose up -d
```
3) Migrar y seed de demo:
```
make migrate
make seed
```

Healthcheck: `http://localhost:8100/v1/health` (ver puertos en `docker-compose.yml`).

## Notas
- Configuración en `.env` (copiado de `.env.example`).
- Alembic ya está inicializado en `backend/alembic`, metadata en `app/db/base.py`.
