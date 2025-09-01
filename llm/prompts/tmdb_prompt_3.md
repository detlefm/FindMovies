
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

# EPG-Eintrag und TMDB-Filmbeschreibungen

```json
{
    "epg_entry":{
        "eventid": "46937",
        "title": "Afrika im Herzen",
        "description": "Voller Idealismus leitet die \u00c4rztin Katrin Berger gemeinsam mit ihrem Kollegen Sam ein Buschkrankenhaus in Namibia. Der sensible Sam empfindet zwar weit mehr als nur kollegiale Freundschaft f\u00fcr Katrin, aber gerade als er ihr endlich seine Gef\u00fchle offenbaren will, taucht \u00fcberraschend der weltgewandte Stefan auf, der Zwillingsbruder von Katrins verstorbenem Ehemann. Dieser behauptet, im Rahmen eines humanit\u00e4ren Projekts in Afrika zu sein. Allein Sam scheint sofort zu sp\u00fcren, dass Stefan ein falsches Spiel treibt - oder ist es nur seine Eifersucht auf den charmanten Rivalen?\n\n[16:9] [SUB] [6+]   [PDC 12.06. 04:35]",
        "event": "Spielfilm Deutschland 2008"
    },
    "tmdb_entries": [
        {
            "adult": false,
            "id": 73904,
            "original_language": "de",
            "original_title": "Afrika im Herzen",
            "overview": "Voller Idealismus leitet die Ärztin Katrin Berger gemeinsam mit ihrem Kollegen Sam ein Buschkrankenhaus in Namibia. Der sensible Sam empfindet zwar weit mehr als nur kollegiale Freundschaft für Katrin, aber gerade als er ihr endlich seine Gefühle offenbaren will, taucht überraschend der weltgewandte Stefan auf, der Zwillingsbruder von Katrins verstorbenem Ehemann. Dieser behauptet, im Rahmen eines humanitären Projekts in Afrika zu sein. Allein Sam scheint sofort zu spüren, dass Stefan ein falsches Spiel treibt - oder ist es nur seine Eifersucht auf den charmanten Rivalen?",
            "release_date": "2008-12-22",
            "title": "Afrika im Herzen",
            "video": false,
            "genres": [
            "Familie",
            "TV-Film"
            ],
            "cast_list": [
            {
                "name": "Christine Neubauer",
                "character": ""
            },
            {
                "name": "Francis Fulton-Smith",
                "character": ""
            },
            {
                "name": "Timothy Peach",
                "character": ""
            }
            ],
            "keywords": []
        },
        {
            "adult": false,
            "id": 172339,
            "original_language": "en",
            "original_title": "Location Africa",
            "overview": "In seinem Filmessay berichtet Steff Gruber über die äusserst schwierigen Dreharbeiten zu Werner Herzogs Film Cobra Verde in Ghana. Der sehr persönliche Film geht jedoch über die übliche Drehberichterstattung hinaus: Er berichtet über die komplizierte Beziehung der beiden Stars Werner Herzog und Klaus Kinski, über Statisten (Herzog lässt tausend junge Ghanesinnen zu Amazonen-Kämpferinnen ausbilden) und über das Aufeinanderprallen von Schwarz und Weiß.",
            "release_date": "1987-02-28",
            "title": "Herzog in Afrika",
            "video": false,
            "genres": [
            "Dokumentarfilm"
            ],
            "cast_list": [
            {
                "name": "Werner Herzog",
                "character": "Self"
            },
            {
                "name": "Peter Berling",
                "character": "Self"
            },
            {
                "name": "Thomas Mauch",
                "character": "Self"
            },
            {
                "name": "King Ampaw",
                "character": "Self"
            },
            {
                "name": "Steff Gruber",
                "character": "Self"
            },
            {
                "name": "Klaus Kinski",
                "character": "Self"
            },
            {
                "name": "Beat Presser",
                "character": "Self"
            },
            {
                "name": "Berthold Sack",
                "character": "Self"
            }
            ],
            "keywords": []
        }
        
    ]
}
```
