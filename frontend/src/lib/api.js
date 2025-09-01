// Liest die Basis-URL aus den Vite-Umgebungsvariablen.
// In einer .env-Datei kann VITE_API_BASE_URL=http://localhost:8000 gesetzt werden.
// Wenn die Variable nicht gesetzt ist, wird ein leerer String verwendet (für relative Pfade).
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Wrapper für die Fetch-API.
 * Stellt sicher, dass Anfragen als JSON behandelt werden und fängt Netzwerkfehler ab.
 * @param {string} endpoint - Der API-Endpunkt (z.B. '/info').
 * @param {RequestInit} [options={}] - Die Optionen für die Fetch-Anfrage (z.B. method, headers, body).
 * @returns {Promise<any>} - Ein Promise, das mit den JSON-Daten der Antwort aufgelöst wird.
 * @throws {Error} - Wirft einen Fehler bei Netzwerkproblemen oder wenn die Antwort keinen OK-Status hat.
 */
export async function api(endpoint, options = {}) {
  // Fügt die Basis-URL zum Endpunkt hinzu.
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      // Versuchen, eine Fehlermeldung aus dem Body zu lesen
      const errorBody = await response.text();
      let errorMessage = `HTTP-Fehler ${response.status}: ${response.statusText}`;
      if (errorBody) {
        try {
          const errorJson = JSON.parse(errorBody);
          errorMessage += ` - ${errorJson.detail || errorBody}`;
        } catch {
          errorMessage += ` - ${errorBody}`;
        }
      }
      throw new Error(errorMessage);
    }

    // Wenn der Content-Type JSON ist, parse die Antwort, ansonsten gib sie als Text zurück.
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    // Für den Fall, dass eine Antwort leer ist (z.B. bei Status 204)
    if (response.status === 204 || response.headers.get('content-length') === '0') {
        return null;
    }
    return await response.text();

  } catch (error) {
    console.error(`API-Fehler bei Anfrage an ${url}:`, error);
    // Wirf den Fehler weiter, damit die aufrufende Komponente ihn behandeln kann.
    throw error;
  }
}
