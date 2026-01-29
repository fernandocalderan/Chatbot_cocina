# Smoke Fase 2 (2 min)

## 0) Stack
```bash
cd /home/fernando/Escritorio/Chatbot_cocina
docker compose up -d db redis
docker compose up -d --build api
```

## 1) Migraciones
```bash
docker compose exec api bash -lc "alembic upgrade heads"
```

## 2) Health + catálogo
```bash
export BASE_URL="http://localhost:8100"
export API_KEY="$ADMIN_API_TOKEN"

curl -s "$BASE_URL/v1/health" | jq .
curl -s -H "x-api-key: $API_KEY" \
  "$BASE_URL/v1/catalog?include_empty_scopes=true&include_drafts=true&include_templates=true" \
  | jq '.verticals | length'
```

## 3) Crear scope
```bash
export VERTICAL_KEY="clinics_private"
export SCOPE_KEY="smoke_scope_$(date +%H%M)"

curl -s -H "x-api-key: $API_KEY" -H "Content-Type: application/json" \
  -d "{\"vertical_key\":\"$VERTICAL_KEY\",\"scope_key\":\"$SCOPE_KEY\",\"display_name\":\"Smoke Scope\",\"description\":\"smoke test\"}" \
  "$BASE_URL/v1/scopes" | jq .
```

## 4) Importar flow base + publicar (admin)

```bash
cat > /tmp/flow_base_smoke.json <<'JSON'
{
  "start_block": "welcome",
  "blocks": {
    "welcome": {"type":"message","text":"Hola, smoke test.","end": true}
  }
}
JSON

# Import (requiere ADMIN_API_TOKEN)
curl -s -H "x-api-key: $API_KEY" \
  -F "file=@/tmp/flow_base_smoke.json;type=application/json" \
  -F "vertical_key=$VERTICAL_KEY" \
  -F "scope_key=$SCOPE_KEY" \
  -F "flow_kind=base" \
  -F "owner_type=GLOBAL" \
  "$BASE_URL/v1/admin/flows/import" | jq .

# Publish (requiere ADMIN_API_TOKEN)
curl -s -H "x-api-key: $API_KEY" \
  -X POST "$BASE_URL/v1/admin/flows/<FLOW_ID>/publish" | jq .
```

## 5) Panel
```bash
cd /home/fernando/Escritorio/Chatbot_cocina/admin_panel
source .venv/bin/activate
python -m streamlit run app.py
```

Checklist UI:
- Scopes: muestra `NO_FLOW_YET` → luego `DRAFT_ONLY` → `PUBLISHED_OK`.
- Flows: aparece el flow publicado.
- Tenants: el scope refleja el estado correcto.

## Wizard 60s (UI)
1) Abrir **Wizard (60s)** en el panel (solo SUPER_ADMIN).
2) Vertical existente: `clinics_private`.
3) Crear scope: `wizard_demo_<HHMM>`.
4) Subir flow base JSON simple y **Importar como borrador**.
5) **Publicar ahora** (checkbox + escribir PUBLICAR).
6) Confirmar en **Scopes** que el estado es `PUBLISHED_OK`.
