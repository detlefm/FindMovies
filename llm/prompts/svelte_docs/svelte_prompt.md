### Prompt zur Erstellung einer Svelte‑5‑App für die Film‑API

```text
Rolle:
Du bist ein erfahrener Frontend‑Engineer. Erstelle eine vollständige, lauffähige HTML/CSS/JavaScript‑App mit Svelte 5 (kein TypeScript, kein SvelteKit), die die unten beschriebenen FastAPI‑Endpunkte bedient. Schreibe sauberen, gut kommentierten Code, verständliche deutsche UI‑Texte und klare Status-/Fehlermeldungen. Nutze Svelte‑5‑Idiome (z. B. Runes wie $state, $derived, $effect, falls passend) und strukturierte Komponenten. Liefere den kompletten Source Code mit Dateistruktur, allen .svelte‑ und .js‑Dateien, sowie minimaler CSS‑Gestaltung (responsive, barrierearm, übersichtlich).

API‑Endpunkte (gegeben):
- POST /collect?model=<optional>
  Zweck: Langlaufende Operation zum Sammeln und Kategorisieren von Filmen. Ein neuer Lauf bricht einen laufenden ab und startet neu.
- GET /createtimer
  Zweck: Timer auf Basis der gesammelten Filme erstellen. Antwort ist ein TimerStatus‑Objekt (Form frei; zeige die wichtigsten Felder roh an).
- GET /movies
  Zweck: Liste der gesammelten Filme als JSON (Array) zurückgeben.
- POST /movies
  Zweck: Die vorhandene Filmliste auf dem Server vollständig ersetzen. Erwarteter Body: { "movies": Movie[] }.
- GET /info
  Zweck: Status der Filmliste. Liefert mindestens: letztes Änderungsdatum, Anzahl der Filme und ggf. Info, dass ein Suchlauf gerade läuft mit Startzeit.
  Hinweis: Falls Feldnamen unbekannt, normalisiere defensiv wie folgt:
    { modified: string|null, count: number, running: boolean, run_started: string|null }
  und dokumentiere die Normalisierung im Code (Mapping/Defaults).

Filmdatensatz (Beispiel):
{
  "eventid": 63919,
  "content": 16,
  "pdc": 541662,
  "charset": 255,
  "title": "Käthe ...",
  "event": "Spielfilm Deutschland 2019",
  "description": "Im zweiten Film von....\n\n[16:9] [5.1] [SUB] [AD] [6+]   [PDC 16.08. 15:30]",
  "start": "2025-08-16T15:30:00",
  "stop": "2025-08-16T17:00:00",
  "epgchannel": "562954315180093",
  "tv_channel": "2359890582721931325",
  "tv_name": "Das Erste HD",
  "contentinfo": ["Movie", "Movie/Drama"],
  "hash": "e296ef54cf3962aa83fd2a1ad1160f77"
}

Anforderungen an die App:
1) Initiales Verhalten
   - Beim Start: GET /info abrufen, Status sichtbar anzeigen.
   - Statusanzeige enthält:
     • Ob eine Filmliste existiert (count > 0 => vorhanden).
     • Letztes Änderungsdatum (formatiert).
     • Anzahl der Filme.
     • Ob ein Suchlauf läuft, inkl. Startzeit (formatiert).
   - Implementiere ein sanftes Polling (z. B. alle 5–10 s) von /info, solange running = true, um den Status live zu aktualisieren. Stoppe Polling, wenn running = false.

2) Collect starten (/collect)
   - Button „Collect starten“ ist immer aktiv.
   - Logik:
     • Falls Filmliste existiert (count > 0) UND modified < 4 Tage alt:
       → Zeige Warn-Dialog: „Die Filmliste wurde vor weniger als 4 Tagen aktualisiert. Trotzdem neuen Collect-Lauf starten?“ (Bestätigen/Abbrechen).
     • Sonst: sofort POST /collect starten.
   - Ein POST /collect während eines laufenden Laufs soll laut Server einen Neustart auslösen; zeige Hinweis „Lauf wird neu gestartet“.
   - Während running=true: zeige visuelles Feedback (Spinner/Badge) und deaktiviere keine anderen Kernaktionen außer sinnvoller Doppel‑Klick‑Prävention.

3) Filme laden und paginieren
   - Button „Filme laden“ ist nur aktiv, wenn laut /info eine Liste existiert (count > 0); sonst ausgegraut.
   - Klick lädt per GET /movies alle Filme in den Client‑State.
   - Anzeige in Kartenform, jeweils 30 Filme pro Seite (Paginierung mit Vor/Zurück und Seitennummern).
   - Jede Karte zeigt:
     • Überschrift: title
     • Darunter: tv_name, start, stop (Format: DD.MM.YY HH:MM in lokaler Zeitzone)
     • Darunter (falls vorhanden): event
     • Darunter: description (Zeilenumbrüche respektieren; lange Texte einklappbar mit „mehr/ weniger“)
   - Biete eine einfache Suche/Filter (clientseitig) über Titel und tv_name, die mit der Paginierung zusammenspielt.

4) „Zum Löschen markieren“ und Speichern
   - Auf jeder Karte Checkbox/Toggle „Zum Löschen markieren“.
   - Markierungen werden im Client‑State gehalten (z. B. Set der eventid).
   - Button „Liste speichern“ (POST /movies) ist nur aktiv, wenn mindestens ein Film zum Löschen markiert ist.
   - Beim Speichern:
     • Sende an den Server NUR die nicht‑gelöschten Filme als vollständige Liste: { movies: <gefiltertes Array> }.
     • Nach Erfolg: aktualisiere den lokalen State, hebe Markierungen auf, aktualisiere /info (count, modified).
     • Zeige Erfolg/Fehler‑Meldungen.

5) Timer erstellen (/createtimer)
   - Button „Timer erstellen“ ist immer aktiv.
   - Wenn aktuell eine Filmliste im Client geladen ist UND es existieren Markierungen zum Löschen (Client‑Stand ≠ Server‑Stand):
     • Vor dem GET /createtimer Warn-Dialog: „Achtung: /createtimer verwendet die Serverliste. Ihre lokale Bearbeitung ist noch nicht gespeichert. Trotzdem fortfahren?“ (Bestätigen/Abbrechen).
   - Nach Aufruf: zeige Ergebnis (z. B. Roh‑JSON oder wichtige Felder freundlich dargestellt).

6) Datum/Logik
   - „Jünger als 4 Tage“: Differenz zwischen now und modified > 4*24*60*60*1000?
     • Wenn modified fehlt: behandle als „älter als 4 Tage“.
   - Datumsformatierung: DD.MM.YY HH:MM. Implementiere robuste Formatter‑Funktion (z. B. Intl.DateTimeFormat('de-DE', …)) und Fallback.
   - Achte auf lokale Zeitzone und gültige ISO‑Parsing.

7) Fehler- und Ladezustände
   - Für jede Netzwerkaktion: Ladeindikator und Fehlermeldungen (oben in einer globalen Notification‑Leiste und ggf. inline an Buttons).
   - Defensive Behandlung unerwarteter Response‑Strukturen (try/catch, optionale Ketten, Defaults).
   - UI bleibt benutzbar; Buttons werden nur dann deaktiviert, wenn es logisch ist (z. B. „Filme laden“ ohne vorhandene Liste).

8) Komponentenstruktur (Vorschlag)
   - src/main.js (App‑Mount, Basissyles importieren)
   - src/App.svelte (Layout, globale Zustände, Polling, Notifications)
   - src/components/StatusBar.svelte (Anzeige von vorhanden?, modified, count, running, run_started)
   - src/components/Controls.svelte (Buttons: Collect starten, Filme laden, Liste speichern, Timer erstellen; Zustandsabhängige Aktivierung)
   - src/components/MovieList.svelte (Paginierung, Filter, Liste)
   - src/components/MovieCard.svelte (Einzelkarte mit Markierung)
   - src/components/ConfirmDialog.svelte (generischer Bestätigungsdialog)
   - src/lib/api.js (Fetch‑Wrapper mit Basis‑URL, Fehlerbehandlung)
   - src/lib/format.js (Datum/Time‑Formatter, Hilfsfunktionen)
   - styles/global.css (schlankes, neutrales Design; dunkler/heller Modus optional)
   Du darfst die Struktur bei Bedarf anpassen, solange der Code klar und modular bleibt.

9) UX‑Details
   - Klarer Header mit Status, zentrale Button‑Leiste, darunter Filter + Paginierung + Karten.
   - Karten rasterbasiert, responsive ab 320px bis Desktop; Textumbrüche sauber.
   - Ausgrauen/Disable klar erkennbar, Fokus‑States für Tastaturbedienung, ARIA‑Labels bei Dialogen.
   - Bestätigungsdialoge sind modale Overlays mit Tastatursteuerung (Esc schließen, Enter bestätigen).

10) Implementationshinweise
   - Nutze nur Fetch API (kein externes State‑/UI‑Framework).
   - Base‑URL: relativ, dieselbe Origin (kein CORS‑Sonderfall).
   - Schreibe Kommentare, warum bestimmte Bedingungen (z. B. 4‑Tage‑Check) so umgesetzt sind.
   - Halte die Logik für „Client‑Stand ≠ Server‑Stand“ knapp: Flag derived von „gelöschteMarkierungen.size > 0“.
   - Nach POST /movies: führe optional GET /info zur Verifikation aus.
   - Nach POST /collect: starte/halte Polling von /info, bis running=false.

11) Abgabeform
   - Zeige zuerst die Projektstruktur als Baum.
   - Danach alle Dateien vollständig (Codeblöcke), inkl. minimaler package.json (Vite + Svelte) und vite.config, sodass man „npm install && npm run dev“ starten kann.
   - Füge kurze README‑Sektion mit Startanleitung und Hinweis auf die API‑Erreichbarkeit hinzu.

Akzeptanzkriterien (müssen erfüllt sein):
- Beim Start wird /info geladen, Status korrekt angezeigt und bei running=true automatisch gepollt.
- Collect‑Warnung erscheint nur, wenn modified < 4 Tage und count > 0; sonst startet Collect sofort.
- „Filme laden“ lädt Karten, 30 pro Seite, mit korrekter Darstellung von title, tv_name, start/stop (DD.MM.YY HH:MM), optional event, description.
- Markierungen zum Löschen funktionieren; „Liste speichern“ sendet nur nicht‑gelöschte Filme via { movies: [...] }.
- „Timer erstellen“ warnt, wenn lokale Markierungen existieren; Fortfahren/Abbrechen funktioniert.
- Buttons sind korrekt aktiviert/deaktiviert, Fehlermeldungen werden angezeigt, UI bleibt responsive und zugänglich.
```
