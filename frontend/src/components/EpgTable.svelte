<script>
  import { formatDateTime } from '../lib/format.js';

  let { movies, markedForDeletion, onToggleMark } = $props();

  let sortColumn = $state(null);
  let sortDirection = $state('asc');
  let expandedRows = $state(new Set());

  // Spaltendefinitionen für die Tabelle
  const columns = [
    { key: 'checked', label: '✓' },
    { key: 'start', label: 'Start' },
    { key: 'duration', label: 'Min.' },
    { key: 'tv_name', label: 'TV-Channel' },
    { key: 'title', label: 'Title' },  
    { key: 'category', label: 'Category' },
    { key: 'event', label: 'Event' }

  ];

  // Abgeleiteter Zustand für sortierte Filme
  const sortedMovies = $derived.by(() => {
    if (!sortColumn) {
      return movies;
    }

    const sorted = [...movies].sort((a, b) => {
      let aValue = a[sortColumn];
      let bValue = b[sortColumn];

      // Spezielle Behandlung für Datum/Zeit und Dauer
      if (sortColumn === 'start') {
        aValue = new Date(a.start).getTime();
        bValue = new Date(b.start).getTime();
      } else if (sortColumn === 'duration') {
        aValue = (new Date(a.stop) - new Date(a.start)) / 60000;
        bValue = (new Date(b.stop) - new Date(b.start)) / 60000;
      }


      if (aValue < bValue) {
        return sortDirection === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortDirection === 'asc' ? 1 : -1;
      }
      return 0;
    });

    return sorted;
  });

  function handleSort(columnKey) {
    if (columnKey === 'checked') return;
    if (sortColumn === columnKey) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = columnKey;
      sortDirection = 'asc';
    }
  }

  function toggleRow(eventId, event) {
    // Verhindert das Ausklappen, wenn auf ein interaktives Element geklickt wird
    if (event.target.closest('input, a, button')) {
      return;
    }
    const newSet = new Set(expandedRows);
    if (newSet.has(eventId)) {
      newSet.delete(eventId);
    } else {
      newSet.add(eventId);
    }
    expandedRows = newSet;
  }

  function getRowData(movie, columnKey) {
    switch (columnKey) {
      case 'start':
        return formatDateTime(movie.start);
      case 'duration':
        return Math.round((new Date(movie.stop) - new Date(movie.start)) / 60000);
      case 'event':
        let eventText = movie.event || movie.description || '';
        if (eventText.length > 37) {
          return eventText.substring(0, 37) + '...';
        }
        return eventText;
      case 'checked':
          return ''; // Platzhalter für Checkbox
      case 'category':
          return movie.contentinfo && movie.contentinfo.length > 0 ? movie.contentinfo[0] : '-';
      default:
        return movie[columnKey];
    }
  }
</script>

<div class="table-container">
  <table>
    <thead>
      <tr>
        {#each columns as column}
          <th onclick={() => handleSort(column.key)} class:sortable={column.key !== 'checked'}>
            {column.label}
            {#if sortColumn === column.key}
              <span class="sort-indicator">{sortDirection === 'asc' ? '▲' : '▼'}</span>
            {/if}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each sortedMovies as movie (movie.eventid)}
        {@const isMarked = markedForDeletion.has(movie.eventid)}
        <tr class="main-row" class:marked={isMarked} onclick={(e) => toggleRow(movie.eventid, e)}>
          {#each columns as column}
            <td>
              {#if column.key === 'title'}
                <span class="expander">{expandedRows.has(movie.eventid) ? '−' : '+'}</span>
              {/if}
              {#if column.key === 'checked'}
                 <input 
                   type="checkbox" 
                   checked={isMarked} 
                   onchange={() => onToggleMark(movie.eventid)}
                   aria-label="Zum Löschen markieren"
                 />
              {:else}
                {getRowData(movie, column.key)}
              {/if}
            </td>
          {/each}
        </tr>
        {#if expandedRows.has(movie.eventid)}
          <tr class="details-row">
            <td colspan={columns.length}>
              <div class="details-content">
                <h4>{movie.title}</h4>
                <p>{movie.description}</p>
                <!-- {#if movie.actors && movie.actors.length > 0}
                  <p><strong>Actors:</strong> {movie.actors.join(', ')}</p>
                {/if} -->
                {#if movie.contentinfo }
                  <p>{movie.contentinfo.join(' | ')}</p>
                {/if}
                 <!-- <p><strong>Kategorie:</strong> {movie.contentinfo ? movie.contentinfo : '-'}</p> -->
                 <!-- <p><strong>Event-ID:</strong> {movie.eventid}</p> -->
              </div>
            </td>
          </tr>
        {/if}
      {/each}
    </tbody>
  </table>
</div>

<style>
  .table-container {
    overflow-x: auto;
    width: 100%;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    white-space: nowrap;
  }
  th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--color-card-border);
  }
  thead {
    background-color: var(--color-card-bg);
  }
  th.sortable {
    cursor: pointer;
    user-select: none;
  }
  th.sortable:hover {
    background-color: var(--color-background);
  }
  .sort-indicator {
    margin-left: 0.5rem;
    font-size: 0.8em;
  }
  .main-row {
    cursor: pointer;
  }
  .main-row.marked {
    background-color: color-mix(in srgb, var(--color-danger) 10%, var(--color-card-bg));
  }
  .main-row:hover {
    background-color: var(--color-background);
  }
  .expander {
    margin-right: 0.5rem;
    font-weight: bold;
  }
  .details-row td {
    background-color: var(--color-background);
    padding: 0;
  }
  .details-content {
    padding: 1rem;
    white-space: normal;
  }
</style>
