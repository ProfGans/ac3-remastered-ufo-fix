"""Copy-only repair service. MIT License."""
from pathlib import Path
from datetime import datetime
import json
from savefile import Save, SaveError, MAX_FILE, digest
from structure import analyze, apply_repair

VERSION = '0.1.0'

def load(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_FILE:
        raise SaveError('Keine gültige Save-Datei oder Datei zu groß.')
    raw = path.read_bytes()
    return raw, Save.parse(raw)

def inspect(path):
    raw, save = load(path)
    return dict(tool_version=VERSION, file=Path(path).name, slot=save.slot,
                sha256=digest(raw), **analyze(save.state))

def repair(path, destination):
    path = Path(path)
    raw, save = load(path)
    if analyze(save.state)['status'] != 'repairable':
        raise SaveError('Kein unterstützter reparierbarer UFO-Zustand. Keine Kopie erstellt.')
    state, details = apply_repair(save.state)
    result = save.encode(state)
    if analyze(Save.parse(result).state)['status'] != 'already_repaired':
        raise SaveError('Nachprüfung der Reparatur fehlgeschlagen.')
    if path.read_bytes() != raw:
        raise SaveError('Quelldatei wurde inzwischen verändert. Spiel und Launcher schließen.')
    parent = Path(destination)
    parent.mkdir(parents=True, exist_ok=True)
    folder = parent / ('AC3-UFO-Fix-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    folder.mkdir()
    (folder/'Original').mkdir()
    (folder/'Repariert').mkdir()
    with (folder/'Original'/path.name).open('xb') as f:
        f.write(raw)
    with (folder/'Repariert'/path.name).open('xb') as f:
        f.write(result)
    report = dict(tool_version=VERSION, file=path.name, slot=save.slot,
                  original_sha256=digest(raw), repaired_sha256=digest(result),
                  original_untouched=True, **details)
    (folder/'Bericht.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return folder, report
