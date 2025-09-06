<script>
  import StatusBar from './components/StatusBar.svelte';
  import Controls from './components/Controls.svelte';
  import MovieList from './components/MovieList.svelte';
  import EpgTable from './components/EpgTable.svelte';
  import ConfirmDialog from './components/ConfirmDialog.svelte';
  import { api } from './lib/api.js';

  // === Zustand (State) ===
  let info = $state(null); // Status vom /info Endpunkt
  let movies = $state([]); // Geladene Filmliste
  let markedForDeletion = $state(new Set()); // Set mit eventids der zu löschenden Filme
  let notification = $state({ type: '', message: '', visible: false }); // Für globale Benachrichtigungen
  let isLoading = $state({ info: true, collect: false, movies: false, save: false, timer: false });
  let dialog = $state({ open: false, title: '', message: '', onConfirm: () => {} });
  let currentView = $state('cards'); // 'cards' or 'table'

  let pollingInterval = null;

  // === Abgeleiteter Zustand (Derived State) ===
  const isDirty = $derived(markedForDeletion.size > 0);

  // === Effekte (Effects) ===

  // Initiales Laden der Info-Daten und Start des Pollings bei Bedarf
  $effect(() => {
    fetchInfo();
    return () => {
      // Aufräumfunktion: Interval löschen, wenn die Komponente zerstört wird
      if (pollingInterval) clearInterval(pollingInterval);
    };
  });

  // Polling-Logik basierend auf dem 'running'-Status
  $effect(() => {
    if (info?.running) {
      startPolling();
    } else {
      stopPolling();
    }
  });

  // Effekt zum automatischen Ausblenden von Benachrichtigungen
  $effect(() => {
    if (notification.visible) {
      const timer = setTimeout(() => {
        notification.visible = false;
      }, 5000);
      return () => clearTimeout(timer);
    }
  });


  // === API-Funktionen ===

  async function fetchInfo(isPolling = false) {
    if (!isPolling) isLoading.info = true;
    try {
      // Defensives Mapping der erwarteten Felder
      const rawInfo = await api('/api/info');
      info = {
        modified: rawInfo.modified || null,
        count: rawInfo.count ?? 0,
        running: rawInfo.running ?? false,
        run_started: rawInfo.run_started || null,
        run_progress: rawInfo.run_progress ?? null, // Fortschritt hinzugefügt
      };
    } catch (error) {
      showNotification('error', `Fehler beim Abrufen des Status: ${error.message}`);
      info = { count: 0, running: false, modified: null, run_started: null, run_progress: null };
    } finally {
      if (!isPolling) isLoading.info = false;
    }
  }

  function startPolling() {
    if (pollingInterval) return; // Verhindert mehrere Intervalle
    // Polling alle 7 Sekunden
    pollingInterval = setInterval(() => fetchInfo(true), 7000);
  }

  function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  }

  async function handleCollect() {
    // Prüft, ob die Filmliste existiert und jünger als 4 Tage ist.
    const isRecent = info?.count > 0 && info?.modified &&
      (new Date() - new Date(info.modified)) < (4 * 24 * 60 * 60 * 1000);

    if (isRecent) {
      showDialog(
        'Collect starten?',
        'Die Filmliste wurde vor weniger als 4 Tagen aktualisiert. Trotzdem neuen Collect-Lauf starten?',
        startCollect
      );
    } else {
      startCollect();
    }
  }

  async function startCollect() {
    if (info?.running) {
        showNotification('info', 'Ein Lauf ist bereits aktiv. Er wird neu gestartet.');
    }
    isLoading.collect = true;

    // Starte den Collect-Aufruf, aber blockiere nicht darauf.
    api('/api/collect', { method: 'POST' })
      .then(async () => {
        // Dieser Block wird ausgeführt, wenn der Collect-Lauf BEENDET ist.
        showNotification('success', 'Collect-Lauf erfolgreich beendet.');
        // Status aktualisieren, um das Ende des Laufs widerzuspiegeln.
        await fetchInfo();
      })
      .catch(error => {
        showNotification('error', `Fehler beim Starten oder Ausführen des Collect-Laufs: ${error.message}`);
      })
      .finally(() => {
        isLoading.collect = false;
      });

    // Unmittelbar nach dem Starten des Aufrufs (ohne zu warten), 
    // den Status abrufen. Das Backend sollte jetzt `running: true` melden.
    // Dies löst den Polling-Effekt aus.
    setTimeout(() => fetchInfo(), 500); // Kurze Verzögerung, um dem Server Zeit zum Starten zu geben
  }

  async function handleLoadMovies() {
    isLoading.movies = true;
    try {
      const loadedMovies = await api('/api/movies');
      movies = loadedMovies || [];
      // Markierungen zurücksetzen, da eine neue Liste geladen wurde
      markedForDeletion = new Set();
      showNotification('success', `${movies.length} Filme erfolgreich geladen.`);
    } catch (error) {
      showNotification('error', `Fehler beim Laden der Filme: ${error.message}`);
    } finally {
      isLoading.movies = false;
    }
  }

  async function handleSave() {
    isLoading.save = true;
    // Erstelle eine neue Liste, die nur die nicht zum Löschen markierten Filme enthält.
    const moviesToSave = movies.filter(m => !markedForDeletion.has(m.eventid));
    try {
      await api('/api/movies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ movies: moviesToSave }),
      });
      // Lokalen Zustand aktualisieren
      movies = moviesToSave;
      markedForDeletion = new Set();
      showNotification('success', 'Filmliste erfolgreich gespeichert.');
      // Info-Status zur Verifikation neu laden
      await fetchInfo();
    } catch (error)
    {
      showNotification('error', `Fehler beim Speichern der Liste: ${error.message}`);
    } finally {
      isLoading.save = false;
    }
  }

  async function handleCreateTimer() {
    if (isDirty) {
      showDialog(
        'Timer erstellen?',
        'Achtung: Sie haben ungespeicherte Änderungen. /createtimer verwendet die auf dem Server gespeicherte Liste. Trotzdem fortfahren?',
        createTimer
      );
    } else {
      createTimer();
    }
  }

  async function createTimer() {
    isLoading.timer = true;
    try {
      const result = await api('/api/createtimer');
      // Zeige das Ergebnis in einem Dialog an
      showDialog(
        'Timer-Erstellung Ergebnis',
        `Antwort vom Server: ${JSON.stringify(result, null, 2)}`,
        () => closeDialog() // Bestätigen schließt nur den Dialog
      );
    } catch (error) {
      showNotification('error', `Fehler bei der Timer-Erstellung: ${error.message}`);
    } finally {
      isLoading.timer = false;
    }
  }


  // === UI-Hilfsfunktionen ===

  function handleToggleMark(eventid) {
    const newSet = new Set(markedForDeletion);
    if (newSet.has(eventid)) {
      newSet.delete(eventid);
    } else {
      newSet.add(eventid);
    }
    markedForDeletion = newSet;
  }

  function showNotification(type, message) {
    notification = { type, message, visible: true };
  }

  function showDialog(title, message, onConfirm) {
    dialog = { open: true, title, message, onConfirm };
  }

  function closeDialog() {
    dialog = { ...dialog, open: false };
  }

  function confirmDialog() {
    if (dialog.onConfirm) {
      dialog.onConfirm();
    }
    closeDialog();
  }

</script>

<main>
  <h1>Film-EPG-Suche</h1>

  {#if notification.visible}
    <div class="notification {notification.type}" role="alert">
      {notification.message}
      <button onclick={() => notification.visible = false} aria-label="Benachrichtigung schließen">&times;</button>
    </div>
  {/if}

  <div class="container">
    {#if isLoading.info}
      <p>Lade Status...</p>
    {:else}
      <StatusBar {info} />
      <Controls {info} {isDirty} {isLoading}
        onCollect={handleCollect}
        onLoadMovies={handleLoadMovies}
        onSave={handleSave}
        onCreateTimer={handleCreateTimer}
      />
    {/if}
  </div>

  {#if movies.length > 0}
    <div class="container">
      <div class="view-toggle">
        <button onclick={() => currentView = 'cards'} disabled={currentView === 'cards'}>Card View</button>
        <button onclick={() => currentView = 'table'} disabled={currentView === 'table'}>Table View</button>
      </div>

      {#if currentView === 'cards'}
        <MovieList {movies} {markedForDeletion} onToggleMark={handleToggleMark} />
      {:else}
        <EpgTable {movies} {markedForDeletion} onToggleMark={handleToggleMark} />
      {/if}
    </div>
  {/if}

  <ConfirmDialog
    open={dialog.open}
    title={dialog.title}
    message={dialog.message}
    onConfirm={confirmDialog}
    onCancel={closeDialog}
  />
</main>

<style>
  .notification {
    padding: 0.33rem;
    margin-bottom: 0.33rem;
    border-radius: 0.25rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .notification.success {
    background-color: var(--color-success);
    color: white;
  }
  .notification.error {
    background-color: var(--color-danger);
    color: white;
  }
  .notification.info {
    background-color: var(--color-info);
    color: white;
  }
  .notification button {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    line-height: 1;
    padding: 0 0.5rem;
  }
  .view-toggle {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 0.33rem;
  }
</style>