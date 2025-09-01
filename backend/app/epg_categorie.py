

# main_categories_original = {
#     0x00: ("Nicht definiert", "Sonstiges"),
#     0x10: ("Movie/Drama", "Film"),
#     0x20: ("News/Information", "News"),
#     0x30: ("Show/Game", "Show"),
#     0x40: ("Sports", "Sport"),
#     0x50: ("Children’s/Youth", "Kinder"),
#     0x60: ("Music/Ballet/Dance", "Show"),
#     0x70: ("Arts/Culture", "Doku"),
#     0x80: ("Social/Science/Education", "Doku"),
#     0x90: ("Leisure/Hobbies", "Doku"),
#     0xA0: ("Special characteristics", "Sonstiges"),
#     0xB0: ("Adult", "Film"),
#     0xC0: ("Education/School", "Doku"),
#     0xD0: ("Drama (nicht DVB-spezifisch)", "Serie"),
#     0xE0: ("Other", "Sonstiges"),
#     0xF0: ("User defined", "Sonstiges")
# }


main_categories = {
    0x00: ("", ""),
    0x10: ("Movie/Drama", "Movie"),
    0x20: ("News/Information", "News"),
    0x30: ("Show/Game", "Show"),
    0x40: ("Sports", "Sport"),
    0x50: ("Children’s/Youth", "Children"),
    0x60: ("Music/Ballet/Dance", "Show"),
    0x70: ("Arts/Culture", "Doku"),
    0x80: ("Social/Science/Education", "Doku"),
    0x90: ("Leisure/Hobbies", "Doku"),
    0xA0: ("", ""),
    0xB0: ("Adult", "Movie"),
    0xC0: ("Education/School", "Doku"),
    0xD0: ("Drama", "Serial"),
    0xE0: ("", ""),
    0xF0: ("", "")
}


# Nur Hauptcodes bis inkl. 0xA0 definiert
sub_tables = {
    0x10: {
        0x0: "Movie Generell",       # "Allgemein"
        0x1: "Crime/Thriller",
        0x2: "Abenteuer/Western/Krieg",
        0x3: "Science Fiction/Fantasy",
        0x4: "Komödie",
        0x5: "Melodram/Soap",
        0x6: "Romanze",
        0x7: "Klassisch/Religiös",
        0x8: "Erwachsenenfilm",
        **{i: "" for i in range(0x9, 0x10)} # "Reserviert" 
    },
    0x20: {
        0x0: "Doku/Wetter/Magazin",      
        0x1: "Wetter",
        0x2: "Magazin",
        0x3: "Dokumentation",
        0x4: "Diskussion/Debatte",
        **{i: "" for i in range(0x5, 0x10)} # "Reserviert" 
    },
    0x30: {
        0x0: "Show Allgemein",       # "Allgemein"
        0x1: "Game Show/Quiz",
        0x2: "Varieté",
        0x3: "Talkshow",
        **{i: "" for i in range(0x4, 0x10)} # "Reserviert" 
    },
    0x40: {
        0x0: "Sport",       # "Allgemein"
        0x1: "Sportereignis",
        0x2: "Fußball",
        0x3: "Tennis/Squash",
        0x4: "Radsport",
        0x5: "Wassersport",
        0x6: "Wintersport",
        0x7: "Leichtathletik",
        0x8: "Motorsport",
        0x9: "Pferdesport",
        0xA: "Ballsport",
        0xB: "Kampfsport",
        0xC: "Turnen",
        0xD: "Extremsport",
        **{i: "" for i in range(0xE, 0x10)} # "Reserviert" 
    },
    0x50: {
        0x0: "Kinderprogramm",       # "Allgemein"
        0x1: "Vorschulkinder",
        0x2: "Kinder",
        0x3: "Jugendliche",
        0x4: "Bildungsprogramm",
        **{i: "" for i in range(0x5, 0x10)} # "Reserviert" 
    },
    0x60: {
        0x0: "Musik",       # "Allgemein"
        0x1: "Rock/Pop",
        0x2: "Seriöse Musik/Klassik",
        0x3: "Volksmusik",
        0x4: "Jazz",
        0x5: "Musical/Oper",
        0x6: "Ballett/Tanz",
        **{i: "" for i in range(0x7, 0x10)} # "Reserviert" 
    },
    0x70: {
        0x0: "Kunst/Kultur",       # "Allgemein"
        0x1: "Darstellende Kunst",
        0x2: "Literatur",
        0x3: "Film/Kino",
        0x4: "Experimentelles",
        0x5: "Mode",
        0x6: "Design/Architektur",
        0x7: "Geschichte",
        0x8: "Kultur/Tradition",
        **{i: "" for i in range(0x9, 0x10)} # "Reserviert" 
    },
    0x80: {
        0x0: "Wissenschaft/Natur",       # "Allgemein"
        0x1: "Natur/Umwelt",
        0x2: "Technik",
        0x3: "Medizin",
        0x4: "Soziales",
        0x5: "Psychologie",
        0x6: "Erziehung",
        0x7: "Sprachen",
        0x8: "Wissenschaft allgemein",
        **{i: "" for i in range(0x9, 0x10)} # "Reserviert" 
    },
    0x90: {
        0x0: "Haushalt/Reisen",       # "Allgemein"
        0x1: "Tourismus/Reisen",
        0x2: "Freizeit/Hobby",
        0x3: "Haushalt",
        0x4: "Garten",
        0x5: "Tiere",
        0x6: "Kochen",
        0x7: "DIY/Heimwerken",
        0x8: "Shopping",
        **{i: "" for i in range(0x9, 0x10)} # "Reserviert" 
    },
    0xA0: {
        0x0: "",       # "Allgemein"
        0x1: "Untertitel",
        0x2: "Hörfassung",
        0x3: "Mehrsprachig",
        0x4: "Live",
        0x5: "Wiederholung",
        0x6: "UT für Gehörlose",
        **{i: "" for i in range(0x7, 0x10)} # "Reserviert" 
    }
}


def main_category(code: int|str):
    try:
        if isinstance(code,str):
            code = int(code)
        main = code & 0xF0
        name, category = main_categories.get(main, ("", ""))
        return main, name, category
    except ValueError:
        return None, "", ""

def sub_category(code: int|str):
    try:
        #code = int(content_hex, 16)
        if isinstance(code,str):
            code = int(code)
        # else:
        #     code = code        
        main = code & 0xF0
        sub = code & 0x0F
        sub_map = sub_tables.get(main, {})
        sub_desc = sub_map.get(sub, "")
        return sub, sub_desc
    except ValueError:
        return 0, ""

def categorie_list(content:int|str) -> list[str]:
    main, name,categorie = main_category(code=content)
    catlst = [categorie,name]
    sub, subcategorie = sub_category(code=content)
    if sub != 0:
        catlst.append(subcategorie)
    return [item for item in catlst if item]


def is_movie(code:int|str):
    if isinstance(code,str):
        code = int(code)
    maincode = code & 0xF0
    if maincode == 0x10 or maincode == 0xB0:
        return True
    return categorie_list(content=code) == []
    #return maincode == 0x10 or maincode == 0xB0 or maincode == 0x00

