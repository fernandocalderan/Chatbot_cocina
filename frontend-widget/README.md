# Chatbot Widget

Widget embebible (React + Vite) listo para Staging/Prod.

## Build y artefactos
- Instala dependencias: `npm install`
- Build estable: `npm run build`
- Salida en `dist/`:
  - `chat-widget.js`
  - `chat-widget.css`
  - `chat-widget.umd.cjs`
- Publica ambos en tu CDN/hosting. Ejemplo URLs productivas:
  - `https://cdn.opunnence.com/chat-widget.js`
  - `https://cdn.opunnence.com/chat-widget.css`

## Snippet final (tiendas / sites)
Incluye JS y CSS desde el CDN, añade el contenedor y ejecuta la init:
```html
<script src="https://cdn.opunnence.com/chat-widget.js"></script>
<link rel="stylesheet" href="https://cdn.opunnence.com/chat-widget.css">

<div id="widget-root"></div>

<script>
  ChatWidget.init({
    apiUrl: "https://api.opunnence.com/v1",
    tenantTheme: "blue"
  });
</script>
```
Colócalo al final del `<body>` (o tras el contenedor) para asegurar que `#widget-root` existe.

## Parámetros admitidos en `ChatWidget.init`
- `apiUrl` (**string, requerido**): endpoint base de la API del chatbot (ej. staging o prod).
- `tenantTheme` (**string, opcional**): paleta principal. Valores soportados: `blue`, `green`, `black` (sin valor usa el tema por defecto).
- `language` (**string, opcional**): `es` o `en`. Cualquier otro valor hace fallback a `es`. Ejemplo: `language: "en"`.
- `startOpen` (**boolean, opcional**): `true` abre la ventana al cargar, `false` muestra solo la burbuja. Ejemplo: `startOpen: true`.

## Notas para Staging/Prod
- Usa el mismo paquete JS/CSS en ambos entornos y cambia solo `apiUrl`.
- Controla cache/CDN versionando la ruta o con headers de invalicación cuando publiques una nueva build.
