# Chatbot Widget

Widget embebible (React + Vite) listo para Staging/Prod.

## Build y artefactos
- Instala dependencias: `npm install`
- Build estable: `npm run build`
- Salida en `dist/`:
  - `chat-widget.js`
  - `chat-widget.css`
- Publica ambos en tu CDN/hosting. Ejemplo URLs productivas:
  - `https://cdn.opunnence.com/chat-widget.js`
  - `https://cdn.opunnence.com/chat-widget.css`

## Contrato canónico (Widget ↔ Backend)
- El widget **no** decide flujos ni textos comerciales.
- El widget solo:
  - pide `GET /v1/widget/runtime` (config + mensajes ensamblados)
  - pide `GET /v1/widget/config`
  - crea sesión `POST /v1/widget/session`
  - envía mensajes `POST /v1/widget/message`
  - agenda slots `GET /v1/widget/agenda/slots`
  - confirma cita `POST /v1/widget/agenda/confirm`

## Snippet final (webs / sites)
Incluye JS y CSS desde el CDN, añade el contenedor y usa el token WIDGET emitido desde el panel tenant.
```html
<script src="https://cdn.opunnence.com/chat-widget.js"></script>
<link rel="stylesheet" href="https://cdn.opunnence.com/chat-widget.css">

<div id="widget-root"></div>

<script>
  ChatWidget.init({
    apiUrl: "https://api.opunnence.com",
    widgetToken: "WIDGET_JWT_TOKEN",
    startOpen: false
  });
</script>
```
Colócalo al final del `<body>` (o tras el contenedor) para asegurar que `#widget-root` existe.

En local (Vite): `VITE_API_BASE=http://localhost:8100 VITE_WIDGET_TOKEN=WIDGET_JWT_TOKEN npm run dev`.

## Parámetros admitidos en `ChatWidget.init`
- `apiUrl` (**string, requerido**): endpoint base de la API del chatbot (ej. staging o prod).
- `widgetToken` (**string, requerido**): JWT tipo `WIDGET` (emitido desde el panel tenant).
- `language` (**string, opcional**): idioma UI (`es`, `pt`, `en`, `ca`). El idioma conversacional lo decide el backend.
- `startOpen` (**boolean, opcional**): `true` abre la ventana al cargar, `false` muestra solo la burbuja. Ejemplo: `startOpen: true`.

## Notas para Staging/Prod
- Usa el mismo paquete JS/CSS en ambos entornos y cambia solo `apiUrl`.
- Controla cache/CDN versionando la ruta o con headers de invalicación cuando publiques una nueva build.
