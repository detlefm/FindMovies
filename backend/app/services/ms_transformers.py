
import xml.etree.ElementTree as ET

from typing import Any



def xml_to_channellst(text:str) ->list[dict]:
    channels = []
    root = ET.fromstring(text=text)   
    # Variante 1: channels > root > group > channel
    # Variante 2: channels > root > group > channel
    for group in root.findall('.//group'):
        for channel in group.findall('channel'):
            channels.append(channel.attrib)
    
    return channels




def xml_to_timerlst(xml_data) -> list[dict]:
    # XML parsen
    root = ET.fromstring(xml_data)

    # Alle Timer-Elemente finden
    timers = root.findall('Timer')

    # Timer-Liste erstellen
    timer_list = []
    for timer in timers:
        # Timer als Dictionary mit Attributen und Unterelementen speichern
        d:dict[str,Any] = timer.attrib       
        for child in timer:
            # Wenn das Element selbst Attribute hat (wie Options)
            key = child.tag
            if key in d.keys():
                key = f'timer_{key}'

            if child.attrib:
                subdict = {}
                if child.text:
                    subdict['#text'] = child.text
                subdict.update(child.attrib)
                d[key] = subdict
            else:
                d[key] = child.text
        
        timer_list.append(d)

    return timer_list




def xml_to_epglst(xml_content):
    root = ET.fromstring(xml_content)
    epglst = []
    
    for epgentry in root.findall('programme'):
        d = {}
        d.update(epgentry.attrib)  # Attribute (start, stop, channel)
        
        for child in epgentry:
            if len(child) > 0:  # Hat Unterelemente?
                tmp = {}
                for subchild in child:
                    tmp[subchild.tag] = subchild.text
                d[child.tag] = tmp
            else:
                d[child.tag] = child.text
        
        epglst.append(d)
    
    return epglst

