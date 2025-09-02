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
2.  **`.env`:** Kopieren Sie `env.example` in das Hauptverzeichnis und benennen Sie es in `prod.env` um (siehe docker run). Passen Sie die Werte darin an.

### 3. Anwendung starten

```bash
# Stellen Sie sicher, dass Ihr virtuelles Environment (.venv) noch aktiviert ist
python backend/main.py
```

Der Server startet und ist nun unter **http://localhost:8000** in Ihrem Browser erreichbar.

---

## Docker-Installation (Empfohlen)

Mit Docker können Sie die Anwendung als isolierten Container ausführen, ohne Python oder Node.js direkt auf Ihrem System installieren zu müssen. Dies ist der sauberste und empfohlene Weg für die meisten Benutzer.

### 1. Voraussetzungen

- **Docker Desktop:** Muss für Ihr Betriebssystem (z.B. Windows oder macOS) installiert und gestartet sein.

### 2. Docker-Image bauen

Öffnen Sie ein Terminal (wie PowerShell, CMD oder das macOS Terminal) im Hauptverzeichnis dieses Projekts und führen Sie den folgenden Befehl aus. Dieser Prozess kann einige Minuten dauern.

```bash
docker build -t findmovies-app .
```

### 3. Docker-Container starten

Die folgenden Anleitungen zeigen den empfohlenen Weg, den Container mit externen Ordnern für Konfiguration und Daten zu starten. Dies ist Best Practice und macht Ihr Setup sauber und wartbar.

#### Anleitung für Windows

**Schritt 1: Verzeichnisse erstellen**
Erstellen Sie die folgende Ordnerstruktur. Sie können dies im Windows Explorer oder mit diesen Befehlen in einer PowerShell tun:
```powershell
mkdir C:\docker-data\findmovies\config
mkdir C:\docker-data\findmovies\data
mkdir C:\docker-data\findmovies\plugins
```

**Schritt 2: Konfigurationsdateien vorbereiten**
1.  Kopieren Sie `app.yaml` nach `C:\docker-data\findmovies\config\app.yaml`.
2.  Kopieren Sie `env.example` nach `C:\docker-data\findmovies\config\prod.env`.
3.  Bearbeiten Sie die `prod.env`-Datei und tragen Sie Ihre Secrets ein.

**Schritt 3: Container starten**
Führen Sie diesen Befehl in Ihrer PowerShell aus:
```powershell
docker run -d --name findmovies-app-instance \
  -p 8000:8000 \
  -v "C:/docker-data/findmovies/config/app.yaml:/app/app.yaml" \
  -v "C:/docker-data/findmovies/data:/app/data" \
  -v "C:/docker-data/findmovies/plugins:/app/plugins" \
  --env-file "C:/docker-data/findmovies/config/prod.env" \
  findmovies-app
```

---

#### Anleitung für macOS

**Schritt 1: Verzeichnisse erstellen**
Öffnen Sie das Terminal und erstellen Sie die Ordner in Ihrem Home-Verzeichnis (`~`):
```bash
# Der -p Flag erstellt die übergeordneten Verzeichnisse, falls sie nicht existieren
mkdir -p ~/docker-data/findmovies/{config,data,plugins}
```

**Schritt 2: Konfigurationsdateien vorbereiten**
1.  Kopieren Sie `app.yaml` nach `~/docker-data/findmovies/config/app.yaml`.
2.  Kopieren Sie `env.example` nach `~/docker-data/findmovies/config/prod.env`.
3.  Bearbeiten Sie die `prod.env`-Datei und tragen Sie Ihre Secrets ein.

**Schritt 3: Container starten**
Führen Sie diesen Befehl in Ihrem Terminal aus:
```bash
docker run -d --name findmovies-app-instance \
  -p 8000:8000 \
  -v ~/docker-data/findmovies/config/app.yaml:/app/app.yaml \
  -v ~/docker-data/findmovies/data:/app/data \
  -v ~/docker-data/findmovies/plugins:/app/plugins \
  --env-file ~/docker-data/findmovies/config/prod.env \
  findmovies-app
```

---

Nach dem Start ist die Anwendung unter **http://localhost:8000** erreichbar.

Um den Container zu stoppen, können Sie `docker stop findmovies-app-instance` ausführen. Um ihn neu zu starten, `docker start findmovies-app-instance`.


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
