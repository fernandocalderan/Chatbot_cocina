# API Contracts

## Chat response (`POST /v1/chat/send`)

Respuesta estándar que debe manejar el widget/panel:

```json
{
  "message": "...",                      // texto del bot (sin IA si está en ahorro/bloqueo)
  "quota_status": "ACTIVE | SAVING | LOCKED",
  "saving_mode": true,                   // presente cuando quota_status=SAVING
  "needs_upgrade_notice": true           // muestra banner/CTA de upgrade
}
```

- Si el tenant está en `LOCKED`, el backend responde con un mensaje de fallback sin IA:
  ```json
  {
    "message": "Has alcanzado el límite de IA de tu plan. Puedes seguir con respuestas básicas o actualizar tu plan.",
    "quota_status": "LOCKED",
    "saving_mode": false,
    "needs_upgrade_notice": true,
    "cta": {"label": "Mejorar plan", "action": "upgrade"}
  }
  ```
- Campo adicional `quota_details` puede aparecer con información extendida (coste, límite, etc.) para panel/telemetría.
