# Keys NG M1.18 — Revisione di sicurezza

## Stato e ambito

Questa è una **revisione ingegneristica interna**, non un audit di sicurezza indipendente. Copre il sorgente distribuito come `0.1.18.dev1`. La revisione si concentra su invocazione dei processi crittografici, policy di firma, integrità record/catalogo, scritture filesystem, parser di import, riferimenti, clipboard, launcher esterni e confini della configurazione.

## Metodo

La revisione M1.18 ha usato ispezione del sorgente, lint di sicurezza basato su AST, test unitari/integrati, test deterministici con input malformati, fault injection sulla sostituzione atomica e regressioni per rilevare rollback/sostituzione. La release contiene inoltre un manuale bilingue esaustivo per la code review, con copertura dei simboli verificata dai test.

I binari esterni Ruff/Bandit/pip-audit non erano disponibili nell'ambiente isolato usato per assemblare questo artefatto, quindi **non se ne dichiara l'esecuzione** in questo report. Restano strumenti di sviluppo dichiarati per CI/ambienti connessi. `tools/security_static_check.py`, privo di dipendenze esterne, è stato eseguito con successo.

## Finding corretti in M1.18

### SR-117-01 — Il rollback/sostituzione isolato di un record non era rifiutato durante la lettura ordinaria

**Prima:** `catalog_health()` poteva segnalare mismatch SHA-256, ma `get_entry()` decifrava e restituiva il record senza imporre la corrispondenza con il catalogo firmato.

**Correzione:** `Vault.get_entry()` chiama ora `_verify_record_binding()`. L'UUID del payload deve coincidere con quello del nome file; il catalogo deve contenere il record; SHA-256 del ciphertext e revisione devono coincidere. In caso contrario il comportamento è fail-closed con `VaultError`.

**Rischio residuo:** chi può ripristinare insieme un vecchio catalogo firmato valido e i corrispondenti record firmati validi può ancora riportare il vault a uno snapshot coerente precedente. Per impedirlo serve stato monotono fidato esterno al vault sincronizzato.

### SR-117-02 — Le directory POSIX del vault dipendevano dall'umask

**Prima:** i file ciphertext erano creati `0600`, mentre root del vault e `records/`/`inbox/` usavano i default di `mkdir`.

**Correzione:** l'inizializzazione crea/porta queste directory a `0700` su POSIX; `vault.json` resta `0600`.

### SR-117-03 — Una configurazione con firma obbligatoria poteva non avere signer

**Prima:** `require_signature=True` poteva coesistere con `signer=None`, creando una configurazione incapace di soddisfare la propria policy.

**Correzione:** `VaultConfig.validate()` richiede signer e almeno un trusted signer quando la verifica firma è abilitata.

### SR-117-04 — Il backend a processo accettava sintatticamente selettori più corti di un fingerprint completo moderno

**Prima:** qualunque selettore esadecimale di almeno 32 caratteri passava il controllo preliminare prima del matching con l'elenco GnuPG.

**Correzione:** `GPGProcessBackend.resolve_fingerprint()` accetta solo fingerprint completi da 40 o 64 caratteri esadecimali, poi richiede match esatto con l'output GnuPG.

## Proprietà confermate dalla revisione

- Sottoprocessi crittografici e launcher usano array argv e `shell=False`.
- Nessun `eval`, `exec` built-in, `compile`, `os.system` o `os.popen` è presente in `src/keys_ng` secondo il check AST M1.18.
- Le API Keys NG non accettano passphrase della chiave privata; l'interazione appartiene a GnuPG/gpg-agent/pinentry.
- Le scritture atomiche persistono solo ciphertext, eseguono fsync del file, replace atomico e fsync della directory su POSIX.
- I record Bash legacy sono analizzati come testo/dati e mai eseguiti.
- L'import XML KeePassXC rifiuta DTD/entity prima del parsing.
- I riferimenti UUID sono same-vault, whole-field, limitati a 32 livelli e con rilevamento cicli.
- Le azioni command rifiutano `shell=True`; la validazione SSH è orientata ad argv.
- I record inbox non firmati richiedono approvazione esplicita dell'operatore.
- Catalogo e cartelle in cache vengono eliminati al lock normale; l'hard lock chiede inoltre al backend crypto di terminare gpg-agent.

## Rischi accettati / attività successive

### Rollback coordinato

Le firme autenticano lo snapshot ma non ne provano la freschezza. Un futuro design potrebbe usare un checkpoint monotono fuori dal vault sincronizzato, un log append-only o un servizio di versioning fidato. Non va aggiunto superficialmente perché cambia le proprietà di recovery offline.

### Vita dei segreti in memoria Python

Password/seed TOTP possono esistere in oggetti immutabili Python `str`/`bytes` e venire copiati da widget GUI, decoding JSON e codice clipboard. La zeroizzazione deterministica non è garantibile. Vedere `MEMORY_REVIEW.md`.

### Cronologia clipboard

Keys NG cancella il valore clipboard che riesce ancora a identificare/controllare. History manager desktop possono conservarne copie.

### Compromissione endpoint same-user

Un processo malevolo con gli stessi privilegi può potenzialmente leggere clipboard, memoria, socket agent o invocare operazioni GnuPG autorizzate. L'hard lock riduce l'esposizione della cache agent ma non difende da un endpoint compromesso.

### Azioni esterne trusted

`shell=False` elimina l'interpretazione dei metacaratteri shell da parte di Keys NG. Non rende innocue azioni command arbitrarie; opzioni OpenSSH come `ProxyCommand`/`LocalCommand` possono eseguire programmi per design. I record che le contengono sono configurazione eseguibile trusted.

### Accesso host Flatpak

Il design Flatpak delega intenzionalmente GnuPG/SSH/RDP all'host usando `flatpak-spawn --host` e richiede accesso al servizio Flatpak. Riduce la duplicazione delle chiavi ma amplia il confine di fiducia del sandbox. Il manifest finale dovrebbe ricevere una revisione indipendente specifica prima della pubblicazione stabile.

## Conclusione

M1.18 migliora concretamente l'integrità fail-closed e la revisionabilità senza cambiare il modello OpenPGP per-record. Resta un password manager pre-1.0 non sottoposto ad audit indipendente. Per uso di produzione sono ancora raccomandati backup verificati e un percorso di recovery indipendente fino al completamento di una revisione esterna.

## Note di revisione M1.18 sulla parità TUI

- La conversione degli editor GUI e TUI condivide ora `services.entry_editor`, riducendo la divergenza delle validazioni tra frontend.
- Rename/move delle cartelle valida una copia di `FolderStore`; un'operazione rifiutata non può lasciare la cache decifrata delle cartelle parzialmente mutata.
- Lo spostamento cartelle rifiuta nomi fratelli duplicati oltre ai cicli.
- Le operazioni distruttive TUI richiedono conferma; la modifica è delegata a `Vault`.
- I banner clipboard non mostrano mai il segreto copiato, solo categoria/esito. I colori semantici del tema sono il default; gli override utente riguardano solo la presentazione.
- L'import TOTP QR nella TUI legge un percorso immagine locale scelto dall'utente e lo passa al decoder QR esistente.
