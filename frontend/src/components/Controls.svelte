<script>
  let {
    info,
    isDirty = false, // Gibt an, ob lokale Änderungen vorhanden sind
    isLoading = {}, // Ladezustände für einzelne Aktionen
    onCollect,
    onLoadMovies,
    onSave,
    onCreateTimer
  } = $props();

  const isMoviesOnServer = $derived(info?.count > 0);
</script>

<div class="controls">
  <button onclick={onCollect} disabled={info?.running || isLoading.collect}>
    {isLoading.collect ? 'Starte...' : 'Collect starten'}
  </button>

  <button onclick={onLoadMovies} disabled={!isMoviesOnServer || isLoading.movies}>
    {isLoading.movies ? 'Lade...' : 'Filme laden'}
  </button>

  <button onclick={onSave} disabled={!isDirty || isLoading.save}>
    {isLoading.save ? 'Speichere...' : 'Liste speichern'}
  </button>

  <button onclick={onCreateTimer} disabled={!isMoviesOnServer || isLoading.timer}>
    {isLoading.timer ? 'Erstelle...' : 'Timer erstellen'}
  </button>
</div>

<style>
  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: center;
    margin-bottom: 0.5rem;
  }
</style>
