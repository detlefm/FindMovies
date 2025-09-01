<script>
  import { formatDateTime } from '../lib/format.js';

  let { movie, isMarked, onToggleMark } = $props();

  let expanded = $state(false);

  // Die Beschreibung kann Zeilenumbrüche enthalten, die wir als <br> rendern wollen.
  // Wir ersetzen sie sicher, um XSS zu vermeiden (obwohl hier unwahrscheinlich).
  const formattedDescription = $derived(
    movie.description
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
      .replace(/\n/g, '<br />')
  );

  const isLongDescription = $derived(movie.description.length > 200);
</script>

<div class="card" class:marked={isMarked}>
  <div class="card-header">
    <h3 class="title">{movie.title}</h3>
    <label class="delete-toggle">
      <input
        type="checkbox"
        bind:checked={isMarked}
        onchange={() => onToggleMark(movie.eventid)}
        aria-label="Zum Löschen markieren"
      />
      Löschen
    </label>
  </div>
  <div class="metadata">
    <span class="channel">{movie.tv_name}</span>
    <span class="time">
      {formatDateTime(movie.start)} - {formatDateTime(movie.stop).split(' ')[1]}
    </span>
  </div>
  {#if movie.event}
    <p class="event">{movie.event}</p>
  {/if}
  <div class="description">
    {@html expanded || !isLongDescription ? formattedDescription : formattedDescription.substring(0, 200) + '...'}
  </div>
  {#if isLongDescription}
    <button class="toggle-description" onclick={() => expanded = !expanded}>
      {expanded ? 'weniger anzeigen' : 'mehr anzeigen'}
    </button>
  {/if}
</div>

<style>
  .card {
    background-color: var(--color-card-bg);
    border: 1px solid var(--color-card-border);
    border-radius: 0.5rem;
    padding: 1rem;
    transition: box-shadow 0.2s, border-color 0.2s;
    display: flex;
    flex-direction: column;
  }

  .card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }

  .card.marked {
    border-left: 5px solid var(--color-danger);
    background-color: color-mix(in srgb, var(--color-danger) 5%, var(--color-card-bg));
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 0.5rem;
  }

  .title {
    margin: 0;
    font-size: 1.2rem;
    color: var(--color-primary);
  }

  .delete-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    white-space: nowrap;
    font-size: 0.9rem;
  }

  .metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.9rem;
    color: var(--color-secondary);
    margin-bottom: 0.75rem;
  }

  .event {
    font-style: italic;
    font-size: 0.9rem;
    margin: 0 0 0.75rem 0;
  }

  .description {
    font-size: 0.95rem;
    line-height: 1.5;
    white-space: pre-wrap; /* Respektiert Zeilenumbrüche aus den Daten */
    word-break: break-word;
  }

  .toggle-description {
    background: none;
    border: none;
    color: var(--color-primary);
    text-decoration: underline;
    padding: 0.25rem 0;
    margin-top: 0.5rem;
    cursor: pointer;
    align-self: flex-start;
  }
</style>
