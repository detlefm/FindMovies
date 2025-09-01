<script>
  import { tick } from 'svelte';

  let { open, title, message, onConfirm, onCancel } = $props();

  let dialogElement = $state();

  // Effekt, um den Fokus zu verwalten, wenn der Dialog geöffnet wird
  $effect(() => {
    if (open && dialogElement) {
      // Warten, bis das Element im DOM ist, und dann den Fokus setzen
      tick().then(() => {
        const focusable = dialogElement.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusable) {
          focusable.focus();
        }
      });
    }
  });

  function handleKeydown(event) {
    if (event.key === 'Escape') {
      onCancel();
    }
  }

  function handleOverlayKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      onCancel();
    }
  }
</script>

{#if open}
  <div
    class="dialog-overlay"
    onclick={onCancel}
    onkeydown={handleOverlayKeydown}
    role="button"
    tabindex="0"
  >
    <div
      class="dialog-content"
      role="alertdialog"
      tabindex="-1"
      aria-modal="true"
      aria-labelledby="dialog-title"
      aria-describedby="dialog-message"
      bind:this={dialogElement}
      onclick={(e) => e.stopPropagation()}
      onkeydown={handleKeydown}
    >
      <h2 id="dialog-title" class="dialog-title">{title}</h2>
      <p id="dialog-message" class="dialog-message">{message}</p>
      <div class="dialog-actions">
        <button class="secondary" onclick={onCancel}>Abbrechen</button>
        <button class="primary" onclick={onConfirm}>Bestätigen</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .dialog-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .dialog-content {
    background-color: var(--color-card-bg);
    padding: 2rem;
    border-radius: 0.5rem;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  }

  .dialog-title {
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
  }

  .dialog-message {
    margin: 0 0 1.5rem 0;
    line-height: 1.5;
  }

  .dialog-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
  }

  .dialog-actions button.secondary {
    background-color: var(--color-secondary);
  }
</style>
