# Validation of version 0.1.0

- One affected Steam PC save: repair confirmed working by its player in-game.
- Generalized structural repair produced exactly the same decoded state as the successful manually reviewed repair.
- Local validation: 18 tests passed, including private integration fixtures, container round trip, corruption rejection, eight synthetic encryption keys, source preservation and repeated-repair rejection.
- Windows executable: check mode, copy-only repair mode and hidden Tkinter widget-construction smoke test exited successfully.
- Public suite: 11 tests using synthetic TLV data; includes varying padding and group counts, duplicate references, malformed boundaries, completed/already-repaired states and unsupported quest flags.

Private integration fixtures are not published. The public suite cannot independently reproduce the in-game result without an appropriate save. No additional real account or non-Steam installation is claimed as validated.

Please report compatibility results with platform/store, game version and tool status. Do not post saves, account identifiers or unredacted paths publicly.
