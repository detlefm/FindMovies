/**
 * Formatiert einen ISO-8601-Datumsstring in ein lesbares deutsches Format.
 * @param {string | null | undefined} isoString - Der zu formatierende ISO-String (z.B. "2025-08-16T15:30:00").
 * @returns {string} - Das formatierte Datum (z.B. "16.08.25 15:30") oder "Ungültiges Datum", wenn die Eingabe ungültig ist.
 */
export function formatDateTime(isoString) {
  if (!isoString) {
    return 'N/A';
  }
  try {
    const date = new Date(isoString);
    // Prüfen, ob das Datum gültig ist. new Date(null) ergibt ein ungültiges Datum.
    if (isNaN(date.getTime())) {
      return 'Ungültiges Datum';
    }

    const options = {
      year: '2-digit',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false, // 24-Stunden-Format
    };
    return new Intl.DateTimeFormat('de-DE', options).format(date);
  } catch (error) {
    console.error('Fehler beim Formatieren des Datums:', isoString, error);
    return 'Formatierungsfehler';
  }
}
