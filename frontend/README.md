# Svelte 5 Film EPG App

Dies ist eine mit Svelte 5 und Vite erstellte Single-Page-Anwendung zur Interaktion mit der Film-EPG-API.

## Voraussetzungen

- [Node.js](https://nodejs.org/) (Version 18 oder höher)
- [npm](https://www.npmjs.com/) (wird mit Node.js geliefert)

## Setup und Start

1.  **Abhängigkeiten installieren:**
    Navigieren Sie in das `frontend`-Verzeichnis und führen Sie den folgenden Befehl aus, um die notwendigen Pakete zu installieren:
    ```bash
    npm install
    ```

2.  **Entwicklungsserver starten:**
    Starten Sie den Vite-Entwicklungsserver mit:
    ```bash
    npm run dev
    ```
    Die Anwendung ist nun unter `http://localhost:5173` (oder einem anderen von Vite zugewiesenen Port) erreichbar.

## API-Erreichbarkeit

Die Anwendung erwartet, dass die FastAPI-Endpunkte (`/info`, `/collect` etc.) auf demselben Host und Port laufen. Die `vite.config.js` ist so konfiguriert, dass API-Anfragen im Entwicklungsmodus an `http://127.0.0.1:8000` weitergeleitet werden. Stellen Sie sicher, dass Ihr Backend-Server unter dieser Adresse läuft, oder passen Sie den Proxy in der `vite.config.js` entsprechend an.

## Build für die Produktion

Um eine optimierte Version der App für das Deployment zu erstellen, führen Sie aus:

```bash
npm run build
```

Die fertigen Dateien werden im `dist`-Verzeichnis abgelegt.