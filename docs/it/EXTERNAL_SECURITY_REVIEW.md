# Pacchetto per la review di sicurezza esterna

## Scopo

Questo documento prepara la review indipendente di Keys NG 0.1.27. È materiale preparatorio, non un audit e non dimostra che l'implementazione sia stata validata esternamente.

Il revisore deve analizzare l'esatto tag e commit consegnato dal maintainer. L'ambito comprende core Python, CLI, TUI, GUI, GnuPG, storage del vault, import/export, clipboard, launcher esterni e delega Flatpak verso l'host.

## Materiale da consegnare

- Tag, commit SHA e SHA256 dell'archivio sorgente.
- Wheel e checksum SHA256.
- ROADMAP.md.
- THREAT_MODEL.md, SECURITY_REVIEW.md, MEMORY_REVIEW.md e VAULT_FORMAT_1.0.md.
- CODE_REVIEW_MANUAL.md inglese e italiano.
- RELEASE_SECURITY_CHECKLIST.md.
- Report completo dei test con OS, Python, GnuPG e dipendenze.
- Fixture sanificate o vault creato dal revisore. Non consegnare credenziali reali, chiavi private o vault di produzione.

Usare un checkout pulito e un keyring di test separato. Non concedere accesso a vault di produzione o chiavi private.

## Ambito

### Crittografia e storage

Verificare cifratura, firma opzionale, trusted signer, invocazione GnuPG, argv, stdin/stdout, configurazione, binding UUID dei record, catalogo, cartelle, scritture atomiche, permessi, lock, hard-lock e rilevamento rollback/sostituzione.

### Input non fidati

Analizzare parser JSON, catalogo, URI, riferimenti UUID, Keys legacy, KeePassXC XML/KDBX, inbox e configurazione. Verificare rifiuto DTD/entity, limiti e cicli dei riferimenti, input malformati e avvisi per import parziali KeePassXC. Eseguire fuzzing o property testing sui parser.

### Gestione dei segreti

Tracciare password, username, seed TOTP e passphrase attraverso memoria Python, widget Qt/Textual, clipboard e subprocess. Verificare delega delle passphrase a GnuPG/pinentry e assenza in argv o log. Esaminare timeout, read-back, cronologia clipboard, export standalone e approvazione inbox.

### Esecuzione esterna e packaging

Analizzare launcher SSH, RDP, URL e generici, shell=False, tokenizzazione argv e implicazioni deliberate di ProxyCommand. Analizzare separatamente permessi Flatpak e host-spawn.

### GUI e TUI

Verificare lock/unlock, preferenze, avvisi import, export standalone, ricerca, lista dei tre vault recenti, percorsi non validi e hard-lock globale GUI con più vault e cartelle aperte/chiuse. Confermare che errori e diagnostica non espongano segreti o JSON decifrato.

## Procedura

1. Congelare il target e registrare tag, commit SHA, SHA256 sorgente e SHA256 wheel.
2. Creare un ambiente isolato senza accesso a vault di produzione o chiavi private.
3. Registrare OS, Python, GnuPG e versioni delle dipendenze.
4. Eseguire: python -m compileall -q src tests.
5. Eseguire: python -m pytest -q.
6. Eseguire: python tools/security_static_check.py.
7. In ambiente connesso eseguire Ruff, Bandit, pip-audit e Semgrep, registrando versioni e output completo.
8. Costruire e provare il wheel in un virtual environment nuovo.
9. Creare chiavi GnuPG e vault temporanei. Provare init, add, search, copy, lock, hard-lock, inbox, export standalone e recovery.
10. Importare fixture KeePassXC con riferimenti validi, mancanti, cicli, campi malformati, URL comando e campi comando personalizzati.
11. Usare il manuale esaustivo di code review, dando priorità a storage, crypto, scritture atomiche, inbox, clipboard, actions, opzioni SSH e parser di migrazione.
12. Eseguire fuzzing o property testing sui parser e conservare riproduzioni minime.
13. Esaminare separatamente permessi Flatpak e comportamento host-spawn.
14. Registrare ogni finding con severità, commit/file, riproduzione, impatto, correzione e verifica.
15. Applicare correzioni e test in nuovi commit, senza riscrivere silenziosamente il target esaminato.
16. Richiedere un report finale con ambito, esclusioni, strumenti, finding, rischi residui ed esatti commit esaminati.

## Criteri di accettazione

Usare le severità Critical, High, Medium, Low e Informational. Non accettare una release candidate con finding Critical o High aperti. I finding Medium devono avere un responsabile e una decisione esplicita di mitigazione o rinvio. Collegare i rischi residui al THREAT_MODEL.md.

## Consegne da richiedere

Richiedere executive summary, ambito e commit, inventario ambiente/strumenti, finding prioritizzati, PoC o test di regressione, verifica delle correzioni, registro rischi residui e limitazioni.

## Modello evidenze

- Target/tag:
- Commit SHA:
- SHA256 archivio sorgente:
- SHA256 wheel:
- Revisore:
- Date review:
- Sistemi operativi:
- Versioni Python/GnuPG:
- Comandi eseguiti:
- Finding:
- Rischi residui accettati:
- Decisione finale:
