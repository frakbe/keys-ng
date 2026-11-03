# Checklist per la review di sicurezza esterna

## Target ed evidenze

- [ ] Registrati tag e commit SHA della release.
- [ ] Registrato SHA256 dell'archivio sorgente.
- [ ] Registrato SHA256 del wheel.
- [ ] Registrati revisore, date, sistemi e versioni degli strumenti.
- [ ] La review è stata eseguita da un checkout pulito.
- [ ] Vault di produzione, credenziali e chiavi private sono esclusi.

## Validazione automatica

- [ ] python -m compileall -q src tests
- [ ] python -m pytest -q
- [ ] python tools/security_static_check.py
- [ ] Ruff eseguito e output archiviato.
- [ ] Bandit eseguito e output archiviato.
- [ ] pip-audit eseguito e output archiviato.
- [ ] Semgrep eseguito e output archiviato.
- [ ] Build e smoke test del wheel in un virtual environment nuovo.

## Review manuale

- [ ] Backend GnuPG, argv, stdin/stdout e gestione errori.
- [ ] Cifratura, firma, trusted signer e fingerprint.
- [ ] Integrità di vault, record, catalogo e cartelle.
- [ ] Scritture atomiche e permessi filesystem.
- [ ] Lock, hard-lock ed eliminazione delle cache.
- [ ] Rilevamento rollback e sostituzione.
- [ ] Parser JSON, URI, riferimenti UUID e configurazione.
- [ ] Migrazione Keys legacy e import KeePassXC XML/KDBX.
- [ ] Approvazione inbox ed export standalone cifrato.
- [ ] Clipboard e durata dei segreti in memoria.
- [ ] Launcher SSH/RDP/URL/generici e confini della shell.
- [ ] Permessi Flatpak e delega verso l'host.
- [ ] Parità GUI/TUI, lista vault recenti e hard-lock con stato cartelle.
- [ ] Fuzzing o property testing dei parser.

## Finding e chiusura

- [ ] Ogni finding contiene severità, impatto, riproduzione e commit/file.
- [ ] I finding Critical e High sono chiusi oppure la release viene rifiutata.
- [ ] I finding Medium hanno responsabile e decisione di mitigazione/rinvio.
- [ ] Le correzioni sono in nuovi commit senza riscrivere il target esaminato.
- [ ] Esistono test di regressione per i problemi azionabili.
- [ ] I rischi residui sono collegati a THREAT_MODEL.md.
- [ ] Report finale e decisione di accettazione sono archiviati.
