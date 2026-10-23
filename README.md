# AC III Remastered UFO Fix

An unofficial, local save repair tool for the **missing UFO investigation / umbrella** bug in *Assassin's Creed III Remastered* on PC.

[Deutsche Anleitung](docs/README-DE.md) · [Windows download](https://github.com/ProfGans/ac3-remastered-ufo-fix/releases/latest) · [Report a problem](https://github.com/ProfGans/ac3-remastered-ufo-fix/issues)

## What it fixes

The UFO Frontiersmen quest has been accepted, but the Boston investigation marker and the umbrella in the tree are missing. In the supported broken state, the accepted quest exists but its Intro mission history entry is absent.

The tool reconstructs that missing Intro entry. **You still play the investigation yourself.** It does not grant completion, achievements or 100% synchronization.

**Experimental:** the repair was confirmed in-game on one affected Steam PC save. Automated tests cover structural variations, copy-only behavior, checksum validation and synthetic account keys. This does not establish compatibility with every save or PC edition. Existing UFO history and unfamiliar states are refused.

## Download and use

1. Download the Windows ZIP from [Releases](https://github.com/ProfGans/ac3-remastered-ufo-fix/releases/latest), extract it, and run `AC3-UFO-Fix.exe`. Windows x64; no Python or installation needed. The executable is unsigned. The current GUI is in German.
2. Choose your main-campaign `.save` file. The tool reads and displays the actual menu slot; do not infer it from the filename. Settings and DLC files are rejected.
3. If the supported bug is detected, create a backup and repaired copy in a folder of your choice. The selected source file is never overwritten.
4. Close the game and Ubisoft Connect. Temporarily disable cloud synchronization for the replacement and separately back up the **entire** save folder. Replace only the selected `.save` with the same-named file from the tool's `Repariert` folder.
5. Load the correct slot, complete the UFO mission, wait for autosave and check that progress survives reloading.
6. Re-enable cloud synchronization. If a conflict appears, keep the repaired local save.

The usual Steam installation stores these files below `Ubisoft Game Launcher/savegames/<account-id>/5184`. Other installations may differ. Choose the file from your own installation; do not replace unrelated slots.

The result folder contains `Original/` (exact backup), `Repariert/` (new copy) and `Bericht.json` (checksums and repair details). To roll back, close the game and launcher and restore the file from `Original/`.

## Supported scope

- PC **Remastered** save format version 33, main-campaign slots 1–3.
- The specific accepted-quest / missing-history state described above.
- No support for the original 2012 game, consoles, Switch, DLC saves, arbitrary corruption or all possible UFO bugs.
- No network connection, uploads, account login or account ID input required by the repair tool.

Keep backups until the repaired save has been tested in-game. No private saves, account identifiers, game executables or extracted game assets are distributed here.

## Run from source

Python 3.10+ with Tkinter is required. The Windows download bundles its runtime.

```sh
python -m pip install -r requirements.txt
python src/app.py
```

CLI mode creates copies too:

```sh
python src/app.py --check "2.save"
python src/app.py --repair "2.save" --output "results"
```

Use `--json-out new-report.json` to save CLI output, including with the windowed EXE. The report file must not already exist. Unsupported states produce no repaired copy. Do not run repair against files being written by the game or launcher.

## Development

```sh
python -m unittest discover -s tests -v
python -m pip install -r requirements-build.txt
python -m PyInstaller --clean --onefile --windowed --name AC3-UFO-Fix src/app.py
```

Build on Windows x64. The initial executable was built with Python 3.13.7 and PyInstaller 6.22.3. See [format and repair notes](docs/FORMAT.md), [validation](docs/VALIDATION.md), and [contributing](CONTRIBUTING.md). Public tests use synthetic data; personal integration fixtures are deliberately excluded.

## License and attribution

Project code: [MIT](LICENSE). Bundled runtime notices are in [licenses](licenses). The Windows executable uses Python, Tcl/Tk and lzokay and is packaged with PyInstaller, whose bootloader exception permits distributing the application under its own license.

This is an independent community project, unaffiliated with Ubisoft. Assassin's Creed and related marks belong to their respective owners.
