# Contributing

Bug reports and carefully scoped improvements are welcome. Include tool version, PC store/game version, displayed slot and error/status text. Explain whether the UFO investigation is missing, already started or completed.

Do not attach personal saves, account directories, credentials or proprietary game assets to public issues. Redact private paths and identifiers from reports. Start with the minimum diagnostic information; a save should not be needed for an initial report.

Changes to repair behavior need synthetic tests demonstrating both acceptance of the intended state and rejection of nearby unsupported states. Preserve copy-only behavior, full container validation, read-back verification and the refusal to grant mission completion. Do not widen support claims without independent validation.

Run `python -m unittest discover -s tests -v` before submitting a pull request. Describe the supported state and how the change was tested. Project contributions are under the MIT license in this repository.
