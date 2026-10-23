# Format and repair notes

This documents the narrow format observed in the supported PC Remastered save. It is not a complete or official format specification.

## Container

- Preserve the 552-byte outer wrapper, including its title and slot metadata.
- Supported payload begins with save version 33 and a known 16-byte format prefix.
- Recover the current repeating 16-byte XOR key locally from ciphertext and the known prefix. No account identifier is embedded or requested.
- Validate the decrypted payload's trailing little-endian CRC32C using reflected polynomial `0x82F63B78` and seed `0xF4C3B8A2`.
- Validate compressed block headers and Adler-32 checksums (initial value 0), then decode LZO blocks using lzokay. Equal stored and unpacked sizes identify a raw block.
- Repack the state into blocks of up to 32768 bytes. Update frame sizes, total size, Adler-32 values and outer CRC32C. Rotate the recovered key right by the payload length delta modulo 16.
- Parse the generated save again and compare decoded state, root metadata and slot before writing the output copy.

## Structural guard

The TLV parser follows property boundaries, object lengths, arrays and references rather than fixed file offsets. It locates the MissionHistory whose identifier has low 32 bits equal to 1, then the Frontiersmen MissionGroup `0x1463028a2`.

The supported broken state has no UFO mission history record and has UFO accomplishment `0x40bbc940f` flags:

| Field | Required value |
| --- | --- |
| Inactive | 0 |
| Completed | 1 |
| CurrentCount | 1 |

These are the accomplishment flags used to recognize the accepted-quest state; they are **not** used as evidence that the investigation itself was completed. Duplicate or ambiguous structures are rejected.

## Change

Insert a 272-byte MissionSaveData record for UFO mission `0x2953f22b0`, containing only Intro step `0x2953f22bb` with its succeeded flag set. Mission score and time remain zero. There is no Body record or overall completion credit. A 19-byte array separator brings the state size increase to 291 bytes. Update the mission array count and nine enclosing lengths discovered by the parser.

Existing history entries and accomplishment flags are retained. The generated record uses format constants only. If UFO history already exists, the service refuses to create another repaired copy; a missing marker alone is insufficient evidence to change an arbitrary save.

## Limits

Only one repaired real-world Steam save was confirmed in-game. Other account keys and data layouts were tested synthetically. Unknown format versions, other UFO failure modes and other platform containers need separate investigation and validation.
