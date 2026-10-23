# Deutsche Anleitung

Dieses inoffizielle Werkzeug repariert einen bestimmten UFO-Fehler in **Assassin's Creed III Remastered am PC**: Der Frontiersmen-Auftrag wurde angenommen, aber Suchgebiet und Regenschirm fehlen. Dabei fehlt der Intro-Eintrag in der Missionshistorie.

**Experimentelle Community-Version:** Die Änderung wurde an einem betroffenen Steam-Spielstand erfolgreich im Spiel bestätigt. Das ist keine Garantie für jeden anderen Save. Das Werkzeug bearbeitet ausschließlich den erkannten Zustand und lehnt andere Zustände ab. Die Untersuchung muss anschließend selbst gespielt werden; es vergibt keine Abschlusswertung.

## Schritt für Schritt

1. Das Windows-ZIP bei [Releases](https://github.com/ProfGans/ac3-remastered-ufo-fix/releases/latest) herunterladen und vollständig entpacken.
2. `AC3-UFO-Fix.exe` starten und die Hauptspielstand-Datei auswählen. Die EXE ist nicht signiert. Python oder eine Installation sind nicht erforderlich.
3. Den angezeigten Slot prüfen. Dateinummer und Menü-Slot müssen nicht übereinstimmen. Einstellungen und DLC-Dateien werden abgelehnt.
4. Falls „Bekannter UFO-Fehler erkannt“ angezeigt wird, **Sicherung und reparierte Kopie erstellen** und einen Zielordner wählen. Das Original wird nicht überschrieben.
5. Spiel und Ubisoft Connect schließen. Cloud-Synchronisation für den Austausch vorübergehend deaktivieren. Den gesamten Save-Ordner zusätzlich sichern.
6. Nur die ausgewählte `.save` durch die gleichnamige Datei aus `Repariert` ersetzen. Keine anderen Slots löschen oder austauschen.
7. Den passenden Slot laden, UFO-Mission abschließen, automatische Speicherung abwarten und nach erneutem Laden prüfen.
8. Cloud-Synchronisation wieder aktivieren. Bei Konflikten den reparierten lokalen Stand auswählen.

Üblicher Steam-Speicherort: `Ubisoft Game Launcher/savegames/<Account-ID>/5184`. Andere Installationen können einen anderen Ordner verwenden.

Im Ergebnisordner liegen `Original` (unveränderte Sicherung), `Repariert` (neue Kopie) und `Bericht.json` (Prüfsummen und Details).

## Bei Problemen

Spiel und Launcher schließen und die gesicherte Datei aus `Original` zurückkopieren. Sicherungen behalten, bis der Erfolg im Spiel und nach erneutem Laden geprüft wurde.

Unterstützt: PC-Remastered, Save-Version 33, Hauptspielslots 1–3 und ausschließlich dieser bekannte Fehlerzustand. Nicht unterstützt: Original von 2012, Konsolen, Switch, DLC oder beliebige defekte Spielstände.

Das Werkzeug arbeitet lokal ohne Netzwerk, Upload oder Anmeldung. Das Repository enthält keine privaten Spielstände oder Account-IDs. Bitte auch in Issues keine vollständigen Saves, privaten Pfade oder Account-Daten veröffentlichen. Plattform, Spielversion und Fehlermeldung reichen zunächst aus.

Quellcode-Nutzung, technische Details und Lizenz: siehe [README](../README.md).
