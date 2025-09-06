<script>
  import MovieCard from './MovieCard.svelte';

  let { movies, markedForDeletion, onToggleMark } = $props();

  let searchTerm = $state('');
  let currentPage = $state(1);
  const itemsPerPage = 30;

  // Abgeleiteter Zustand für die gefilterte und durchsuchte Filmliste
  const filteredMovies = $derived.by(() => {
    if (!searchTerm) {
      return movies;
    }
    const lowerCaseSearch = searchTerm.toLowerCase();
    return movies.filter(movie =>
      movie.title.toLowerCase().includes(lowerCaseSearch) ||
      movie.tv_name.toLowerCase().includes(lowerCaseSearch)
    );
  });

  // Abgeleiteter Zustand für die Paginierung
  const totalPages = $derived(Math.ceil(filteredMovies.length / itemsPerPage));

  // Effekt, um die Seitenzahl zurückzusetzen, wenn die Filterung die Anzahl der Seiten ändert
  $effect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      currentPage = totalPages;
    } else if (totalPages === 0) {
      currentPage = 1;
    }
  });

  const paginatedMovies = $derived.by(() => {
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return filteredMovies.slice(start, end);
  });

  function goToPage(page) {
    if (page >= 1 && page <= totalPages) {
      currentPage = page;
    }
  }
</script>

<div class="movie-list-container">
  {#if movies.length > 0}
    <div class="filter-controls">
      <input
        type="search"
        bind:value={searchTerm}
        placeholder="Filme nach Titel oder Sender filtern..."
        aria-label="Filme filtern"
      />
      <div class="pagination-summary">
        Zeige {paginatedMovies.length} von {filteredMovies.length} Filmen
      </div>
    </div>

    <div class="movie-grid">
      {#each paginatedMovies as movie (movie.eventid)}
        <MovieCard
          {movie}
          isMarked={markedForDeletion.has(movie.eventid)}
          {onToggleMark}
        />
      {/each}
    </div>

    {#if totalPages > 1}
      <nav class="pagination" aria-label="Seitennavigation">
        <button onclick={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>
          &laquo; Zurück
        </button>
        <span>Seite {currentPage} von {totalPages}</span>
        <button onclick={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages}>
          Weiter &raquo;
        </button>
      </nav>
    {/if}
  {:else}
    <p>Keine Filme geladen. Klicken Sie auf "Filme laden", um die Liste abzurufen.</p>
  {/if}
</div>

<style>
  .movie-list-container {
    width: 100%;
  }

  .filter-controls {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
  }

  .filter-controls input {
    flex-grow: 1;
    min-width: 250px;
  }

  .pagination-summary {
    font-size: 0.9rem;
    color: var(--color-secondary);
  }

  .movie-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 1.5rem;
  }
</style>
