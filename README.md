# FindMovies Movie Collector

Dieses Projekt ermöglicht das Sammeln, Filtern und Verwalten von Filminformationen aus einem EPG (Electronic Program Guide). Es besteht aus einem FastAPI-Backend für die Datenverarbeitung und einem Svelte-Frontend zur Interaktion.

## Features

- **Filme sammeln:** Startet einen Prozess, um Filmdaten von einer konfigurierten Quelle zu laden.
- **Filtern & Kategorisieren:** Wendet eine Reihe von Filtern an und kann eine KI-basierte Kategorisierung durchführen.
- **Web-Interface:** Eine Svelte-basierte Benutzeroberfläche zur Steuerung der Prozesse und zur Anzeige der Ergebnisse.
- **Timer-Erstellung:** Kann die gefilterte Filmliste an einen externen Service zur Erstellung von Aufnahme-Timern übergeben.
- **Erweiterbar:** Unterstützt benutzerdefinierte Filter-Plugins.

---

## Verteilungsoptionen

Es gibt drei Möglichkeiten, dieses Projekt zu nutzen:

1.  **Manuelle Installation:** Für Entwickler, die den Code direkt ausführen oder anpassen möchten.
2.  **Docker-Installation (Empfohlen):** Der einfachste und sauberste Weg, die Anwendung als isolierten Dienst auszuführen.
3.  **Release-Bundle:** Ein vorkonfigurierter Ordner für Benutzer, die eine einfache, klickbare Startlösung ohne Docker bevorzugen.

---

## Manuelle Installation

### 1. Voraussetzungen

Stellen Sie sicher, dass die folgende Software auf Ihrem System installiert ist:

- **Python:** Version 3.10 oder neuer.
- **Node.js:** Version 18 oder neuer (inklusive `npm`).
- **uv:** Ein schneller Python-Paketmanager. Falls noch nicht installiert, können Sie es mit `pip install uv` installieren.

### 2. Setup

Führen Sie die folgenden Schritte aus, um das Projekt lokal einzurichten.

#### a) Repository klonen

```bash
git clone <URL_des_GitHub_Repos>
cd FindMovies
```

#### b) Backend einrichten

```bash
# 1. Virtuelles Environment im Ordner .venv erstellen
uv venv

# 2. Environment aktivieren
#    Windows (CMD/PowerShell):
.venv\Scripts\activate
#    Linux/macOS:
#    source .venv/bin/activate

# 3. Python-Abhängigkeiten installieren
uv pip install -r requirements.txt
```

#### c) Frontend einrichten

```bash
# 1. In das Frontend-Verzeichnis wechseln
cd frontend

# 2. Node.js-Abhängigkeiten installieren
npm install

# 3. Frontend-Anwendung bauen
npm run build

# 4. Zurück ins Hauptverzeichnis wechseln
cd ..
```

#### d) Konfiguration

1.  **`app.yaml`:** Passen Sie diese Datei bei Bedarf an Ihre Umgebung an.
2.  **`.env`:** Kopieren Sie `backend/env.example` in das Hauptverzeichnis des Projekts und benennen Sie die Kopie in `.env` um. Passen Sie die Werte in dieser neuen `.env`-Datei an. Für die lokale Ausführung wird standardmässig in eine Datei geloggt (`LOG_TO_STDOUT=false`).

### 3. Anwendung starten

```bash
# Stellen Sie sicher, dass Ihr virtuelles Environment (.venv) noch aktiviert ist
python backend/main.py
```

Der Server startet und ist nun unter **http://localhost:8000** in Ihrem Browser erreichbar.

### 4. Zugriff auf die Logs

Je nach Einstellung in Ihrer `.env`-Datei werden die Logs unterschiedlich ausgegeben:

- **Wenn `LOG_TO_STDOUT=false` (Standard):**
  Die Anwendung schreibt die Logs in die Datei `data/app.log` im Projektverzeichnis.

- **Wenn `LOG_TO_STDOUT=true`:**
  Die Logs werden direkt in dem Terminal ausgegeben, in dem Sie die Anwendung mit `python backend/main.py` gestartet haben.

---

## Docker-Installation

Mit Docker können Sie die Anwendung als isolierten Container ausführen, ohne Python oder Node.js direkt auf Ihrem System installieren zu müssen.

### Docker Compose (Empfohlene Methode)

Dies ist der einfachste und sauberste Weg, die Anwendung zu betreiben. Docker Compose verwendet eine Konfigurationsdatei (`docker-compose.yml`) und eine Umgebungsdatei (`docker.env`) für die Konfiguration.

**Konfliktvermeidung:** Um einen Konflikt mit der `.env`-Datei zu vermeiden, die für die manuelle Ausführung verwendet wird, nutzt Docker Compose hier die Datei `docker.env`.

#### 1. Voraussetzungen

- **Docker Desktop:** Muss für Ihr Betriebssystem (z.B. Windows oder macOS) installiert und gestartet sein. Die moderne Version `docker compose` (V2) ist hier standardmäßig enthalten.

#### 2. Konfiguration

**Schritt 1: Verzeichnisse erstellen**
Erstellen Sie eine Ordnerstruktur für Ihre Konfiguration und Daten. Diese Ordner sollten **außerhalb** des Projektverzeichnisses liegen, um sie bei Updates zu schützen.

*Beispiel für Windows (PowerShell):*
```powershell
mkdir C:\docker-data\findmovies\config
mkdir C:\docker-data\findmovies\data
mkdir C:\docker-data\findmovies\plugins
```

*Beispiel für macOS/Linux:*
```bash
mkdir -p ~/docker-data/findmovies/{config,data,plugins}
```

**Schritt 2: Konfigurationsdateien vorbereiten**
1.  Kopieren Sie `app.yaml` in Ihr Konfigurationsverzeichnis (z.B. `C:\docker-data\findmovies\config\app.yaml`) und passen Sie die Netzwerkkonfiguration an (siehe Hinweis unten).
2.  Kopieren Sie `backend/env.example` als `prod.env` in Ihr Konfigurationsverzeichnis (z.B. `C:\docker-data\findmovies\config\prod.env`).
3.  Bearbeiten Sie die `prod.env`-Datei:
    - Tragen Sie Ihre Secrets (API-Keys) ein.
    - Setzen Sie `LOG_TO_STDOUT=true`. Dies ist für den Docker-Betrieb zwingend erforderlich.
4.  Kopieren Sie `data/blacklist.txt` in Ihr Datenverzeichnis (falls Sie eine verwenden).

**Schritt 3: Pfade für Docker Compose konfigurieren**
1.  Kopieren Sie die Datei `docker.env.example` zu `docker.env` im Hauptverzeichnis des Projekts.
2.  Öffnen Sie die neue `docker.env`-Datei und passen Sie die Pfade `CONFIG_PATH`, `DATA_PATH` und `PLUGINS_PATH` an die im ersten Schritt erstellten Verzeichnisse an.

**Schritt 4: Docker-Image bauen und Container starten**
Öffnen Sie ein Terminal im Hauptverzeichnis des Projekts und führen Sie folgende Befehle aus. Wir verwenden hier die moderne `docker compose` Syntax (mit Leerzeichen statt Bindestrich). Die `--env-file`-Option teilt Docker Compose mit, wo die Konfiguration der Pfade zu finden ist.

```bash
# Baut das Docker-Image (nur beim ersten Mal oder nach Code-Änderungen nötig)
docker compose --env-file docker.env build

# Startet den Container im Hintergrund
docker compose --env-file docker.env up -d
```

Die Anwendung ist nun unter **http://localhost:8000** erreichbar.

**Zugriff auf die Logs**
```bash
docker compose --env-file docker.env logs -f
```

**Container stoppen**
```bash
docker compose --env-file docker.env down
```

#### Wichtiger Hinweis zur Netzwerkkonfiguration

Die `server_url` in Ihrer `app.yaml` muss korrekt auf den EPG-Service verweisen.
- **EPG-Service auf demselben Computer:** Verwenden Sie `http://host.docker.internal:8089`.
- **EPG-Service im Netzwerk (z.B. NAS):** Verwenden Sie die IP-Adresse des Geräts, z.B. `http://192.168.1.100:8089`.

---


### Manueller `docker run` (Alternative Methode)

Diese Methode wird nicht empfohlen, da sie zu langen und fehleranfälligen Befehlen führt. Verwenden Sie sie nur, wenn Sie Docker Compose nicht nutzen können oder wollen.

Die Vorbereitung der Verzeichnisse und Konfigurationsdateien erfolgt wie im Abschnitt "Docker Compose" beschrieben.

**1. Docker-Image bauen**

```bash
docker build -t findmovies-app .
```

**2. Container starten**

Der `docker run`-Befehl kann durch die vielen Parameter sehr lang werden. Lange, mehrzeilige Befehle können in manchen Terminals (insbesondere unter Windows) Probleme verursachen.

Es gibt hierfür zwei Lösungsansätze:

1.  **Den Befehl in einer einzigen Zeile ausführen:** Dies ist die einfachste Methode, um Kompatibilitätsprobleme zu vermeiden.
2.  **Ein Start-Skript erstellen:** Für eine wiederverwendbare Lösung können Sie den Befehl in einer Skriptdatei (`.cmd` für Windows oder `.sh` für macOS/Linux) speichern.


#### Anleitung für Windows

Führen Sie einen der folgenden Befehle in Ihrer PowerShell aus.

**Option A: Mehrzeiliger Befehl (für moderne Terminals wie Windows Terminal)**

Beachten Sie den Backtick (`` ` ``) am Ende jeder Zeile, der PowerShell signalisiert, dass der Befehl auf der nächsten Zeile weitergeht.

```powershell
docker run -d --name findmovies-app-instance `
  -p 8000:8000 `
  -v "C:/docker-data/findmovies/config/app.yaml":/app/app.yaml `
  -v "C:/docker-data/findmovies/data":/app/data `
  -v "C:/docker-data/findmovies/plugins":/app/plugins `
  --env-file "C:/docker-data/findmovies/config/prod.env" `
  findmovies-app
```

**Option B: Einzeiliger Befehl (sicherste Methode)**

Kopieren Sie diesen Befehl als eine einzige lange Zeile in Ihr Terminal.

```powershell
docker run -d --name findmovies-app-instance -p 8000:8000 -v "C:/docker-data/findmovies/config/app.yaml":/app/app.yaml -v "C:/docker-data/findmovies/data":/app/data -v "C:/docker-data/findmovies/plugins":/app/plugins --env-file "C:/docker-data/findmovies/config/prod.env" findmovies-app
```

---

#### Anleitung für macOS

**Option A: Mehrzeiliger Befehl**

Der Backslash (`\`) am Zeilenende signalisiert der Shell, dass der Befehl weitergeht.

```bash
docker run -d --name findmovies-app-instance \
  -p 8000:8000 \
  -v ~\/docker-data\/findmovies\/config\/app.yaml:\/app\/app.yaml \
  -v ~\/docker-data\/findmovies\/data:\/app\/data \
  -v ~\/docker-data\/findmovies\/plugins:\/app\/plugins \
  --env-file ~\/docker-data\/findmovies\/config\/prod.env \
  findmovies-app
```

**Option B: Einzeiliger Befehl**

```bash
docker run -d --name findmovies-app-instance -p 8000:8000 -v ~\/docker-data\/findmovies\/config\/app.yaml:\/app\/app.yaml -v ~\/docker-data\/findmovies\/data:\/app\/data -v ~\/docker-data\/findmovies\/plugins:\/app\/plugins --env-file ~\/docker-data\/findmovies\/config\/prod.env findmovies-app
```

**Zugriff auf die Logs**
```bash
docker logs -f findmovies-app-instance
```

**Container stoppen**
```bash
docker stop findmovies-app-instance
```


## Release-Bundle (für einfache Nutzung)

Diese Methode ist für Benutzer gedacht, die eine einfache "Kopieren und Starten"-Lösung ohne Docker bevorzugen.

### Release-Bundle erstellen

Sie können ein Release-Bundle in einem beliebigen Ordner mit dem folgenden Befehl erstellen. Das Skript sammelt alle notwendigen Dateien (gebautes Frontend, Backend, Start-Skripte) an einem Ort.


```bash
# Stellen Sie sicher, dass Sie python installiert haben
python scripts/create_release.py <destionationfolder>
```

oder auf Windows mit
``` cmd
.\scripts\create_release.cmd <destionationfolder>
```

### Release-Bundle verwenden

Folgen Sie den Anweisungen in der `README.md`-Datei innerhalb dieses Ordners, um die Anwendung zu konfigurieren und zu starten.

---

## Projektstruktur

- **/backend:** Enthält die FastAPI-Anwendung.
- **/frontend:** Enthält die Svelte-Anwendung.
- **/data:** Standard-Speicherort für Laufzeitdaten.
- **/plugins:** Hier können benutzerdefinierte Filter als `.py`-Dateien abgelegt werden.
- **/scripts:** Enthält Hilfsskripte wie `create_release.py`.