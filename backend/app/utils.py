import sys
from datetime import datetime, timedelta
import json
from functools import wraps
import time
import tiktoken
from collections import defaultdict
from pathlib import Path
from typing import Any

def print2file(dateiname):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            original_stdout = sys.stdout
            with open(dateiname, "w", encoding="utf-8") as f:
                sys.stdout = f
                try:
                    return func(*args, **kwargs)
                finally:
                    sys.stdout = original_stdout
        return wrapper
    return decorator

# def fmt_dict(d:dict):
#     return json.dumps(d, indent=2,default=str, ensure_ascii=False)


# def progress_std(*arg):
#     text = ' '.join(arg)
#     print('\r\x1b[K' + text, end='',flush=True)
    

def dt2str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def try_parsedatetime(s, default=datetime.min) -> datetime:

    pattern_gr = "%d.%m.%Y %H:%M:%S"
    pattern_eu = "%d-%m-%Y %H:%M:%S"
    pattern_epg = "%Y%m%d%H%M%S"

    for pattern in [pattern_gr, pattern_eu, pattern_epg]:
        try:
            return datetime.strptime(s, pattern)
        except:  
            ...
    try:
        return datetime.fromisoformat(s)
    except:  
        return default
    



def grpby(collection: list[Any], key: str) -> dict[Any, list[Any]]:
    """Gruppiert Elemente nach einem Attribut, Dictionary-Schlüssel oder verschachtelten Pfaden.
    
    Args:
        collection: Liste von Objekten oder Dictionaries
        key: String mit Punkt-separiertem Pfad (z.B. 'attr1.attr2' oder 'dict_key.sub_key')
    
    Returns:
        defaultdict(list): Gruppierte Elemente mit key-Werten als Schlüssel
        
    Raises:
        KeyError: Wenn ein Teil des Pfads in einem Element fehlt
    """
    grouped = defaultdict(list)
    if not collection:
        return grouped

    parts = key.split('.')
    
    for item in collection:
        current = item
        for i, part in enumerate(parts):
            if current is None:
                full_path = '.'.join(parts[:i+1])
                raise KeyError(f"Wert ist None bei Pfad: '{full_path}'")
                
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    raise KeyError(f"Schlüssel '{part}' fehlt in Dictionary (Pfad: '{'.'.join(parts[:i+1])}')")
            else:
                if hasattr(current, part):
                    current = getattr(current, part)
                else:
                    raise KeyError(f"Attribut '{part}' fehlt in Objekt (Pfad: '{'.'.join(parts[:i+1])}')")
                    
        grouped[current].append(item)
        
    return grouped


def timedelta2str(timespan:timedelta):

    days = timespan.days
    seconds = timespan.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if days:
        return f"{days} Tage, {hours:02d}:{minutes:02d}:{seconds:02d}"
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


elapsed = lambda started: timedelta2str(datetime.now() - started)

def f_write(filepath:str|Path,data:str) ->int:
    if isinstance(filepath,str):
        filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    return filepath.write_text(data,encoding='utf-8')

def read_jsonl(filepath:str|Path):
    if isinstance(filepath,str):
        filepath = Path(filepath)

    lines = filepath.read_text(encoding='utf-8').splitlines()  
    return [json.loads(line) for line in lines]

def read_json(filepath:str|Path):
    if isinstance(filepath,str):
        filepath = Path(filepath)
    return json.loads(filepath.read_text(encoding='utf-8'))





def write_jsonl(filepath:str|Path,data:list):
    if isinstance(filepath,str):
        filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry,ensure_ascii=False) + "\n")



def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} dauerte {end - start:.4f} Sekunden")
        return result
    return wrapper


def async_time_it(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} dauerte {end - start:.4f} Sekunden (async)")
        return result
    return wrapper





# Modell-Name angeben (z. B. für GPT-4.1-Nano)
MODEL_NAME = "gpt-5"
# nano_tokenizer = tiktoken.encoding_for_model("gpt-4-1-nano")

def count_message_tokens(messages, model_name=MODEL_NAME):
    tokenizer = tiktoken.encoding_for_model(model_name=model_name)
    total_tokens = 0
    for message in messages:
        # Rolle (role), Name (optional) und Content zählen
        total_tokens += len(tokenizer.encode(message.get("role", "")))
        total_tokens += len(tokenizer.encode(message.get("content", "")))
        if "name" in message:
            total_tokens += len(tokenizer.encode(message["name"]))
        # Extra Tokens pro Message (bei ChatGPT-Modellen, meist 4 pro message)
        total_tokens += 4
    total_tokens += 2  # jedes Chat-Completion Prompt endet mit "assistant"
    return total_tokens
