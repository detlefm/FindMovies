from pathlib import Path
import re
import unicodedata

# synonyms are currently not used
synonymsprefix = "xx"
synonymssuffix = "xx"

similarwords = {"Mexiko": "Mexico", "Alptraum": "Albtraum", "Alpträume": "Albträume"}


def read_synonyms(filename: str) -> dict[str, str]:
    resultdict = {}
    lines = Path(filename).read_text(encoding="utf-8").split("\n")
    for line in lines:
        words = [norm_word(w) for w in line.split(",")]
        for w in words[1:]:
            resultdict[w] = words[0]
    return resultdict




def remove_diacritical(text):
    """
    remove diacritical marks (accents, umlauts, etc.) from a string.
    
    Args:
        text (str): The input string to remove diacritical marks from.
    
    Returns:
        str: The input string with diacritical marks removed.
    
    Samles:
    >>> remove_diacritical("Håka")     'Haka'
    >>> remove_diacritical("Café")     'Cafe'
    >>> remove_diacritical("Mëtàl")    'Metal'
    """
    # Normalize the text in NFD form (breaks down characters into base characters + diacritics)
    normalized_text = unicodedata.normalize('NFD', text)
    # Remove all combining characters (diacritical marks)
    cleaned_text = ''.join(
        char for char in normalized_text
        if not unicodedata.combining(char)
    )
    return cleaned_text


def remove_umlaute(s: str) -> str:
    rdict = {
        "Ö": "Oe",
        "Ä": "Ae",
        "Ü": "Ue",
        "ö": "oe",
        "ä": "ae",
        "ß": "ss",
        "ü": "ue",
        "é": "e",
        "à": "a",
    }
    if erg := s:
        for k, v in rdict.items():
            erg = erg.replace(k, v)
    return erg





def clean_text(text, replace_other_non_ascii=False):
    """
    Removes diacritics and optionally converts other non-ASCII characters to ASCII equivalents.
    
    Args:
        text: Input string (e.g., "Håla€ß©ÆØ")
        replace_other_non_ascii: If True, also converts ß, Æ, Ø, currency symbols etc.
    
    Returns:
        Cleaned string (e.g., "HalaEURss(c)AeOe" when replace_other_non_ascii=True)
    """
    # Normalize to decomposed form and remove diacritical marks
    normalized = unicodedata.normalize('NFKD', text)
    cleaned = ''.join([c for c in normalized if not unicodedata.combining(c)])
    
    if replace_other_non_ascii:
        # Define replacements for special characters
        replacements = {
            # German
            'ß': 'ss',
            
            # Scandinavian/Nordic letters
            'Æ': 'Ae', 'æ': 'ae',
            'Ø': 'Oe', 'ø': 'oe',
            'Å': 'Aa', 'å': 'aa',
            'Ð': 'D', 'ð': 'd',  # Icelandic Eth
            'Þ': 'Th', 'þ': 'th', # Icelandic Thorn
            'Ł': 'L', 'ł': 'l',    # Polish L
            
            # Currency symbols
            '€': 'EUR',
            '£': 'GBP',
            
            # Legal symbols
            '©': '(c)',
            '®': '(r)',
            '™': '(tm)',
            
            # French quotes
            '«': '<<', 
            '»': '>>'
        }
        
        # Apply replacements
        cleaned = ''.join(replacements.get(c, c) for c in cleaned)
        
        # Remove any remaining non-ASCII characters
        cleaned = cleaned.encode('ASCII', errors='ignore').decode('ASCII')
    
    return cleaned

    # Test cases
    # print(clean_text("Håla€ß©ÆØŁ"))               # Output: "Hala€ß©ÆØŁ"
    # print(clean_text("Håla€ß©ÆØŁ", True))        # Output: "HalaEURss(c)AeOeL"
    # print(clean_text("Mëtàl 10€ ©"))             # Output: "Metal 10€ (c)"
    # print(clean_text("Mëtàl 10€ ©", True))       # Output: "Metal 10EUR (c)"
    # print(clean_text("Þór's © café"))            # Output: "Thor's (c) cafe"


def norm_word(s: str) -> str:
    # strip space cr lf and remove umlaute
    tmp = remove_umlaute(s.strip())
    return str.lower(tmp)


def get_words(s: str, synonyms: dict = {}):
    if not s:
        return []
    s = s.replace("'", "")
    tmp = ""
    for c in s:
        if c.isdigit() or c.isalpha() or c == "$":
            tmp += c
        else:
            tmp += " "
    words = tmp.split()
    return words


def strip_x(s: str):
    return s.strip("' \"\n\r\t")


def split_partno(s: str) -> tuple[str, int, str]:
    patterns = [
        r"(?P<Title>.*?)\((?P<Number>\d{1,2})/?(?P<Tail>.*?)\)",
        r"(?P<Title>.*)[ _-]Teil[ _](?P<Number>\d{1,2})(?P<Tail>.*)",
    ]

    for pattern in patterns:
        match = re.match(pattern, s)
        if match:
            title = match.group("Title").strip()
            number = match.group("Number")
            tail = match.group("Tail").strip()
            no = int(number)
            return (title, no, tail)

    return (s, -1, "")


def split_line_rfind(line: str, trenner: str) -> tuple[str, str]:
    pos = line.rfind(trenner)
    if pos > -1:
        return line[:pos], line[pos + 1 :].strip()
    return line, ""


def split_line_find(line: str, trenner: str) -> tuple[str, str]:
    pos = line.find(trenner)
    if pos > -1:
        return line[:pos], line[pos + 1 :].strip()
    return line, ""


def unified_sentence(s: str, sep: str = "", tolower=False):
    erg = s
    if s:
        tmp = remove_umlaute(s)
        slst = get_words(tmp)
        erg = sep.join(slst)
        if tolower:
            return erg.lower()
    return erg


def trim_nodigits(str: str) -> str:
    tmp = str
    while not tmp[-1].isdigit():
        tmp = tmp[0:-1]
    return tmp


def clean_filename(name: str) -> str:
    rd = {" - ": "-", "  ": " ", " ": "_"}
    tmp = remove_umlaute(name)
    for k, v in rd.items():
        while k in tmp:
            tmp = tmp.replace(k, v)
    return tmp


def cutstr(s: str, l: int = 20):
    if len(s) <= l:
        return s
    return s[:l] + "..."


def str2hex(s: str):
    return s.encode("utf-8").hex(" ").upper()




def convert_roman(title:str) -> str:
    """
    Ersetzt eigenständige römische Zahlen in Filmtiteln durch Dezimalzahlen.
    Ein "I" am Anfang wird als englisches "Ich" behandelt und nicht umgewandelt.
    """
    roman_numerals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    
    def is_valid_roman(s):
        # Überprüft ob der String eine gültige römische Zahl ist
        if not all(c in roman_numerals for c in s):
            return False
        # Einfache Validierung der römischen Zahl (nicht vollständig, aber für die meisten Fälle ausreichend)
        for invalid in ('IIII', 'VV', 'XXXX', 'LL', 'CCCC', 'DD', 'MMMM'):
            if invalid in s:
                return False
        return True

    def roman_to_int(s):
        # Umwandlung römischer Zahl in Integer
        total = 0
        prev = 0
        for c in reversed(s):
            current = roman_numerals[c]
            if current < prev:
                total -= current
            else:
                total += current
            prev = current
        return total

    words = title.split()
    for i, word in enumerate(words):
        # Trenne Wort in Präfix, mögliche römische Zahl und Suffix
        # Finde den längsten gültigen römischen Zahlenteil
        max_roman_len = 0
        for j in range(1, len(word)+1):
            part = word[:j]
            if is_valid_roman(part):
                max_roman_len = j
        
        if max_roman_len == 0:
            continue
            
        roman_str = word[:max_roman_len]
        suffix = word[max_roman_len:]
        
        # Sonderfall: Einzelnes "I" am Anfang nicht umwandeln
        if i == 0 and roman_str == 'I' and not suffix:
            continue
            
        # Nur umwandeln wenn:
        # 1. Das ganze Wort eine römische Zahl ist ODER
        # 2. Die römische Zahl gefolgt von Satzzeichen ist (:,.) ODER
        # 3. Die römische Zahl gefolgt von th, st, nd, rd (für Ordinalzahlen)
        valid_suffixes = ('', ':', ',', '.', 'th', 'st', 'nd', 'rd')
        if suffix.lower() not in valid_suffixes:
            continue
            
        # Umwandeln
        decimal_value = roman_to_int(roman_str)
        
        # Suffix für Ordinalzahlen behalten (z.B. "IInd" -> "2nd")
        if suffix.lower() in ('th', 'st', 'nd', 'rd'):
            suffix = suffix.lower()
        
        # Ersetze das Wort durch den Dezimalwert mit Suffix
        words[i] = f"{decimal_value}{suffix}"
        break  # Nur eine römische Zahl wird ersetzt
    
    return ' '.join(words)


def short_str(s:str,length:int):
    if len(s) <= length:
        return s + ' '*(length-len(s))
    return s[:length] + '...'