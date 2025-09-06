<script>
  import { formatDateTime } from '../lib/format.js';

  let { info } = $props();

  const formattedModified = $derived(formatDateTime(info?.modified));

  const statusText = $derived(
    info?.running
      ? `Running ${info.run_progress != null ? `${Math.round(info.run_progress * 100)}%` : '?? %'}`.trim()
      : 'Inaktiv'
  );

</script>

<div class="status-bar">
  <div class="status-item">
    <strong>Status:</strong>
    <span class="status-badge" class:running={info?.running}>{statusText}</span>
  </div>
  <div class="status-item">
    <strong>Filme auf Server:</strong> {info?.count ?? 'N/A'}
  </div>
  <div class="status-item">
    <strong>Letzte Änderung:</strong> {formattedModified}
  </div>
</div>

<style>
  .status-bar {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem;
    background-color: var(--color-card-bg);
    border: 1px solid var(--color-card-border);
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .status-badge {
    padding: 0.2rem 0.5rem;
    border-radius: 1rem;
    font-weight: bold;
    background-color: var(--color-secondary);
    color: white;
  }

  .status-badge.running {
    background-color: var(--color-info);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(23, 162, 184, 0.7);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(23, 162, 184, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(23, 162, 184, 0);
    }
  }
</style>
