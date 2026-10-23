"""AC3 UFO Fix GUI and CLI. MIT License."""
import argparse
import json
import sys
import os
from pathlib import Path
from service import inspect, repair, VERSION

def gui(smoke=False):
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    root = tk.Tk()
    root.title('AC III Remastered – UFO Fix ' + VERSION)
    root.geometry('680x450')
    root.minsize(620, 430)
    if smoke: root.withdraw()
    frame = ttk.Frame(root, padding=24)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='UFO-Mission reparieren', font=('Segoe UI', 18)).pack(anchor='w')
    ttk.Label(frame, text='Inoffizielles Werkzeug für PC-Spielstände von AC III Remastered.\nErstellt eine Sicherung und eine reparierte Kopie. Das Original bleibt unverändert.', wraplength=610).pack(anchor='w', pady=(10,16))
    selected = tk.StringVar(value='Noch keine .save-Datei gewählt')
    ttk.Label(frame, textvariable=selected, wraplength=610).pack(anchor='w')
    status = tk.StringVar(value='Spiel und Ubisoft Connect vor dem Einsetzen der Kopie schließen.\nCloud-Synchronisation für den Austausch vorübergehend deaktivieren.')
    chosen = [None]
    output = [None]
    def choose():
        file = filedialog.askopenfilename(title='Hauptspielstand wählen', filetypes=[('Save-Dateien','*.save'),('Alle Dateien','*.*')])
        if not file: return
        chosen[0] = file
        selected.set(file)
        fix.configure(state='disabled')
        try:
            info = inspect(file)
            labels = {'repairable':'Bekannter UFO-Fehler erkannt. Reparatur möglich.', 'already_repaired':'UFO-Missionshistorie ist bereits vorhanden. Keine Änderung.', 'completed':'UFO-Mission bereits abgeschlossen. Keine Änderung.', 'unsupported':'Dieser Missionszustand wird nicht unterstützt. Keine Änderung.'}
            status.set(f"Spielstand-Slot {info['slot']}\n" + labels.get(info['status'], info['reason']))
            if info['status']=='repairable': fix.configure(state='normal')
        except Exception as exc:
            status.set('Datei wird nicht verändert.\n' + str(exc))
    ttk.Button(frame, text='Save-Datei wählen und prüfen …', command=choose).pack(anchor='w', pady=14)
    ttk.Label(frame, textvariable=status, wraplength=610).pack(anchor='w', pady=10)
    def run():
        dest = filedialog.askdirectory(title='Ordner für Sicherung und reparierte Kopie wählen')
        if not dest: return
        try:
            folder, _ = repair(chosen[0], dest)
            output[0] = str(folder)
            status.set('Fertig: Sicherung in „Original“, neue Datei in „Repariert“.\nNur die neue Datei anstelle der gewählten Save-Datei einsetzen.\nDanach Mission abschließen und speichern; bei Cloud-Konflikt den lokalen Stand wählen.')
            fix.configure(state='disabled')
            show.configure(state='normal')
            messagebox.showinfo('Kopie erstellt', str(folder), parent=root)
        except Exception as exc:
            messagebox.showerror('Keine Reparatur durchgeführt', str(exc), parent=root)
    fix = ttk.Button(frame, text='Sicherung und reparierte Kopie erstellen …', command=run, state='disabled')
    fix.pack(anchor='w', pady=10)
    show = ttk.Button(frame, text='Ergebnisordner öffnen', command=lambda:os.startfile(output[0]), state='disabled')
    show.pack(anchor='w')
    ttk.Label(frame, text='Unterstützt ausschließlich den erkannten Fehlerzustand. Anleitung im ZIP lesen.', wraplength=610).pack(side='bottom', anchor='w', pady=(16,0))
    if smoke:
        root.update()
        root.destroy()
    else: root.mainloop()

def main():
    parser = argparse.ArgumentParser(description='AC III Remastered UFO Fix (copy only)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', metavar='SAVE')
    group.add_argument('--repair', metavar='SAVE')
    parser.add_argument('--output', help='Parent folder for backup and repaired copy')
    parser.add_argument('--json-out', help='Write CLI result to this new file')
    parser.add_argument('--smoke-test', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.smoke_test:
        gui(True)
        return 0
    if not args.check and not args.repair:
        gui()
        return 0
    try:
        if args.check: result = inspect(args.check)
        else:
            if not args.output: parser.error('--repair requires --output')
            folder, result = repair(args.repair, args.output)
            result['output_folder'] = str(folder)
        code = 0
    except Exception as exc:
        result = {'status':'error', 'reason':str(exc)}
        code = 1
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        with Path(args.json_out).open('x', encoding='utf-8') as file: file.write(text)
    if sys.stdout: print(text)
    return code

if __name__ == '__main__':
    sys.exit(main())
