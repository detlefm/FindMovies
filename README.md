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

## Docker-Installation (Empfohlen)

Mit Docker können Sie die Anwendung als isolierten Container ausführen, ohne Python oder Node.js direkt auf Ihrem System installieren zu müssen. Dies ist der sauberste und empfohlene Weg für die meisten Benutzer.

### 1. Voraussetzungen

- **Docker Desktop:** Muss für Ihr Betriebssystem (z.B. Windows oder macOS) installiert und gestartet sein.

### 2. Wichtiger Hinweis zur Netzwerkkonfiguration

Die `server_url` in Ihrer `app.yaml` muss korrekt auf den EPG-Service verweisen. Je nachdem, wo dieser Dienst läuft, unterscheidet sich die Konfiguration:

- **Szenario 1: Der EPG-Service läuft auf demselben Computer wie Docker (dem "Host")**
  Wenn der EPG-Dienst lokal auf Ihrem Windows- oder Mac-Rechner unter `localhost:8089` erreichbar ist, müssen Sie im Container eine spezielle Adresse verwenden. Ändern Sie die `server_url` in Ihrer `app.yaml` zu:
  ```yaml
  server_url: "http://host.docker.internal:8089"
  ```
  **Grund:** `localhost` innerhalb eines Containers verweist auf den Container selbst, nicht auf Ihren Computer. `host.docker.internal` ist die von Docker bereitgestellte Adresse, um den Host-Rechner zu erreichen.

- **Szenario 2: Der EPG-Service läuft auf einem anderen Gerät im Netzwerk (z.B. NAS)**
  Wenn sich der Dienst auf einem anderen Server in Ihrem lokalen Netzwerk befindet (z.B. unter der IP `192.168.1.100`), können Sie diese IP-Adresse direkt in der `app.yaml` verwenden:
  ```yaml
  server_url: "http://192.168.1.100:8089"
  ```
  **Gut zu wissen:** Hierfür sind keine speziellen Docker-Netzwerkeinstellungen notwendig. Der Container kann standardmäßig auf andere Geräte in Ihrem lokalen Netzwerk zugreifen.

### 3. Docker-Image bauen

Öffnen Sie ein Terminal (wie PowerShell, CMD oder das macOS Terminal) im Hauptverzeichnis dieses Projekts und führen Sie den folgenden Befehl aus. Dieser Prozess kann einige Minuten dauern.

```bash
docker build -t findmovies-app .
```

### 4. Docker-Container starten

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
1.  Kopieren Sie `app.yaml` nach `C:\docker-data\findmovies\config\app.yaml` und passen Sie die Netzwerkkonfiguration wie oben beschrieben an.
2.  Kopieren Sie `backend/env.example` nach `C:\docker-data\findmovies\config\prod.env`.
3.  Bearbeiten Sie die `prod.env`-Datei:
    - Tragen Sie Ihre Secrets (API-Keys) ein.
    - Setzen Sie `LOG_TO_STDOUT=true`. Dies ist für den Docker-Betrieb dringend empfohlen.
4.  Kopieren Sie `data/blacklist.txt` nach `C:\docker-data\findmovies\data\blacklist.txt` (falls Sie eine verwenden).


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
mkdir -p ~\/docker-data\/findmovies\/{config,data,plugins}
```

**Schritt 2: Konfigurationsdateien vorbereiten**
1.  Kopieren Sie `app.yaml` nach `~/docker-data/findmovies/config/app.yaml` und passen Sie die Netzwerkkonfiguration wie oben beschrieben an.
2.  Kopieren Sie `backend/env.example` nach `~/docker-data/findmovies/config/prod.env`.
3.  Bearbeiten Sie die `prod.env`-Datei:
    - Tragen Sie Ihre Secrets (API-Keys) ein.
    - Setzen Sie `LOG_TO_STDOUT=true`. Dies ist für den Docker-Betrieb dringend empfohlen.

**Schritt 3: Container starten**
Führen Sie diesen Befehl in Ihrem Terminal aus:
```bash
docker run -d --name findmovies-app-instance \
  -p 8000:8000 \
  -v ~\/docker-data\/findmovies\/config\/app.yaml:\/app\/app.yaml \
  -v ~\/docker-data\/findmovies\/data:\/app\/data \
  -v ~\/docker-data\/findmovies\/plugins:\/app\/plugins \
  --env-file ~\/docker-data\/findmovies\/config\/prod.env \
  findmovies-app
```

---

Nach dem Start ist die Anwendung unter **http://localhost:8000** erreichbar.

### 5. Zugriff auf die Logs

Je nach Konfiguration in Ihrer `prod.env` -Datei werden die Logs unterschiedlich ausgegeben:

- **Wenn `LOG_TO_STDOUT=true` (Empfohlen für Docker):**
  Die Logs werden vom Container an Docker weitergeleitet. Sie können sie jederzeit mit diesem Befehl einsehen:
  ```bash
  docker logs findmovies-app-instance
  ```
  Um die Logs live zu verfolgen, fügen Sie den `-f` (follow) Flag hinzu:
  ```bash
  docker logs -f findmovies-app-instance
  ```

- **Wenn `LOG_TO_STDOUT=false` (Standard für lokale Ausführung):**
  Die Anwendung schreibt in eine Datei `app.log`. Wenn Sie die Docker-Anleitung befolgt haben, finden Sie diese auf Ihrem Host-Rechner unter:
  `C:\docker-data\findmovies\data\app.log` (für Windows) oder `~/docker-data/findmovies/data/app.log` (für macOS).


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