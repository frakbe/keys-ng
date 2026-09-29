# M1.18 — Checklist di sicurezza della release

- [x] Versione sincronizzata a `0.1.18.dev1` in Python e metadati Briefcase.
- [x] Suite di test completa superata.
- [x] Sorgenti Python compilati con `compileall`.
- [x] Check di sicurezza AST senza dipendenze superato.
- [x] Nessun `shell=True`, `eval`/`exec`/`compile` built-in, `os.system` o `os.popen` nel sorgente applicativo.
- [x] Permessi delle directory vault POSIX coperti da test.
- [x] Fault injection sul replace atomico coperta da test.
- [x] Corpus deterministico di JSON malformati coperto da test.
- [x] Rollback/sostituzione di un singolo record fallisce closed durante la lettura ordinaria.
- [x] Mismatch UUID payload/nome file fallisce closed.
- [x] Config con firma obbligatoria non può omettere signer/trusted signer.
- [x] Il backend GnuPG a processo richiede fingerprint completi da 40/64 caratteri.
- [x] Formato vault 1.0 documentato/congelato per la revisione.
- [x] Threat model documentato in inglese e italiano.
- [x] Limiti sulla vita dei segreti in memoria documentati.
- [x] Ogni classe/funzione Python documentata in entrambi i manuali e copertura verificata dai test.
- [ ] Code review indipendente — requisito esterno.
- [ ] Penetration/security audit indipendente — requisito esterno.
- [ ] Esecuzione Ruff/Bandit/pip-audit/Semgrep in ambiente connesso — non dichiarata da questo assemblaggio offline.
- [ ] Smoke test packaging reali Windows/macOS — richiedono runner/hardware dei rispettivi OS.
- [ ] Matrice hardware token (YubiKey/OpenPGP card) — richiede dispositivi fisici.

## Delta parità M1.18

- [x] Conversione e validazione voce condivise tra GUI/TUI.
- [x] Un fallimento di move/rename cartella lascia invariata la cache decifrata.
- [x] Test di regressione per cicli e nomi fratelli duplicati.
- [x] Superficie TUI crea/modifica/sposta/elimina coperta da test.
- [x] Round-trip della configurazione banner clipboard testato.
- [x] Manuale bilingue esaustivo di code review rigenerato dal sorgente M1.18.

## Integrazioni M1.19

- [x] La creazione del vault è centralizzata in `services.vault_init` e valida destinatari, fingerprint completi e stato della directory di destinazione.
- [x] Prima di creare i file del vault viene eseguito un self-test crittografico cifratura/decifratura/firma.
- [x] Le procedure Nuovo Vault di GUI e TUI usano lo stesso servizio core del comando CLI `init`.
- [x] Il rilevamento GnuPG su Windows è centralizzato e non invoca una shell.
- [x] Gli override degli eseguibili GnuPG memorizzano solo percorsi, mai credenziali.
- [x] Sono presenti metadata licenza PEP 639 per il packaging.
- [x] Test sorgente e controllo statico di sicurezza passano nell'ambiente di assemblaggio della release.
- [ ] Rieseguire Briefcase `create/build/run/package` per M1.19 su un host Windows reale; la procedura è in `WINDOWS_MSI_BUILD.md`.
