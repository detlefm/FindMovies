from datetime import datetime
import json
from pathlib import Path



sys_prompt:str = (
    "Du bist ein hilfreicher KI-Assistent, der die Wahrscheinlichkeit berechnet, "
    "dass ein EPG-Eintrag mit einem Film aus der TMDB Datenbank übereinstimmt."
)



facts_template = """
 ## Berücksichtige 
 - Das Filmformat 16:9 wurde ab 1985 verwendet.
 - Dolby 5.1 kam erstmals 1987 zum Einsatz.
 - Das aktuelle Datum ist {date}
"""

def system_prompt() -> dict:
    content = sys_prompt
    content += f'\n{facts_template.format(date=datetime.now().strftime("%Y-%m-%d"))}'
    return {
        "role": "system",
        "content": content
    }



newusrprompt = """

# Aufgabenbeschreibung
Du erhältst zwei Arten von Informationen im JSON-Format:
Einen EPG-Eintrag und eine Liste von TMDB-Filmbeschreibungen.Deine Aufgabe ist es, für jede dieser TMDB-Filmbeschreibungen eine Wahrscheinlichkeit (zwischen 0 und 1) anzugeben, wie wahrscheinlich es ist, dass sich der EPG-Eintrag auf diesen Film bezieht.
# Ausgabeformat
Gib als Ergebnis eine JSON-Liste ohne weitere Anmerkungen im folgenden Format zurück:
[
  {
    "tmdb_title": "...",
    "tmdb_id": 123456,
    "eventid": 789012,
    "probability": 0.85,
    "reasoning": "..."
  },
  ...
]

# EPG-Eintrag 
<EPG_ENTRY>

# TMDB-Filmbeschreibungen

<TMDB_MOVIES>


"""

def epg_movie_user_prompt(epg: dict, movies: list[dict]) -> dict[str, str]:
    epgtxt = json.dumps(epg, ensure_ascii=False)
    moviestxt = json.dumps(movies, ensure_ascii=False)
    content = newusrprompt.replace('<EPG_ENTRY>', epgtxt).replace('<TMDB_MOVIES>', moviestxt)
    return {"role": "user", "content": content}





def json_repair_prompt(json_string, error_message):
    return f"""
Der folgende JSON-String konnte mit Python nicht geladen werden.
Bitte analysiere und korrigiere ihn so, dass er syntaktisch gültig ist und sich mit Python json.loads erfolgreich parsen lässt.
Lösche keine Daten und ändere keine Inhalte, es sei denn zur Behebung des Fehlers.
Gib ausschließlich den korrigierten JSON zurück – ohne Kommentare oder Erläuterungen.

Fehlermeldung:
{error_message}

JSON-String:
{json_string}
"""


epg_content_prompt = """
Analysiere den Titel und die Beschreibung des EPG-Eintrags, um die passendste Kategorie zu bestimmen. Prüfe auf Schlüsselwörter wie 'Dokumentarfilm', 'Interviews', 'Prozess', 'Porträt' oder andere Hinweise auf Inhaltstypen. Entscheide basierend auf dem Kontext, ob es sich um einen Film (Movie), Serien (Serial), Sport, Show, Nachrichten (News), Dokumentation (Docu) handelt. Ist aus den Informationen keine der benannten Kategorien erkennbar antworte mit "Other". 
Mögliche Kategorien: Movie, Serial, Sport, Show, News, Docu, Other
Gib nur die Kategorie als JSON-String zurück, in der Form {"category": "Movie"} - keine weiteren Kommentare.
# EPG Eintrag
<EPGENTRY>
"""