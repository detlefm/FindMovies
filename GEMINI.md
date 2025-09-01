

### Projektkontext
**Frontend-Anwendung** (`/frontend`):  
Bietet 4 Interaktionsbuttons zur Verwaltung einer Filmliste:
1. **Collect starten** – Initiiert Neuerstellung der Filmliste (löscht bestehende Liste; Langzeitoperation)
2. **Filme laden** – Ruft gespeicherte Filmliste vom Backend ab (ermöglicht Bearbeitung im Frontend)
3. **Liste speichern** – Übergibt die modifizierte Frontend-Liste an das Backend (persistiert Änderungen)
4. **Timer erstellen** – Konvertiert die Backend-Filmliste in Timer für einen externen Service

---

### Backend-API-Endpunkt
**GET `/info`**  
Liefert Statusdaten als JSON-Objekt mit folgenden Feldern:
```json
{
  "modified": "Optional[String] (ISO-Datum/Uhrzeit)",  // Zeitpunkt der letzten Filmlistenerstellung
  "count": "Integer",                                  // Anzahl der Einträge in der aktuellen Liste
  "running": "Boolean",                                // true = Collect-Operation läuft
  "run_started": "Optional[String] (ISO-Datum/Uhrzeit)", // Startzeitpunkt der aktuellen Operation
  "run_progress": "Optional[Float] [0.0–1.0]"          // Fortschritt der laufenden Operation
}
```

---

### Frontend-Komponente: StatusBar
Anzuzeigende Statusfelder (in `src/components/StatusBar.svelte`):
1. **Status** – Betriebsstatus des Systems
2. **Filme auf Server** – Anzahl der gespeicherten Filme
3. **Letzte Änderung** – Zeitpunkt der letzten Listenaktualisierung

---

### Button-Logik (Aktiv/Inaktiv)
| Button           | Aktivierungsbedingung                          | Backend-Indikator       |
|------------------|------------------------------------------------|-------------------------|
| **Collect starten** | Immer, außer während laufendem Collect         | `running == false`      |
| **Filme laden**     | Wenn eine Filmliste existiert                  | `count > 0`             |
| **Liste speichern** | Wenn eine Liste im Frontend geladen ist        | (Frontend-Intern)       |
| **Timer erstellen** | Wenn eine Filmliste existiert                  | `count > 0`             |

---

### Statusanzeige-Logik
**Polling-Anforderung**:  
- Statusdaten müssen kontinuierlich abgefragt werden (auch während laufendem Collect).

**Feldinhalte**:
- **Status**:
  - Standard: `"Inaktiv"`
  - Bei laufendem Collect:`"Running  {progress}%"`  
    - `{progress}`: `run_progress * 100` (z.B. `0.1 → 10%`)

- **Filme auf Server**:
  - Wert: `count` (bei laufendem Collect oder leerer Liste: `0`)

- **Letzte Änderung**:
  - Wert: `modified` (Erstellungsdatum der Filmliste oder start des collect Vorgangs)

---

### Kritischer Fehler
keine kritischen Fehler
---

