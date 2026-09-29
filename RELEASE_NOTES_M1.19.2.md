# Keys NG M1.19.2 — Inbox & Trusted Signers UX

Version: `0.1.19.dev2`

M1.19.2 makes the OpenPGP write-only Inbox workflow first-class in GUI and TUI while preserving the security distinction between GnuPG ownertrust and per-vault authorization.

## Highlights

- GUI and TUI notify the user when `.gpg` files are pending in a vault Inbox.
- GUI **Vault → Inbox…** and TUI **I** open an Inbox review/import workflow.
- Each Inbox item is classified as trusted, valid-but-untrusted, unsigned, invalid-signature, undecryptable, or malformed.
- Valid-but-untrusted signers can be authorized explicitly for the current vault.
- Trusted signers can be listed, added and removed from CLI, GUI and TUI.
- GnuPG ownertrust does not automatically authorize a signer for a Keys NG vault.
- Unsigned import remains explicit and requires a warning/confirmation in interactive frontends.
- Imported Inbox records are re-encrypted and signed with the destination vault policy; failed imports leave the source Inbox ciphertext untouched.
- GnuPG `VALIDSIG` primary-key fingerprint is used when a signing subkey produced the signature, so authorization follows the primary identity rather than a rotatable subkey.
- Privacy-safe diagnostics record Inbox states and timing without filenames, titles, UUIDs, fingerprints or decrypted values.
- Added an end-to-end two-colleague regression test matching the Linux-sender/Windows-recipient workflow.

## CLI trusted signer management

```text
keys-ng trust list VAULT
keys-ng trust add VAULT FULL_FINGERPRINT
keys-ng trust remove VAULT FULL_FINGERPRINT
```

The vault's own signing key cannot be removed from `trusted_signers` through the supported interface.
