"""ACIII Remastered PC save envelope. No account identifiers or save fixtures.

Copyright (c) 2026 AC3 UFO Fix contributors. MIT License.
"""
from dataclasses import dataclass
import hashlib
import struct
import re
import zlib
import lzokay

class SaveError(ValueError):
    pass

HEADER_SIZE = 552
MAX_FILE = 16 * 1024 * 1024
MAX_STATE = 64 * 1024 * 1024
MAGIC = bytes.fromhex('33aafb5799fa0410')
KNOWN_PREFIX = bytes.fromhex('21000000acdbfe000000000000000000')

def need(condition, message):
    if not condition:
        raise SaveError(message)

def crc_table():
    result=[]
    for i in range(256):
        for _ in range(8):
            i=(i>>1)^(0x82F63B78 if i&1 else 0)
        result.append(i)
    return result

TABLE=crc_table()
def checksum(data):
    value=0xF4C3B8A2 ^ 0xFFFFFFFF
    for byte in data:
        value=TABLE[(value^byte)&255]^(value>>8)
    return value ^ 0xFFFFFFFF

def xor(data,key):
    return bytes(v ^ key[i&15] for i,v in enumerate(data))

def rotate_right(key,count):
    count%=16
    return key[-count:]+key[:-count] if count else key

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_title(header):
    text=header[40:].decode('utf-16-le',errors='strict').split('\0',1)[0]
    match=re.fullmatch(r'AC3RM\[(-?\d+)\]-tm_[0-9_]+',text)
    need(match is not None,'Kein unterstützter AC III Remastered PC-Spielstand.')
    index=int(match.group(1))
    need(index in (0,1,2),'Diese Datei enthält Einstellungen oder DLC-Daten. Bitte einen Hauptspielstand wählen.')
    return index+1

@dataclass
class Save:
    raw: bytes
    key: bytes
    payload: bytes
    state_header_at: int
    root: bytes
    state: bytes
    slot: int
    block_count: int

    @classmethod
    def parse(cls,raw):
        need(HEADER_SIZE+100<=len(raw)<=MAX_FILE,'Die Dateigröße wird nicht unterstützt.')
        need(raw[:8]==bytes.fromhex('2402000000000000'),'Unbekannter Ubisoft-Save-Header.')
        try:
            slot=read_title(raw[:HEADER_SIZE])
        except UnicodeError as exc:
            raise SaveError('Der Dateikopf ist beschädigt.') from exc
        cipher=raw[HEADER_SIZE:]
        # Version 33 has this exact plaintext header. Integrity and type checks
        # below authenticate this inference; no Ubisoft account ID is required.
        key=bytes(a^b for a,b in zip(cipher[:16],KNOWN_PREFIX))
        payload=xor(cipher,key)
        need(checksum(payload[:-4])==int.from_bytes(payload[-4:],'little'),
             'Die Gesamtprüfsumme ist ungültig oder das Save-Format wird nicht unterstützt. Keine Änderung.')
        need(payload[24:32]==MAGIC and payload[32:40]==bytes.fromhex('0100000080000001'),
             'Unbekanntes Kompressionsformat.')
        limit=len(payload)-4
        def block(at,cs,us,stored,maximum):
            need(0<cs<=MAX_FILE and 0<us<=maximum and at+cs<=limit,'Ungültige Blockgröße.')
            comp=payload[at:at+cs]
            need(zlib.adler32(comp,0)==stored,'Eine Blockprüfsumme ist ungültig.')
            try:
                value=lzokay.decompress(comp,us) if cs!=us else comp
            except Exception as exc:
                raise SaveError('Ein komprimierter Block ist beschädigt.') from exc
            need(len(value)==us,'Falsche entpackte Blockgröße.')
            return value
        cs,us,ck=struct.unpack_from('<III',payload,40)
        root=block(52,cs,us,ck,65536)
        need(len(root)>=18 and root[14:18]==bytes.fromhex('523bbebd'),'Unbekanntes SaveGame-Objekt.')
        h=52+cs
        need(h+44<=limit,'Der Spielzustand fehlt.')
        total,version,magic,expected=struct.unpack_from('<IIII',payload,h)
        need(total==len(payload)-h-8 and version==3 and magic==0x00CAFE00,
             'Unbekannter Spielzustands-Container.')
        need(0<expected<=MAX_STATE,'Der Spielzustand überschreitet die unterstützte Größe.')
        need(payload[h+16:h+24]==MAGIC and payload[h+24:h+32]==bytes.fromhex('0100000080000001'),
             'Unbekanntes Kompressionsformat des Spielzustands.')
        cs,us,ck=struct.unpack_from('<III',payload,h+32)
        chunks=[block(h+44,cs,us,ck,32768)]
        at=h+44+cs
        expanded=len(chunks[0])
        while at<limit:
            need(at+13<=limit and payload[at]==1 and payload[at+4]==0 and payload[at+8]==0,
                 'Ungültiger Frame-Header.')
            cs=int.from_bytes(payload[at+1:at+4],'little')
            us=int.from_bytes(payload[at+5:at+8],'little')
            ck=struct.unpack_from('<I',payload,at+9)[0]
            need(expanded+us<=expected and len(chunks)<2048,'Ungültige Anzahl oder Größe der Frames.')
            chunks.append(block(at+13,cs,us,ck,32768))
            expanded+=us
            at+=13+cs
        need(at==limit and expanded==expected,'Die Gesamtgröße des Spielzustands stimmt nicht.')
        state=b''.join(chunks)
        need(len(state)>=30 and state[14:18]==bytes.fromhex('f1f8d694'),
             'Kein unterstütztes AssassinSaveGameData-Objekt.')
        return cls(raw,key,payload,h,root,state,slot,len(chunks)+1)

    def encode(self,state):
        need(0<len(state)<=MAX_STATE,'Ungültige Größe des neuen Spielzustands.')
        parts=[state[i:i+32768] for i in range(0,len(state),32768)]
        compressed=[lzokay.compress(p) for p in parts]
        # Equal-size blocks are defined as raw in this format.
        compressed=[c if len(c)!=len(p) else p for c,p in zip(compressed,parts)]
        header=bytearray(self.payload[self.state_header_at:self.state_header_at+44])
        struct.pack_into('<I',header,12,len(state))
        struct.pack_into('<III',header,32,len(compressed[0]),len(parts[0]),zlib.adler32(compressed[0],0))
        buf=bytearray(header+compressed[0])
        for comp,plain in zip(compressed[1:],parts[1:]):
            buf.extend(b'\1'+len(comp).to_bytes(3,'little')+b'\0'+len(plain).to_bytes(3,'little')+b'\0')
            buf.extend(struct.pack('<I',zlib.adler32(comp,0)))
            buf.extend(comp)
        struct.pack_into('<I',buf,0,len(buf)+4-8)
        payload=self.payload[:self.state_header_at]+buf
        payload+=struct.pack('<I',checksum(payload))
        new_key=rotate_right(self.key,len(payload)-len(self.payload))
        raw=self.raw[:HEADER_SIZE]+xor(payload,new_key)
        verified=Save.parse(raw)
        need(verified.root==self.root and verified.state==state and verified.slot==self.slot,
             'Die Prüfung der neu erzeugten Datei ist fehlgeschlagen.')
        return raw
