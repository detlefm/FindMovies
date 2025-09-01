---

```markdown
# 📦 Installation

1. **Inhalt entpacken**  
   Entpacke die ZIP‑Datei in ein **neues Verzeichnis** deiner Wahl.

2. **Verzeichnis in der Kommandozeile öffnen**  
   Öffne dieses Verzeichnis entweder mit  
   - der **Eingabeaufforderung (CMD)** oder  
   - **PowerShell**  
   *(Unter Windows 11 öffnet sich ggf. das Windows Terminal mit einem CMD‑ oder PowerShell‑Tab.)*

3. **Virtuelle Umgebung erstellen**
```
   python -m venv .venv
   ```

4. **Virtuelle Umgebung aktivieren**  
   - **PowerShell**:
   ```
​     .venv\Scripts\Activate.ps1
     ```
   - **CMD**:
     ```
​     .venv\Scripts\activate.bat
     ```

5. **Benötigte Pakete installieren**
     ```
   pip install -r requirements.txt
   ```

6. **Beispiel-Umgebungsdatei kopieren**
   ```
   copy env.txt .env
   ```

7. **`.env` anpassen**  
   - Entferne die Einträge zu AI‑Providern, die du **nicht** nutzen möchtest.  
   - Füge für die gewünschten Provider die entsprechenden **API‑Keys** hinzu.  
   - Aktuell unterstützt: `OPENAI`, `GEMINI`, `OPENROUTER`, `OLLAMA`  
     > Auch für lokale Ollama‑Anfragen wird ein API‑Key benötigt (Inhalt beliebig).  
   - `TMDB_TOKEN` wird derzeit nicht benötigt, da keine Daten von TMDB geladen werden.

8. **`app.yaml` bearbeiten**  
   - `server_url`: URL zu deinem MediaServer eintragen  
   - `ai_model`: leer lassen oder Modellnamen eintragen  
     *(Wenn leer, werden keine AI‑Anfragen ausgeführt)*  
   - `ai_provider`: Einträge entfernen, für die kein API‑Key vorhanden ist bzw. die nicht genutzt werden sollen.

9. **Script starten**
   ```
   python .\find_movies.py [Optionen]
   ```

---

## 📖 Hilfe anzeigen
   ```
python .\find_movies.py --help
```

**Ausgabe:**
```
Usage: find_movies.py [OPTIONS] COMMAND [ARGS]...

  CLI-Einstiegspunkt.

Options:
  --output   Log-Ausgabe auf die Konsole.
  --debug    Debugmodus aktivieren.
  --help     Show this message and exit.

Commands:
  collect      Filme sammeln und kategorisieren.
  createtimer  Timer auf Basis der gesammelten Filme anlegen.
```

### 🔍 Zusätzliche Hinweise zu Befehlen
- `collect --dest DATEINAME` → speichert Ergebnis in angegebener Datei  
- `createtimer --src DATEINAME --model AI-MODELNAME` → überschreibt `ai_model` aus `app.yaml`  
- `--debug` → derzeit ohne Funktion  
- `--output` → leitet Logging zusätzlich auf die Konsole

---

## 🎬 Viewer für `movies.jsonl`
Im Verzeichnis befindet sich eine **Single‑HTML‑App** mit dem Namen **`Viewer.html`**.  
Damit kannst du die erzeugte **`movies.jsonl`**‑Datei bequem ansehen.

- **Start über die Kommandozeile**:
```
  start Viewer.html
  ```
- **Oder direkt im Browser öffnen** (Doppelklick auf die Datei)

Danach einfach die gewünschte `movies.jsonl`‑Datei auswählen und ansehen.
  ```
