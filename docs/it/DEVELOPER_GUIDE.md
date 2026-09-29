# Keys NG — Guida al codice, dall'architettura alle singole funzioni

**Versione del codice descritta:** `0.1.18.dev1` / milestone M1.18.1  
**Destinatario:** sviluppatore con basi di Python, programmazione a oggetti e moduli, ma non necessariamente esperto di Qt, Textual, OpenPGP o packaging Python.  
**Obiettivo:** permetterti di capire, mantenere e modificare Keys NG senza dover ricostruire ogni volta l'architettura del progetto.

---

## Documentazione M1.18 per i revisori

Per una revisione indipendente di sicurezza/codice, questa guida va letta insieme a `CODE_REVIEW_MANUAL.md`, che contiene una voce derivata dal sorgente per ogni classe, metodo, funzione e helper annidato Python, con intervalli di righe, firme, mappe delle chiamate dirette e indicazioni sugli effetti di sicurezza. `THREAT_MODEL.md`, `VAULT_FORMAT_1.0.md`, `SECURITY_REVIEW.md`, `MEMORY_REVIEW.md` e `RELEASE_SECURITY_CHECKLIST.md` definiscono ambito e rischi residui.


## Regola M1.18 per la parità dei frontend

GUI e TUI non devono implementare separatamente la validazione delle credenziali. Entrambe costruiscono un `EntryDraft` e chiamano `build_entry_from_draft()` da `services/entry_editor.py`. Questa è la trasformazione canonica dai campi dell'editor all'`Entry` di dominio; durante una modifica vengono preservate le azioni command importate e i custom field che gli editor non espongono direttamente. La riorganizzazione delle cartelle resta responsabilità di `Vault`, così i controlli contro cicli e nomi duplicati valgono per qualunque frontend.

La TUI Textual usa schermate modali per editor della voce, nome cartella, spostamento e conferma distruttiva. Gli esiti della clipboard sono mostrati in un banner temporizzato: con override colore vuoti si usano i colori semantici del tema Textual, mentre foreground/background espliciti provengono da `[ui.tui]`.

## 1. Come leggere questa guida

Questa documentazione segue un approccio **Top-Down**:

1. prima descrive il sistema come una scatola nera;
2. poi mostra i sottosistemi principali;
3. quindi segue i workflow reali (apertura vault, ricerca, salvataggio, TOTP, SSH, clipboard, import);
4. infine scende a livello di modulo, classe e funzione;
5. chiude con una serie di “ricette di modifica” per sapere **dove intervenire** quando vuoi aggiungere o cambiare una funzionalità.

Una regola mentale utile è questa:

> **GUI, TUI e CLI non sono il password manager. Sono solo tre interfacce verso lo stesso core.**

Il cuore dell'applicazione è costituito soprattutto da:

- `models.py`: definisce i dati;
- `storage/vault.py`: gestisce il vault;
- `crypto/*`: cifra, decifra e verifica le firme;
- `services/*`: esegue operazioni accessorie (TOTP, clipboard, launcher SSH/RDP, password generator);
- `storage/settings.py` e `storage/config.py`: configurazione globale e configurazione del singolo vault.

---

# Parte I — Quadro generale

## 2. Il modello mentale di Keys NG

Keys NG può essere visto come sei strati sovrapposti:

```text
┌───────────────────────────────────────────────────────────┐
│                    FRONTEND                               │
│     CLI                TUI                 GUI            │
│  argparse            Textual             PySide6         │
└───────────────┬──────────┬──────────────────┬──────────────┘
                │          │                  │
                └──────────┴─────────┬────────┘
                                     ▼
┌───────────────────────────────────────────────────────────┐
│                    CORE / VAULT                           │
│                  storage/vault.py                         │
│  record, catalogo, folder, ricerca, lock, reindex         │
└───────────────────────────┬───────────────────────────────┘
                            │
             ┌──────────────┼────────────────┐
             ▼              ▼                ▼
┌─────────────────┐ ┌────────────────┐ ┌──────────────────┐
│  MODELLO DATI   │ │    SERVICES    │ │      CRYPTO      │
│   models.py     │ │ totp/clipboard │ │ gpg_process.py   │
│                 │ │ actions/qr/... │ │ CryptoBackend    │
└─────────────────┘ └────────────────┘ └────────┬─────────┘
                                                │
                                                ▼
                                        ┌─────────────┐
                                        │ GnuPG/agent │
                                        └─────────────┘
```

Questa separazione è fondamentale. Per esempio, quando premi `Ctrl+C` nella GUI:

```text
QShortcut
   ↓
Window.copy_password_clicked()
   ↓
copy_secret_qt()
   ↓
clipboard del sistema
```

La GUI non sa come generare un TOTP e non sa come decifrare GPG. Delega queste attività ai servizi e al vault.

---

## 3. Struttura del repository

La parte eseguibile principale è sotto `src/keys_ng/`:

```text
src/keys_ng/
├── cli/
│   └── main.py                CLI scriptabile
├── crypto/
│   ├── backend.py             interfaccia astratta crittografica
│   ├── factory.py             scelta del backend
│   ├── gpg_process.py         backend GnuPG reale
│   └── gpgme_backend.py       placeholder backend GPGME
├── gui/
│   └── main.py                GUI PySide6
├── i18n/
│   └── manager.py             gettext
├── migration/
│   ├── keepassxc.py           import KeePassXC
│   ├── legacy_parser.py       parser sicuro Keys legacy
│   └── migrator.py            migrazione Keys legacy → Keys NG
├── platform/
│   ├── app_identity.py        nome/icona/app-id
│   ├── desktop_integration.py integrazione GNOME/freedesktop
│   └── paths.py               directory standard
├── services/
│   ├── actions.py             apertura URL, SSH, RDP, command
│   ├── clipboard.py           clipboard GUI/CLI/TUI
│   ├── clipboard_helper.py    processo separato per timeout clipboard
│   ├── passwords.py           generatore password
│   ├── qr.py                  lettura QR TOTP
│   ├── ssh_options.py         parsing opzioni SSH avanzate
│   └── totp.py                calcolo e parsing TOTP
├── storage/
│   ├── atomic.py              scritture atomiche di ciphertext
│   ├── config.py              vault.json
│   ├── inbox.py               inbox write-only
│   ├── settings.py            config.toml globale
│   └── vault.py               oggetto centrale Vault
├── tui/
│   └── main.py                TUI Textual
├── errors.py                  eccezioni applicative
└── models.py                  dataclass del dominio
```

I test sono sotto `tests/`. La documentazione utente è in `README*.md`, `SECURITY*.md`, `docs/` e nelle risorse di help incorporate nel package.

---

## 4. I due tipi di configurazione: non confonderli

Keys NG ha **due configurazioni con scopi diversi**.

### 4.1 Configurazione globale dell'applicazione

File tipico Linux:

```text
~/.config/keys-ng/config.toml
```

È gestito da `AppSettings` in `storage/settings.py` e contiene preferenze locali dell'utente:

- lingua;
- timeout clipboard;
- auto-lock;
- backend crittografico;
- vista albero espansa/compatta;
- terminale da usare per SSH;
- client e opzioni RDP.

Queste impostazioni **non fanno parte del vault** e possono differire da computer a computer.

### 4.2 Configurazione del singolo vault

File:

```text
<Vault>/vault.json
```

È gestito da `VaultConfig` in `storage/config.py` e contiene proprietà strutturali del vault:

- fingerprint dei destinatari OpenPGP;
- fingerprint della chiave di firma;
- firmatari fidati;
- obbligo di firma;
- livello di privacy del catalogo.

Questo file accompagna il vault ed è necessario per interpretarlo correttamente.

---

## 5. Cosa c'è fisicamente dentro un vault

```text
my-vault/
├── vault.json
├── catalog.gpg
├── folders.gpg
├── records/
│   ├── <uuid>.gpg
│   ├── <uuid>.gpg
│   └── ...
└── inbox/
    └── <uuid-casuale>.gpg
```

### `records/*.gpg`

Ogni file contiene **una sola Entry JSON cifrata e, normalmente, firmata**.

### `folders.gpg`

Contiene la struttura logica delle cartelle. Le cartelle non sono directory reali del filesystem, così il provider cloud non vede nomi come `Banca`, `Lavoro`, `Server-Produzione`.

### `catalog.gpg`

È un indice cifrato usato per:

- visualizzare l'elenco senza decifrare ogni record;
- ricercare velocemente;
- sapere se una voce contiene password/TOTP/azione;
- scegliere l'icona GUI;
- verificare hash e coerenza.

### `inbox/`

Permette a un sistema che possiede soltanto la **chiave pubblica** di depositare nuove entry cifrate senza poter leggere il vault.

---

# Parte II — I dati

## 6. `models.py`: il vocabolario del programma

`models.py` è il punto migliore da leggere per primo quando vuoi capire quali dati esistono nel sistema.

### 6.1 `SCHEMA_VERSION`

```python
SCHEMA_VERSION = 1
```

Indica la versione del formato JSON interno. Se in futuro cambiassi in modo incompatibile la struttura delle entry, dovresti aumentare questo numero e implementare una migrazione.

### 6.2 `utc_now()`

Restituisce una data UTC ISO-8601 senza microsecondi, ad esempio:

```text
2026-08-19T09:31:00Z
```

Viene usata per `created_at` e `updated_at`.

---

## 7. `TotpConfig`

Rappresenta i parametri necessari per generare un TOTP:

```text
secret
issuer
account_name
algorithm
 digits
period
```

### `validate()`

Controlla che:

- algoritmo ∈ `SHA1`, `SHA256`, `SHA512`;
- cifre ∈ 6, 7, 8;
- periodo sia tra 5 e 300 secondi;
- il secret non sia vuoto.

Nota: la validità Base32 vera e propria viene verificata anche nel servizio `totp_from_secret()`.

---

## 8. `Action`

Una `Action` dice **cosa può essere aperto/eseguito** da una entry.

Tipi supportati:

```text
url
ssh
rdp
command
```

Campi principali:

- `url`: per un sito;
- `host`, `port`, `username`: SSH/RDP;
- `argv`: comando strutturato;
- `shell`: deve restare `False`;
- `ssh_x11_forwarding`: `off`, `X` o `Y`;
- `ssh_options`: lista argv delle opzioni avanzate SSH.

### `Action.validate()`

Questa funzione è una barriera di sicurezza importante. Verifica, tra l'altro:

- nessuna azione shell;
- URL obbligatorio per `url`;
- host obbligatorio per `ssh`/`rdp`;
- argv non vuoto per `command`;
- tipo conosciuto;
- porta tra 1 e 65535;
- opzioni SSH usate solo su azioni SSH;
- validazione delle opzioni avanzate tramite `validate_ssh_options()`.

Quando aggiungi un nuovo tipo di azione, devi quasi certamente modificare **sia questa classe sia `services/actions.py`**.

---

## 9. `Folder` e `FolderStore`

### `Folder`

Una cartella è molto semplice:

```text
id UUID
name
parent_id
created_at
updated_at
```

Una sottocartella punta al genitore tramite UUID.

### `Folder.create()`

Genera un nuovo UUID casuale e costruisce la cartella.

### `Folder.validate()`

Controlla:

- UUID valido;
- `parent_id` valido;
- impossibilità di essere genitore di se stessa;
- nome non vuoto;
- nessuno slash/backslash nel nome.

Gli slash sono vietati perché i percorsi logici come `Lavoro/Server/Prod` vengono costruiti dal rapporto parent/child, non memorizzati nel nome.

### `FolderStore`

È il contenitore serializzato in `folders.gpg`.

`FolderStore.validate()` verifica l'intera struttura:

1. schema corretto;
2. nessun ID duplicato;
3. ogni parent deve esistere;
4. assenza di cicli nella gerarchia.

`to_bytes()` serializza a JSON UTF-8 compatto.  
`from_bytes()` fa il percorso inverso e **valida sempre** il risultato.

---

## 10. `Entry`: il record completo

`Entry` rappresenta una credenziale completa.

Campi:

```text
id                  UUID
 title               nome mostrato all'utente
kind                website / ssh / rdp / account / ...
usernames           lista di username
password            password opzionale
totp                lista TotpConfig
actions             lista Action
tags                tag
notes               note testuali
custom_fields       campi importati/arbitrari
folder_id           cartella logica
revision            revisione monotona locale
created_at
updated_at
schema
```

### `Entry.create(title, **kwargs)`

Factory semplice che genera automaticamente l'UUID.

### `Entry.validate()`

Controlla:

- schema;
- UUID;
- UUID cartella se presente;
- titolo non vuoto;
- revision ≥ 1;
- tutti i TOTP;
- tutte le azioni.

### `to_bytes()`

Serializza la dataclass in JSON canonico-ish:

- `ensure_ascii=False`: conserva Unicode;
- `sort_keys=True`: ordine stabile;
- separatori compatti.

Il risultato in bytes viene passato alla crittografia.

### `from_bytes()`

Legge JSON, ricostruisce oggetti `TotpConfig` e `Action`, applica default per campi introdotti successivamente e valida l'entry.

Questo metodo è il punto in cui implementare compatibilità con una futura versione del record.

---

## 11. `CatalogItem` e `Catalog`

`CatalogItem` è una **vista ridotta** di una Entry. Non deve contenere necessariamente tutti i dati del record.

Campi importanti:

- `id`, `title`, `kind`;
- username/tags/host in funzione della privacy;
- `capabilities`;
- `revision`;
- `ciphertext_sha256`;
- `folder_id`.

`capabilities` può contenere valori come:

```text
password
totp
actions
action:url
action:ssh
action:rdp
action:command
```

La GUI le usa anche per scegliere l'icona senza decifrare l'entry.

`Catalog` contiene:

- lista `items`;
- snapshot delle `folders`;
- schema.

Il catalogo è una **cache ricostruibile**: `Vault.reindex()` può rigenerarlo dai record cifrati.

---

# Parte III — Il cuore: `Vault`

## 12. Perché `Vault` è la classe più importante

`storage/vault.py` è il vero coordinatore del password manager.

Le interfacce dovrebbero chiedere a `Vault`:

```text
salva entry
leggi entry
cerca
crea cartella
sposta cartella
blocca vault
reindicizza
```

Non dovrebbero manipolare direttamente `catalog.gpg` o `records/*.gpg`.

---

## 13. `Vault.__init__()`

Quando fai:

```python
vault = Vault(path, crypto)
```

succede questo:

1. normalizza il percorso con `expanduser()` e `resolve()`;
2. conserva il backend crittografico;
3. carica `vault.json` con `VaultConfig.load()`;
4. parte sbloccato (`_locked = False`);
5. inizializza due cache RAM:
   - `_catalog_cache`;
   - `_folders_cache`;
6. rimuove eventuali file temporanei ciphertext lasciati da una scrittura interrotta.

Le cache sono intenzionali: permettono una ricerca veloce senza chiamare GnuPG centinaia di volte.

---

## 14. `Vault.init()`

È il costruttore di un nuovo vault.

Flusso:

```text
controlla directory vuota
        ↓
crea records/ e inbox/
        ↓
crea VaultConfig
        ↓
scrive vault.json
        ↓
crea oggetto Vault
        ↓
crea folders.gpg vuoto
        ↓
crea catalog.gpg vuoto
```

Su Unix `vault.json` riceve permessi `0600`.

Il file non contiene password, ma contiene informazioni su fingerprint e policy, quindi è comunque ragionevole limitarne i permessi.

---

## 15. Lock e unlock

### `locked`

Property read-only che restituisce `_locked`.

### `lock(hard=False)`

Fa tre cose:

```text
_locked = True
catalog cache = None
folder cache  = None
```

Con `hard=True` chiama anche:

```python
self.crypto.hard_lock()
```

Nel backend GPG questo termina `gpg-agent` e quindi elimina la sua cache di autorizzazione.

### `unlock()`

Imposta temporaneamente `_locked = False`, poi prova a leggere e verificare catalogo e cartelle. Se qualcosa fallisce, torna bloccato.

Questo significa che “unlock” non contiene la passphrase: è GnuPG/gpg-agent a chiedere eventualmente l'autorizzazione privata.

### `_require_unlocked()`

Guardia interna. Ogni operazione sensibile la chiama e solleva `VaultError` se il vault è bloccato.

---

## 16. Firma e crittografia interne

### `_verify(signer_fingerprint, signature_valid)`

Applica la policy definita da `vault.json`.

Se `require_signature=False`, non fa nulla.

Altrimenti richiede:

1. firma valida;
2. fingerprint presente;
3. fingerprint compreso in `trusted_signers`.

### `_encrypt(plaintext)`

Chiama:

```python
crypto.encrypt(
    plaintext,
    config.recipients,
    config.signer,
)
```

### `_decrypt(ciphertext)`

Chiama il backend, ottiene `DecryptionResult`, verifica la firma con `_verify()` e restituisce soltanto il plaintext.

Questa è la ragione per cui altre parti del programma dovrebbero usare `Vault._decrypt()` invece di chiamare direttamente `crypto.decrypt()` quando stanno leggendo un oggetto del vault.

---

## 17. Catalogo e cartelle: cache RAM

### `_write_catalog(catalog)`

```text
Catalog → JSON bytes → encrypt/sign → atomic_write_ciphertext
```

Dopo una scrittura riuscita aggiorna `_catalog_cache`.

### `_write_folders(store)`

Identico concettualmente per `folders.gpg`.

### `load_catalog()`

Se la cache esiste, la restituisce immediatamente.

Altrimenti:

```text
catalog.gpg
  ↓ read_bytes
_decrypt
  ↓
Catalog.from_bytes
  ↓
cache RAM
```

### `load_folders()`

Stesso principio. Include compatibilità con i vault M1.0–M1.3: se `folders.gpg` non esiste, usa le cartelle eventualmente presenti nello snapshot del catalogo.

Questa architettura risolve il vecchio problema di ricerca lenta: durante una sessione sbloccata i metadati non vengono decifrati continuamente.

---

## 18. `_catalog_item()`: da Entry a indice

Questa funzione crea il record ridotto del catalogo.

Prima ricava gli host dalle azioni:

- URL → hostname tramite `urlparse`;
- SSH/RDP → `action.host`.

Poi costruisce `capabilities`.

Infine applica `catalog_privacy`:

### `minimal`

Non include username, tag o host.

### `standard`

Include i tag ma non username/host.

### `full`

Include anche username e host.

In tutti i casi il catalogo resta cifrato, ma questa opzione riduce la quantità di metadata che resta in memoria quando il catalogo viene aperto.

`ciphertext_sha256` è l'hash del **file cifrato**, non del plaintext.

---

## 19. `save_entry()` — workflow completo di salvataggio

È una delle funzioni da capire meglio.

```text
Entry
  ↓ validate
controllo folder_id
  ↓
updated_at = now
  ↓
Entry.to_bytes()
  ↓
_encrypt()
  ↓
atomic_write records/<id>.gpg
  ↓
load catalog
  ↓
crea CatalogItem
  ↓
sostituisce item precedente
  ↓
ordina per titolo
  ↓
sincronizza snapshot cartelle
  ↓
scrive catalog.gpg
```

Nota importante: record e catalogo sono due file distinti; non esiste una transazione filesystem unica che li aggiorni insieme. Per questo esistono `reindex()` e `catalog_health()` come meccanismi di recupero/verifica.

---

## 20. `get_entry()` e `delete_entry()`

### `get_entry(entry_id)`

1. costruisce `records/<uuid>.gpg`;
2. verifica che esista;
3. decifra e verifica la firma;
4. passa il plaintext a `Entry.from_bytes()`.

### `delete_entry(entry_id)`

1. elimina il file `.gpg`;
2. rimuove l'item dal catalogo;
3. riscrive il catalogo cifrato.

Non usa `shred`: il file eliminato è ciphertext.

---

## 21. `list_items()`

Senza `folder_id` restituisce tutto il catalogo.

Con `folder_id` filtra gli item.

Se `recursive=True`, calcola ricorsivamente l'insieme di tutte le sottocartelle e restituisce anche le relative entry.

---

## 22. Percorsi delle cartelle

### `_folder_paths_from(folders)`

Costruisce una mappa:

```text
folder UUID → "Personali/Cloud/Server"
```

Lo fa con memoizzazione (`cache`) per evitare di risalire ripetutamente gli stessi parent.

Ha anche un controllo anti-ciclo durante la risoluzione.

### `folder_paths(catalog_snapshot=False)`

Decide se costruire i percorsi da:

- `folders.gpg` reale;
- snapshot delle cartelle presente in `catalog.gpg`.

La ricerca usa lo snapshot catalogo per poter fare normalmente **una sola decrypt**.

### `folder_path(folder_id)`

Restituisce il percorso di una singola cartella.

### `resolve_folder_path(path)`

Fa l'opposto:

```text
"Lavoro/Server/Prod" → UUID folder
```

Il confronto è case-insensitive tramite `casefold()`.

---

## 23. `search()`

La ricerca è volutamente semplice e veloce.

```python
needle = query.casefold().strip()
```

Per ogni `CatalogItem` costruisce una stringa con:

- titolo;
- tipo;
- username se presenti nel livello privacy;
- tag;
- host URL;
- capabilities;
- percorso cartella.

Poi fa:

```python
if needle in haystack:
```

Quindi attualmente è una ricerca substring, non un motore full-text.

Punti importanti:

- non apre ogni record;
- non cerca nelle password;
- non cerca nelle note, perché le note non sono nel catalogo;
- con privacy `minimal`, username/host non sono ricercabili senza cambiare architettura.

---

## 24. `reindex()`

Rigenera il catalogo da zero:

```text
for each records/*.gpg
    decrypt
    Entry.from_bytes
    _catalog_item
sort
snapshot folders
write catalog.gpg
```

È un'operazione più lenta perché decifra tutte le entry, ma serve solo per manutenzione o migrazione.

---

## 25. `catalog_health()`

Controlla la coerenza senza bisogno di fidarsi ciecamente del catalogo.

Verifica:

- record presente ma assente dal catalogo;
- hash del ciphertext differente;
- entry che punta a cartella inesistente;
- catalogo che punta a record inesistente;
- snapshot cartelle del catalogo diverso da `folders.gpg`.

Restituisce:

```python
(ok: bool, issues: list[str])
```

---

## 26. API delle cartelle

### `list_folders()`

Restituisce le cartelle ordinate per percorso completo.

### `get_folder(id)`

Lookup semplice per UUID.

### `create_folder(name, parent_id=None)`

Controlla parent, duplicati tra sibling, valida struttura, scrive `folders.gpg`, aggiorna snapshot catalogo.

### `create_folder_path(path)`

È una funzione comoda usata dai migratori.

Con:

```text
Lavoro/Server/Prod
```

crea solo i livelli mancanti e restituisce la cartella finale.

### `rename_folder()`

Controlla duplicati nello stesso parent, aggiorna timestamp, valida e riscrive folder+catalogo.

### `move_folder()`

Cambia `parent_id`. `FolderStore.validate()` rileva eventuali cicli.

### `delete_folder()`

Rifiuta l'eliminazione se contiene:

- sottocartelle;
- entry.

### `move_entry()`

Carica l'entry completa, cambia `folder_id`, incrementa `revision`, chiama `save_entry()`.

---

# Parte IV — Crittografia

## 27. `CryptoBackend`: perché esiste un'interfaccia astratta

`crypto/backend.py` separa il resto del programma dall'implementazione concreta GnuPG.

L'interfaccia richiede:

```python
encrypt(...)
decrypt(...)
diagnose(...)
```

ed espone inoltre:

```python
list_keys()
resolve_fingerprint()
hard_lock()
```

Questo rende possibile testare `Vault` con un backend finto, e in futuro inserire GPGME senza riscrivere il core.

---

## 28. `DecryptionResult`

Il backend non restituisce solo plaintext. Restituisce:

```text
plaintext
signer_fingerprint
signature_valid
```

Questo è necessario perché **decifrare** e **fidarsi del contenuto** sono due operazioni distinte.

---

## 29. `KeyInfo`

Rappresenta una chiave OpenPGP scoperta:

- fingerprint;
- user IDs;
- capacità encrypt/sign;
- presenza chiave segreta;
- revoked/expired.

La property `label` costruisce una stringa leggibile del tipo:

```text
Mario Rossi <mario@example.org> [FINGERPRINT...]
```

---

## 30. `GPGProcessBackend`

È il backend attualmente usato davvero.

Principio di sicurezza centrale:

> **mai `shell=True`; plaintext/ciphertext passano via pipe stdin/stdout.**

### `__init__()`

Sceglie `gpg`, `gpg2` o il percorso passato esplicitamente. Può usare un `homedir` GnuPG alternativo, utile nei test.

### `_base_args()`

Aggiunge `--homedir <path>` quando necessario.

### `_run(args, data, check=True)`

Wrapper centrale attorno a `subprocess.run()`.

Comando costruito come lista argv:

```python
[self.executable, *base_args, *args]
```

`data` va su stdin. stdout/stderr vengono catturati.

Se il return code è non-zero e `check=True`, solleva `CryptoError`.

### `encrypt()`

Costruisce un comando GnuPG con:

- `--batch`;
- `--no-tty`;
- destinatari;
- eventuale `--local-user signer --sign`;
- `--encrypt`;
- output su stdout.

Non gestisce la passphrase: se serve, è gpg-agent/pinentry a occuparsene.

### `decrypt()`

Usa `--status-fd 2` per ricevere output machine-readable sullo stderr.

Cerca una riga:

```text
[GNUPG:] VALIDSIG <fingerprint> ...
```

Se la trova, imposta firma valida e fingerprint.

### `list_keys(secret=False)`

Usa il formato `--with-colons`, molto più stabile da parsare dell'output umano.

Ricostruisce `KeyInfo` analizzando record:

```text
pub/sec
fpr
uid
```

### `resolve_fingerprint()`

Keys NG richiede volutamente fingerprint lunghi, non short ID o nomi. Controlla che il selettore sia esadecimale e abbastanza lungo, quindi cerca match esatto.

### `hard_lock()`

Esegue:

```text
gpgconf --kill gpg-agent
```

Questo ha effetto globale sull'agent dell'utente: può influenzare anche altre applicazioni GPG.

### `diagnose()`

Raccoglie una serie di controlli per il comando diagnostico:

- esistenza `gpg`;
- `gpgconf`;
- versione;
- numero chiavi pubbliche;
- numero chiavi segrete.

---

## 31. `crypto/factory.py`

`create_crypto_backend(preference="auto")` è il punto unico dove viene deciso quale backend usare.

Quando in futuro implementerai davvero `GPGMEBackend`, è qui che dovrà essere integrato.

Regola: frontend e `Vault` non dovrebbero istanziare direttamente `GPGProcessBackend` salvo casi di test.

---

# Parte V — Scritture sicure e storage

## 32. `atomic_write_ciphertext()`

Questa funzione è importante per la robustezza del vault.

Non scrive direttamente sopra il file finale. Fa:

```text
crea .nome.random.tmp con O_EXCL
        ↓
scrive ciphertext
        ↓
flush
        ↓
fsync file
        ↓
os.replace(tmp, final)
        ↓
fsync directory (Unix)
```

Il file temporaneo contiene **solo ciphertext**.

`os.replace()` è atomico sullo stesso filesystem: o si vede il vecchio file o quello nuovo, non metà file.

Nel `finally` prova sempre a rimuovere il temp.

### `remove_stale_ciphertext_temps()`

All'avvio elimina temp abbandonati del pattern `.*.*.tmp`. Essendo ciphertext, non serve shred.

---

## 33. Inbox write-only

### `deposit_entry()`

Serve quando una macchina può cifrare verso il vault ma non può leggere catalogo/private key.

```text
Entry.validate
  ↓
Entry.to_bytes
  ↓
crypto.encrypt(recipient public key)
  ↓
inbox/<uuid-random>.gpg
```

Non serve accesso al catalogo.

### `import_inbox(vault)`

Sulla macchina autorizzata:

1. legge ogni `.gpg`;
2. usa `vault._decrypt()`, quindi verifica la firma secondo policy;
3. ricostruisce `Entry`;
4. controlla collisione ID;
5. `vault.save_entry()`;
6. opzionalmente elimina il ciphertext inbox.

Gli errori vengono riportati per file invece di interrompere tutto.

---

# Parte VI — Configurazione

## 34. `VaultConfig` (`vault.json`)

Campi:

```text
recipients
signer
trusted_signers
require_signature
catalog_privacy
schema
```

### `validate()`

Verifica almeno un destinatario e privacy valida.

### `to_json()`

Serializza in JSON leggibile, ordinato.

### `load()`

Legge `vault.json`, verifica schema, applica default e valida.

---

## 35. `AppSettings` (`config.toml`)

Questa dataclass rappresenta preferenze locali.

### `_string_list()`

Valida campi TOML che devono essere liste di stringhe, soprattutto opzioni launcher.

### `_toml_string()` e `_toml_array()`

Sono piccoli serializer usati da `save()`. Servono perché la standard library Python dispone di `tomllib` per leggere TOML ma non di un writer TOML equivalente.

### `default_path()`

Usa `platformdirs.user_config_dir()` per ottenere una posizione nativa per OS.

### `load()`

Legge TOML e separa le sezioni:

```text
clipboard
security
ui
launchers.ssh
launchers.rdp.linux
launchers.rdp.windows
launchers.rdp.macos
```

Valida `tree_startup_view` e le liste argv.

### `save()`

Scrive il TOML completo e, su Unix, applica `0600`.

---

# Parte VII — TOTP e password

## 36. `services/totp.py`

### `_decode_base32(secret)`

Rimuove spazi, converte in uppercase, aggiunge padding `=` necessario e chiama `base64.b32decode()`.

### `totp_from_secret()`

È la funzione consigliata quando l'utente inserisce direttamente una chiave TOTP.

Fa:

1. normalizzazione;
2. verifica decodifica Base32;
3. costruzione `TotpConfig`;
4. `validate()`.

### `generate_totp(config, at_time=None)`

Implementa l'algoritmo TOTP.

Passaggi:

```text
now
 ↓
counter = now // period
 ↓
HMAC(secret, counter a 8 byte big-endian)
 ↓
dynamic truncation
 ↓
mod 10^digits
 ↓
zero padding
```

Restituisce:

```python
(code, remaining_seconds)
```

Questo secondo valore permette alla GUI di mostrare `123456 (17s)`.

### `parse_otpauth_uri()`

Legge URI del tipo:

```text
otpauth://totp/Issuer:account?secret=...&digits=6&period=30
```

Accetta soltanto `totp`, non HOTP.

### `build_otpauth_uri()`

Fa l'inverso: da `TotpConfig` costruisce URI interoperabile.

---

## 37. `services/passwords.py`

`generate_password()` usa il modulo `secrets`, non `random`.

Flusso:

1. valida lunghezza minima;
2. crea classi abilitate;
3. opzionalmente rimuove caratteri ambigui;
4. garantisce almeno un carattere per ogni classe;
5. riempie i caratteri restanti;
6. esegue shuffle Fisher-Yates usando `secrets.randbelow()`.

Quindi non c'è il classico problema per cui una password generata casualmente potrebbe non contenere una delle classi richieste.

---

# Parte VIII — Clipboard

## 38. Perché esistono due percorsi clipboard

La GUI ha già un event loop Qt, quindi può gestire timer e ownership direttamente.

CLI/TUI invece possono terminare o non avere Qt. Per questo usano un **helper separato**.

---

## 39. `copy_secret_qt()`

Usato dalla GUI.

Crea un `QMimeData` con:

- testo segreto;
- token casuale MIME `application/x-keys-ng-token`;
- hint KDE password manager.

Poi avvia un `QTimer.singleShot()`.

Alla scadenza cancella la clipboard **solo se il token è ancora quello di Keys NG**.

Questa logica evita il bug:

```text
copio password
copio poi una frase personale
scade timer Keys NG
→ NON deve cancellare la frase personale
```

---

## 40. Backend clipboard nativi

### `available_native_clipboard_backend()`

Ordine indicativo:

- macOS: `pbcopy/pbpaste`;
- Windows: PowerShell;
- Wayland: `wl-copy/wl-paste`;
- X11: `xclip`;
- X11: `xsel`;
- fallback Wayland.

### `set_native_clipboard()`

Passa il segreto via **stdin**, non in argv e non in environment.

### `read_native_clipboard()`

Rilegge il clipboard per verificare che il valore sia stato realmente impostato.

### `clear_native_clipboard()`

Usa il comando specifico della piattaforma/backend.

### `_run_clipboard_command()`

Wrapper subprocess con timeout e `shell=False`.

---

## 41. `copy_secret_cli()` e `clipboard_helper.py`

`copy_secret_cli()` avvia:

```text
python -m keys_ng.services.clipboard_helper <timeout>
```

Il segreto viene scritto sullo stdin del processo helper.

Il parent aspetta un messaggio `READY` con timeout. In questo modo CLI/TUI non dichiarano “copiato” se il backend non è partito.

L'helper:

1. legge il segreto da stdin;
2. prova backend nativo;
3. verifica read-back;
4. stampa `READY`;
5. attende TTL;
6. ricontrolla il clipboard;
7. lo cancella solo se contiene ancora quel valore.

Se i backend nativi non esistono, prova Qt. Nella TUI esiste inoltre un fallback Textual/terminal clipboard, ma con garanzie di cancellazione inferiori.

---

# Parte IX — Apertura URL, SSH, RDP e comandi

## 42. `services/actions.py`

È il solo modulo che dovrebbe trasformare `Action` in processi esterni.

### `_resolve_executable(name)`

Se il nome è un path, controlla file eseguibile. Altrimenti usa `shutil.which()`.

### `_ssh_terminal(settings)`

Decide quale terminale usare.

Se `ssh_terminal != "auto"`, usa quello configurato e relative opzioni.

In auto prova:

```text
xdg-terminal
xdg-terminal-exec
gnome-terminal
kgx
ptyxis
konsole
xterm
alacritty
```

Restituisce:

```python
(executable, terminal_options)
```

### `_launch_ssh(action, settings)`

Costruisce argv in ordine:

```text
ssh
[-X|-Y]
[advanced options]
[-p port]
[user@]host
```

Poi:

- Windows: avvia direttamente `ssh` nella console corrente;
- Unix-like: avvia il terminale configurato e gli passa l'argv SSH.

La password non compare mai nella command line.

### `_linux_rdp()`

Sceglie `xfreerdp3` o `xfreerdp` oppure client configurato.

Costruisce:

```text
client + global options + /v:host[:port] + /u:username
```

### `_windows_rdp()`

Usa tipicamente `mstsc` e `/v:`.

### `_macos_rdp()`

Costruisce un URI `rdp://...` e lo apre con `open` o launcher configurato.

### `launch_action(action, settings=None)`

Dispatcher pubblico:

```text
url     → webbrowser.open
ssh     → _launch_ssh
rdp     → OS-specific function
command → subprocess.Popen(action.argv)
```

Prima chiama sempre `action.validate()`.

---

## 43. `services/ssh_options.py`

Questo modulo permette libertà all'utente senza trasformare le opzioni in una stringa shell.

### `parse_ssh_options(text)`

Usa `shlex.split()` per trasformare:

```text
-J bastion -o ServerAliveInterval=30
```

in:

```python
["-J", "bastion", "-o", "ServerAliveInterval=30"]
```

Poi valida.

### `validate_ssh_options(argv)`

Rifiuta opzioni che devono essere controllate dai campi dedicati:

- `-X`, `-Y`, `-x`;
- `-p`;
- `-l`;
- `-o Port=...`;
- `-o User=...`;
- `--`.

Permette invece opzioni come:

```text
-J
-L
-R
-D
-i
-o ServerAliveInterval=...
```

Nota di sicurezza: `ProxyCommand` e `LocalCommand` sono opzioni OpenSSH capaci di avviare comandi. `shell=False` protegge Keys NG dal parsing shell, ma non impedisce a **ssh stesso** di eseguire comportamenti esplicitamente richiesti da quelle opzioni.

### `format_ssh_options(argv)`

Usa `shlex.join()` per mostrare una rappresentazione editabile del vettore argv salvato.

---

# Parte X — GUI

## 44. Perché le classi GUI sono dentro `main()`

`gui/main.py` importa PySide6 **solo dentro `main()`**. Questo evita che importare moduli comuni di Keys NG richieda automaticamente la dipendenza GUI.

Le classi `VaultTree`, `EntryDialog`, `HelpDialog` e `Window` sono quindi locali a `main()`.

È una scelta funzionale, anche se in futuro, crescendo la GUI, sarebbe ragionevole spostarle in file separati.

---

## 45. Startup GUI

Workflow:

```text
parse argv
 ↓
AppSettings.load()
 ↓
configure_language()
 ↓
create_crypto_backend()
 ↓
Vault(...)
 ↓
ensure_user_desktop_integration()
 ↓
configure_process_identity()
 ↓
QApplication
 ↓
apply_qt_identity()
 ↓
Window()
 ↓
app.exec()
```

`tree_startup_view` viene scelto da CLI `--tree-view` oppure `config.toml`.

---

## 46. `VaultTree`

Sottoclasse di `QTreeWidget` che aggiunge drag & drop semantico.

### `__init__()`

Abilita:

- drag;
- drop;
- indicatori;
- move action.

Riceve callback `on_move`, tipicamente `Window.tree_move`.

### `dropEvent()`

Capisce:

- cosa stai trascinando (`folder` o `entry`);
- su quale nodo stai rilasciando;
- quale deve essere il nuovo parent folder.

Poi chiama:

```python
on_move(item_type, item_id, parent_id)
```

Quindi ricarica la finestra.

---

## 47. `EntryDialog`

È il form “Nuova voce / Modifica voce”.

### `__init__()`

Costruisce i widget e, se esiste una Entry, li precompila.

Gestisce tipi:

```text
generic
url
ssh
rdp
```

Per SSH include:

- host;
- porta;
- X11 forwarding;
- advanced SSH options.

Per TOTP include:

- URI otpauth;
- secret manuale;
- import QR file;
- import QR clipboard.

Carica anche l'elenco folder dal vault.

### `update_action_fields()`

Mostra/nasconde i campi a seconda del tipo selezionato.

Questa è la funzione da modificare se aggiungi un nuovo tipo di entry nella GUI.

### `import_qr()`

Apre file dialog, legge QR, converte il token in URI e precompila secret.

### `import_qr_clipboard()`

Stesso concetto ma prende una `QImage` dal clipboard.

### `build_entry()`

È il metodo più importante del dialog.

Legge i widget e costruisce il modello `Entry`.

Parti principali:

1. titolo, username, password, tag;
2. preservazione di eventuali azioni `command` importate;
3. costruzione azione primaria URL/SSH/RDP;
4. parsing opzioni SSH;
5. costruzione TOTP da URI o secret;
6. cartella;
7. `kind` coerente;
8. se modifica: aggiorna oggetto, incrementa revision;
9. se nuovo: `Entry.create()`.

Il dialog **non cifra** nulla. Restituisce un oggetto, e sarà `vault.save_entry()` a cifrarlo.

---

## 48. `HelpDialog`

Mostra tre tab:

```text
Help
Security
License
```

Usa `current_language()` per cercare prima:

```text
keys_ng/help/<lingua>/...
```

poi fa fallback su `en`.

`QTextBrowser.setMarkdown()` renderizza i Markdown incorporati.

---

## 49. `Window`: stato principale

Campi di stato:

```text
current_id
current_entry
current_folder_id
```

Sono volutamente distinti: la selezione può essere una cartella oppure un'entry.

### `__init__()`

Costruisce:

- search box;
- tree;
- pannello dettagli;
- pulsanti;
- menu;
- shortcut;
- timer TOTP;
- timer auto-lock.

La ricerca usa un debounce di 75 ms: ogni carattere non ricostruisce immediatamente tutto l'albero.

---

## 50. Menu e shortcut GUI

### `_menu_action()`

Helper per creare una QAction testuale e collegarla a callback.

### `build_menus()`

Costruisce:

```text
Vault
Entry
Folder
?
```

Gli shortcut veri vengono creati tramite `QShortcut` nel costruttore; il testo del menu li mostra per leggibilità.

### `focus_search()`

Focus e select-all sulla search box, poi reset auto-lock.

### `schedule_search()`

Riavvia il timer debounce.

### `activity()`

Riavvia il timer di auto-lock se il vault è sbloccato.

Ogni azione utente significativa dovrebbe chiamarla.

---

## 51. Icone GUI

### `_theme_icon(names, fallback)`

Prova più nomi dal tema desktop. Se nessuno esiste usa `QStyle` standard.

### `_folder_icon()`

Icona folder.

### `_entry_icon(catalog_item)`

Decide l'icona dalle capabilities:

```text
action:ssh → terminal/server
action:rdp → remote desktop/computer
action:url → browser/network
action:command → terminal
altro → icona generica
```

Il vantaggio è che non deve decifrare l'entry per sapere l'icona.

---

## 52. Costruzione albero e ricerca GUI

### `_folder_item()`

Crea `QTreeWidgetItem`, associa tipo e UUID tramite ruoli Qt custom.

### `_entry_item()`

Crea nodo entry con icona e ID.

### `reload()`

È la funzione centrale di rendering.

Caso ricerca:

```text
vault.search(query)
 ↓
risultati piatti
 ↓
"titolo — percorso"
```

Caso normale:

```text
vault.list_folders()
 ↓
ricostruisce gerarchia
 ↓
vault.list_items()
 ↓
aggancia entry al parent
 ↓
expandAll o collapseAll
```

Durante una ricerca il drag & drop viene disabilitato, perché l'albero visualizzato non rappresenta la gerarchia reale.

---

## 53. Selezione, lock e dettaglio GUI

### `select_item()`

Se è folder:

- imposta `current_folder_id`;
- mostra nome/percorso;
- pulisce dettagli entry.

Se è entry:

- `vault.get_entry()`;
- quindi viene decifrato **solo quel record**;
- mostra titolo, folder, username, note;
- aggiorna TOTP.

### `clear_details()`

Azzera selezione e widget.

### `tree_move()`

Dispatcher drag&drop:

```text
folder → vault.move_folder
entry  → vault.move_entry
```

### `lock(hard)`

Chiama vault lock, cancella clipboard Qt, pulisce UI.

### `unlock()`

Chiama `vault.unlock()`, ricarica e riattiva timer.

### `refresh_otp()`

Ogni secondo ricalcola il primo token TOTP della entry corrente.

---

## 54. Operazioni GUI su entry

### `copy_url_clicked()`

Trova la prima action URL e usa `copy_secret_qt()`.

### `copy_username_clicked()`

Copia il primo username.

### `copy_password_clicked()`

Copia password.

### `copy_otp_clicked()`

Genera il TOTP corrente e lo copia.

### `open_action_clicked()`

Prende la prima azione e chiama `launch_action()`.

### `new_entry()`

Apre `EntryDialog`, poi:

```text
build_entry → vault.save_entry → reload
```

### `edit_entry()`

Stesso flusso usando `current_entry`.

### `delete_entry()`

Chiede conferma, `vault.delete_entry()`, pulisce e ricarica.

---

## 55. Operazioni GUI su folder

### `new_folder()`

Chiede nome, crea sotto `current_folder_id` se è selezionata una cartella.

### `rename_folder()`

Carica folder, chiede nuovo nome, `vault.rename_folder()`.

### `delete_folder()`

Conferma e prova `vault.delete_folder()`. Il core impedirà l'eliminazione se non è vuota.

---

# Parte XI — TUI

## 56. Startup TUI

Come la GUI:

```text
argparse
AppSettings
gettext
CryptoBackend
Vault
Textual App
```

Non importa PySide6.

---

## 57. `KeysApp`

### `BINDINGS`

Definisce:

```text
Ctrl+Q quit
Ctrl+F search
Ctrl+U URL
Ctrl+B username
Ctrl+C password
Ctrl+T TOTP
Ctrl+O open
L lock
R reload
```

I binding di copia sono `priority=True` perché un `Input` terminale può altrimenti intercettare alcune combinazioni.

### `__init__()`

Tiene `current_entry`.

### `compose()`

Definisce layout dichiarativo:

```text
Header
Search Input
Horizontal:
    Tree
    Detail + Status
Footer
```

### `on_mount()`

Imposta titolo terminale, costruisce tree e mette focus sull'albero.

---

## 58. Ricerca e albero TUI

### `rebuild_tree(query="")`

Con query:

- usa `vault.search()`;
- mostra risultati piatti con path;
- espande root.

Senza query:

- costruisce folder nodes;
- aggiunge entry;
- applica `tree_startup_view`.

### `on_input_changed()`

Ad ogni modifica dell'Input richiama `rebuild_tree()`.

A differenza GUI non c'è debounce; la ricerca core è però in RAM e molto veloce.

### `on_tree_node_selected()`

Solo per entry:

- carica e decifra record;
- mostra folder, username, presenza password/TOTP, azioni, note.

---

## 59. Azioni TUI

### `_status()`

Aggiorna widget status.

### `action_focus_search()`

Focus search.

### `action_reload_tree()`

Ricostruisce mantenendo query corrente.

### `_copy(value, timeout, success)`

Primo tentativo: `copy_secret_cli()` con helper verificato.

Se fallisce, usa `self.copy_to_clipboard()` di Textual come fallback terminale. In quel caso avvisa che la cancellazione automatica non è verificabile.

### `action_copy_*`

Leggono il valore da `current_entry` e delegano a `_copy()`.

### `action_open_action()`

Chiama `launch_action()` sulla prima azione.

### `action_lock_vault()`

Blocca il vault e informa che attualmente la TUI va riavviata per riaprirlo.

Questa è una differenza rispetto alla GUI e un possibile punto di miglioramento futuro.

---

# Parte XII — CLI

## 60. Struttura di `cli/main.py`

La CLI è pensata per essere:

- scriptabile;
- utile per manutenzione;
- frontend completo senza GUI.

Funzioni helper iniziali:

### `_settings()`

Carica `AppSettings`.

### `_crypto()`

Crea il backend usando `settings.crypto_backend`.

### `_vault(path)`

Crea `Vault(path, _crypto())`.

### `_print_items(items)`

Stampa righe catalogo in formato leggibile.

---

## 61. `build_parser()`

Costruisce l'intero albero `argparse` con subcommand.

È il posto da modificare quando aggiungi una nuova opzione CLI.

La struttura generale segue il modello:

```python
sub = parser.add_subparsers(...)
cmd = sub.add_parser("nome")
cmd.add_argument(...)
```

Tra i comandi presenti nelle milestone correnti ci sono init, list/search, CRUD, TOTP/password, folder, move, reindex, health, import, desktop integration e diagnostica.

---

## 62. `run(args)`

È il grande dispatcher CLI.

Pattern concettuale:

```python
if args.command == "init":
    ...
elif args.command == "search":
    ...
elif ...:
    ...
```

Ogni ramo dovrebbe restare sottile e delegare al core.

Esempio corretto:

```text
CLI interpreta argomenti
    ↓
Vault/Service fa il lavoro vero
    ↓
CLI formatta output
```

Non sarebbe invece ideale inserire logica crittografica o filesystem direttamente nel ramo CLI.

### `main()`

Costruisce parser, configura lingua dove necessario, esegue `run()` e trasforma il risultato in exit code.

---

# Parte XIII — Internazionalizzazione

## 63. `i18n/manager.py`

### `_locales_dir()`

Cerca prima cataloghi `.mo` incorporati nel package. In sviluppo può trovare la directory `locales/` del repository.

### `_language_code()`

Riduce valori come:

```text
it_IT → it
en-US → en
```

### `configure_language(language)`

Se è indicata una lingua esplicita, la usa. Con `auto`, usa locale del sistema.

Carica il dominio gettext `keys-ng` con fallback.

### `current_language()`

Restituisce il codice corrente, usato anche per i Markdown help.

### `_()`, `ngettext()`, `pgettext()`

Wrapper standard gettext.

Regola pratica: ogni stringa visibile all'utente dovrebbe passare da uno di questi wrapper, mentre nomi JSON, enum, opzioni CLI stabili e chiavi config non vanno tradotti.

---

# Parte XIV — QR

## 64. `services/qr.py`

### `QRUnavailable`

Eccezione specifica quando manca una dipendenza opzionale.

### `_decode_image(image)`

Usa `zxingcpp.read_barcode()` limitato a QRCode.

Accetta soltanto contenuti che iniziano con:

```text
otpauth://totp/
```

Poi delega a `parse_otpauth_uri()`.

### `parse_totp_qr_file(path)`

Usa Pillow per aprire immagine e convertirla RGB.

### `parse_totp_qimage(image)`

Permette alla GUI di passare direttamente una `QImage`.

---

# Parte XV — Migrazioni

## 65. Parser legacy Keys

Il principio più importante è:

> **il nuovo migratore non esegue mai il vecchio record Bash con `source`.**

### `_unescape_single_quoted_legacy()`

Accetta solo escape limitati di backslash e apostrofo.

Non espande `$VAR`, backtick o command substitution.

### `parse_legacy_record(text)`

Accetta solo righe del tipo:

```text
target='...'
user='...'
password='...'
note='...'
comando='...'
```

Qualsiasi altra sintassi viene rifiutata.

Questo trasforma un vecchio “script Bash” in un formato dati ristretto.

---

## 66. `migration/migrator.py`

### `_legacy_kind(path)`

Deduce tipo dal suffisso:

```text
_sites   → website
_cmd     → command
_account → account
```

### `migrate_legacy_tree()`

Per ogni file:

1. decifra con il backend;
2. parser sicuro;
3. converte directory legacy in cartelle logiche;
4. crea action URL o command;
5. costruisce Entry;
6. salva nel nuovo vault;
7. opzionalmente rileggere e confrontare (`verify`).

Gli errori sono per-file, quindi una voce corrotta non interrompe l'intera migrazione.

---

## 67. Import KeePassXC

`migration/keepassxc.py` ha due percorsi:

```text
KDBX → keepassxc-cli → XML su pipe → parser Keys NG
```

oppure:

```text
XML già esportato → parser Keys NG
```

### `KeePassXCImportReport`

Accumula contatori/risultati di import.

### `_safe_xml_root(raw)`

Rifiuta costrutti XML pericolosi come DOCTYPE/entity prima di fare parsing.

### `_text()`

Helper per leggere testo XML con default.

### `_strings()`

Trasforma le coppie KeePass `<String><Key>..` in un dizionario Python.

### `_normalize_totp_algorithm()`

Normalizza algoritmo TOTP.

### `_parse_totp()`

Riconosce campi TOTP KeePassXC/interoperabili e costruisce `TotpConfig`.

### `_action_from_url()`

Converte URL KeePass in azione Keys NG:

- http/https → URL;
- ssh → SSH strutturata;
- rdp → RDP strutturata;
- schemi sconosciuti conservati senza esecuzione automatica dove previsto.

### `_parse_tags()`

Converte i tag XML in lista.

### `_entry_from_xml()`

È la funzione che traduce una entry KeePass in `Entry` Keys NG, includendo custom fields.

### `import_keepassxc_xml()`

Importa la gerarchia gruppi/entry ricorsivamente. I gruppi diventano folder Keys NG.

### `export_kdbx_to_xml()`

Avvia `keepassxc-cli` e riceve XML su stdout, evitando un file XML plaintext temporaneo.

### `import_keepassxc()`

Dispatcher alto livello: decide se input è KDBX o XML e collega export+parser.

---

# Parte XVI — Identità applicazione e desktop

## 68. `platform/app_identity.py`

Costanti:

```text
APP_NAME = Keys NG
APP_ID = org.keysng.KeysNG
```

### `icon_bytes()`

Legge dal package l'icona legacy.

### `configure_process_identity()`

Su Windows imposta AppUserModelID, best-effort.

### `apply_qt_identity(app)`

Imposta nome, display name, organization, desktop file name e icona Qt.

### `set_textual_terminal_title(app)`

Per la TUI può impostare il titolo, ma non controllare in modo portabile l'icona grafica del terminal emulator.

---

## 69. `platform/desktop_integration.py`

### `_xdg_data_home()`

Rispetta `XDG_DATA_HOME`, fallback `~/.local/share`.

### `user_paths()`

Calcola:

```text
applications/org.keysng.KeysNG.desktop
icons/hicolor/64x64/apps/org.keysng.KeysNG.png
```

### `_resource_bytes()`

Legge asset incorporati.

### `install_user_desktop_integration()`

Installa file per utente su Linux senza sudo.

### `ensure_user_desktop_integration()`

Versione best-effort usata dalla GUI. Confronta anche il contenuto e aggiorna se necessario.

### `uninstall_user_desktop_integration()`

Rimuove i due file.

### `desktop_integration_status()`

Dice se entrambi esistono.

---

# Parte XVII — Eccezioni

## 70. `errors.py`

Gerarchia:

```text
KeysNGError
├── CryptoError
│   └── SignatureError
├── VaultError
└── LegacyFormatError
```

Avere eccezioni specifiche permette ai frontend di mostrare un errore all'utente senza dover interpretare stringhe generiche.

---

# Parte XVIII — Workflow completi

## 71. Avvio GUI e prima ricerca

```text
keys-ng-gui VAULT
       │
       ▼
AppSettings.load()
       │
       ▼
configure_language()
       │
       ▼
create_crypto_backend()
       │
       ▼
Vault.__init__()
       │
       ├── VaultConfig.load()
       └── recover temp ciphertext
       │
       ▼
Window.reload()
       │
       ├── load_folders() → decrypt folders.gpg una volta
       └── load_catalog() → decrypt catalog.gpg una volta
       │
       ▼
cache RAM
       │
       ▼
utente digita nella ricerca
       │
       ▼
Vault.search()
       │
       └── lavora sul Catalog già in memoria
```

---

## 72. Apertura di una entry

```text
utente seleziona voce
      │
      ▼
Window.select_item()
      │
      ▼
Vault.get_entry(uuid)
      │
      ▼
read records/uuid.gpg
      │
      ▼
crypto.decrypt()
      │
      ▼
Vault._verify(signature)
      │
      ▼
Entry.from_bytes()
      │
      ▼
GUI mostra dettaglio
```

Solo la voce selezionata viene decifrata.

---

## 73. Salvataggio di una nuova voce SSH

```text
EntryDialog
  │
  ├── host/port/user
  ├── X11 selector
  └── advanced options string
          │
          ▼
parse_ssh_options()
          │
          ▼
Action(type="ssh", ...)
          │
          ▼
Entry.create()
          │
          ▼
Vault.save_entry()
          │
          ├── validate
          ├── encrypt/sign JSON
          ├── atomic records/<uuid>.gpg
          └── update catalog.gpg
```

---

## 74. Ctrl+O su una SSH entry

```text
Ctrl+O
  ↓
Window.open_action_clicked()
  ↓
launch_action(Action ssh)
  ↓
Action.validate()
  ↓
_launch_ssh()
  ↓
ssh argv
  ↓
_ssh_terminal()
  ↓
terminal argv + ssh argv
  ↓
subprocess.Popen(shell=False)
```

---

## 75. Generazione TOTP

```text
Entry.totp[0]
   │
   ▼
generate_totp()
   │
   ├── Base32 decode
   ├── counter temporale
   ├── HMAC
   └── truncation
   │
   ▼
("123456", 17)
```

Nessun codice TOTP corrente viene salvato nel vault.

---

## 76. Ctrl+C password GUI

```text
current_entry.password
       │
       ▼
copy_secret_qt(secret, ttl)
       │
       ├── clipboard text
       ├── token ownership
       └── timer
               │
               ▼
       clear solo se ancora owned
```

---

## 77. Lock normale vs hard lock

### Lock normale

```text
Vault.lock(False)
  ↓
blocca API
  ↓
cancella catalog/folder cache RAM
```

La cache di gpg-agent può rimanere.

### Hard lock

```text
Vault.lock(True)
  ↓
come sopra
  ↓
crypto.hard_lock()
  ↓
gpgconf --kill gpg-agent
```

Alla prossima operazione privata, GnuPG dovrà normalmente chiedere di nuovo la passphrase/token authorization.

---

# Parte XIX — Dove modificare cosa

## 78. Voglio aggiungere un nuovo campo a una Entry

Esempio: `email_recovery`.

Ordine consigliato:

```text
1. models.Entry
2. Entry.from_bytes() per default compatibilità
3. EntryDialog GUI
4. CLI parser/dispatcher se necessario
5. TUI dettaglio se necessario
6. importer legacy/KeePassXC se applicabile
7. test round-trip JSON
8. test vault save/get
```

Se il campo deve essere ricercabile senza aprire il record, devi anche decidere se inserirlo in `CatalogItem` e `_catalog_item()`.

---

## 79. Voglio aggiungere una nuova azione, ad esempio VNC

Modifica almeno:

```text
models.Action.validate()
services/actions.py → launcher
GUI EntryDialog → tipo e campi
GUI _entry_icon()
CLI argomenti
Catalog capabilities (automaticamente action:vnc se action valida)
importer, se necessario
```

Probabilmente dovrai anche aggiornare schema/compatibilità se aggiungi campi nuovi ad `Action` senza default.

---

## 80. Voglio cambiare il comportamento della ricerca

Punto centrale:

```text
Vault.search()
```

Ma chiediti prima: **il dato che voglio cercare è nel catalogo?**

Se vuoi cercare nelle note, hai tre possibilità:

1. aggiungere note al catalogo → ricerca veloce, più plaintext metadata in RAM;
2. decifrare tutte le entry ad ogni ricerca → sconsigliato;
3. mantenere un indice cifrato separato più ricco → architettura più complessa.

---

## 81. Voglio aggiungere un'opzione al `config.toml`

Modifica:

```text
AppSettings dataclass
AppSettings.load()
AppSettings.save()
config.example.toml
README / help
```

Poi usa il valore nel servizio interessato.

Evita di leggere direttamente TOML da GUI/TUI/CLI: passa sempre da `AppSettings`.

---

## 82. Voglio aggiungere un nuovo shortcut GUI

Nel `Window.__init__()` aggiungi alla tupla:

```python
("Ctrl+X", self.some_callback)
```

Poi, se deve apparire nel menu, aggiungi la stessa azione in `build_menus()`.

La callback dovrebbe chiamare `activity()` se rappresenta attività utente, per evitare auto-lock durante uso reale.

---

## 83. Voglio aggiungere un nuovo shortcut TUI

Aggiungi un `Binding` a `KeysApp.BINDINGS` e implementa:

```python
def action_nomeazione(self):
    ...
```

Se lo shortcut può essere intercettato da `Input`, considera `priority=True`.

---

## 84. Voglio cambiare la crittografia

Non partire da GUI o `Vault.save_entry()`.

Il confine corretto è:

```text
CryptoBackend
```

Implementa un nuovo backend che rispetti:

```python
encrypt() -> bytes
decrypt() -> DecryptionResult
```

poi registralo in `crypto/factory.py`.

Il resto del programma dovrebbe rimanere invariato.

---

## 85. Voglio introdurre schema versione 2

Questo richiede disciplina.

Approccio consigliato:

1. aumenta `SCHEMA_VERSION` solo quando hai definito una migrazione;
2. `Entry.from_bytes()` deve sapere leggere v1 e trasformarla in memoria verso il modello nuovo;
3. stesso discorso per `Catalog` e `FolderStore` se cambiano;
4. aggiungi test con fixture v1 reali;
5. non aggiornare automaticamente tutti i ciphertext senza backup e procedura esplicita.

---

# Parte XX — Punti delicati di sicurezza

## 86. Dove esiste plaintext in memoria

Anche senza file temporanei, il plaintext esiste temporaneamente come:

- `bytes` restituiti da GnuPG;
- stringhe Python in `Entry`;
- password/secret nei widget GUI;
- clipboard;
- XML KeePassXC durante import;
- output interno dei parser.

Python non permette di garantire una cancellazione sicura di tutte le copie in RAM. Il modello di sicurezza attuale punta soprattutto a:

- evitare plaintext persistente su filesystem;
- minimizzare durata e copie;
- non passare segreti in argv/env;
- svuotare cache metadati al lock;
- lasciare la passphrase privata a GnuPG/gpg-agent.

---

## 87. Funzioni private chiamate da altri moduli

`storage/inbox.py` usa `vault._decrypt()` anche se il prefisso `_` indica API interna.

È una scelta deliberata per riutilizzare la verifica firma. In una futura pulizia architetturale potresti esporre un metodo pubblico come:

```python
def decrypt_verified_object(...)
```

ed evitare l'accesso a metodi privati.

---

## 88. `trust-model always`

Il backend GnuPG usa `--trust-model always` per cifrare verso fingerprint esplicitamente configurati. Questo evita che il modello Web-of-Trust interattivo impedisca operazioni programmatiche.

La sicurezza del destinatario dipende quindi dal fatto che `vault.json` contenga i fingerprint corretti.

---

## 89. Catalogo e leakage in RAM

Il catalogo è cifrato su disco, ma quando il vault è aperto è una struttura Python in RAM.

Il parametro `catalog_privacy` controlla cosa viene inserito nel catalogo:

```text
minimal  → meno metadati
standard → compromesso
full     → ricerca più ricca
```

Se vuoi rafforzare ulteriormente il threat model contro memory inspection, `minimal` è preferibile, con il prezzo di una ricerca meno completa.

---

## 90. Launcher avanzati SSH

Le opzioni sono parse senza shell, ma alcune opzioni di OpenSSH hanno semantica propria di esecuzione comandi.

Per esempio:

```text
-o ProxyCommand=...
-o LocalCommand=...
```

Il codice del record è cifrato e firmato, quindi l'utente sta di fatto autorizzando quelle opzioni. Durante un audit è importante considerarle come **contenuto eseguibile/attivo**, non semplice dato.

---

# Parte XXI — Test e metodo di sviluppo

## 91. Perché i test sono parte dell'architettura

Keys NG ha diversi confini che possono essere testati senza GnuPG reale:

```text
Entry JSON round-trip
Vault con fake crypto
folder hierarchy
search cache
TOTP vectors
SSH argv
clipboard subprocess construction
legacy parser
KeePassXC parser
```

Questo permette di cambiare il codice mantenendo il comportamento osservabile.

Quando modifichi una funzione, cerca prima un test relativo. Se non esiste, aggiungilo **prima o insieme alla modifica**.

---

## 92. Test che richiedono integrazione reale

Alcuni aspetti richiedono test manuali o integration test su OS reali:

- pinentry/gpg-agent;
- clipboard Wayland/X11/Windows/macOS;
- GNOME taskbar icon;
- terminal launcher;
- RDP client;
- QR clipboard GUI;
- drag & drop Qt;
- packaging/installazione.

Il fatto che un test unitario passi non garantisce che un desktop environment si comporti allo stesso modo.

---

# Parte XXII — Ordine di lettura consigliato del sorgente

## 93. Percorso didattico

Per padroneggiare il progetto, suggerisco questo ordine:

```text
1. models.py
2. storage/config.py
3. crypto/backend.py
4. crypto/gpg_process.py
5. storage/atomic.py
6. storage/vault.py
7. services/totp.py
8. services/actions.py
9. services/clipboard.py + clipboard_helper.py
10. gui/main.py
11. tui/main.py
12. cli/main.py
13. migration/*
14. platform/*
15. tests/*
```

Non partire dalla GUI: è il file più lungo e mescola molti concetti di Qt. Se prima conosci `Vault`, `Entry` e `Action`, il codice GUI diventa molto più leggibile.

---

# Parte XXIII — Mappa rapida “chi chiama chi”

## 94. Dipendenze principali

```text
GUI ───────┐
TUI ───────┼──► Vault ───► CryptoBackend ───► GnuPG
CLI ───────┘      │
                  ├──► Entry / Catalog / Folder
                  └──► atomic_write_ciphertext

GUI/TUI/CLI ───► services.actions ───► subprocess/webbrowser
GUI/TUI/CLI ───► services.totp
GUI/TUI/CLI ───► services.clipboard

Migration ───► Entry/Action ───► Vault
```

Una dipendenza che **non** dovresti introdurre è:

```text
Vault → GUI
```

Il core deve restare indipendente dai frontend.

---

# Parte XXIV — Checklist mentale prima di una modifica

## 95. Cinque domande

Prima di cambiare il codice, chiediti:

1. **Sto cambiando il modello dati o solo la presentazione?**  
   Se cambia il modello, parti da `models.py`.

2. **Il comportamento appartiene al core o a un frontend?**  
   Se deve valere per GUI/TUI/CLI, mettilo nel core/service.

3. **Sto introducendo un nuovo punto in cui un segreto passa a un processo?**  
   Evita argv/env; preferisci stdin/file descriptor/API native.

4. **Sto modificando un formato persistente?**  
   Pensa subito a schema e compatibilità.

5. **Quale test dimostra che il comportamento è corretto?**  
   Se non sai rispondere, la modifica non è ancora ben delimitata.

---

# Appendice A — Riferimento sintetico di tutte le funzioni principali

Questa sezione è volutamente compatta: serve come indice quando sai già cosa cerchi.

## `models.py`

- `utc_now()` — timestamp UTC ISO.
- `TotpConfig.validate()` — valida parametri TOTP.
- `Action.validate()` — valida azione e vincoli sicurezza.
- `Folder.create()` — crea folder con UUID.
- `Folder.validate()` — valida singola folder.
- `FolderStore.validate()` — valida gerarchia completa.
- `FolderStore.to_bytes()/from_bytes()` — JSON folder store.
- `Entry.create()` — crea entry con UUID.
- `Entry.validate()` — valida record completo.
- `Entry.to_bytes()/from_bytes()` — JSON entry.
- `Catalog.to_bytes()/from_bytes()` — JSON catalogo.

## `storage/vault.py`

- `Vault.__init__()` — apre struttura/config e prepara cache.
- `Vault.init()` — crea nuovo vault.
- `recover_interrupted_writes()` — elimina temp ciphertext.
- `lock()/unlock()` — stato e cache.
- `_require_unlocked()` — guardia.
- `_verify()` — policy firma.
- `_encrypt()/_decrypt()` — confine crypto.
- `_write_catalog()/_write_folders()` — persistenza cifrata.
- `load_catalog()/load_folders()` — decrypt con cache RAM.
- `_catalog_item()` — riduzione Entry → CatalogItem.
- `_sync_catalog_folders()` — aggiorna snapshot folder.
- `save_entry()` — salva record + catalogo.
- `get_entry()` — decifra record.
- `delete_entry()` — elimina record + indice.
- `list_items()` — listing/filter folder.
- `_folder_paths_from()` — calcolo path gerarchici.
- `folder_paths()` — map UUID→path.
- `search()` — ricerca catalogo.
- `reindex()` — rigenera catalogo.
- `catalog_health()` — coerenza catalogo/filesystem.
- `list_folders()/get_folder()/folder_path()` — lettura folder.
- `resolve_folder_path()` — path→UUID.
- `create_folder()/create_folder_path()` — creazione.
- `rename_folder()/move_folder()/delete_folder()` — CRUD folder.
- `move_entry()` — cambia folder a entry.

## `crypto/backend.py`

- `KeyInfo.label` — etichetta user-friendly.
- `CryptoBackend.encrypt/decrypt/diagnose` — contratto astratto.
- `list_keys()` — default vuoto.
- `resolve_fingerprint()` — match fingerprint.
- `hard_lock()` — hook backend.

## `crypto/gpg_process.py`

- `__init__()` — selezione eseguibile/homedir.
- `_base_args()` — `--homedir`.
- `_run()` — subprocess GPG sicuro.
- `encrypt()` — sign+encrypt.
- `decrypt()` — decrypt + parse VALIDSIG.
- `list_keys()` — parsing `--with-colons`.
- `resolve_fingerprint()` — fingerprint full only.
- `hard_lock()` — kill gpg-agent.
- `diagnose()` — controlli GPG.

## `storage/atomic.py`

- `atomic_write_ciphertext()` — temp ciphertext + fsync + replace.
- `remove_stale_ciphertext_temps()` — recovery.

## `storage/settings.py`

- `_string_list()` — validazione argv TOML.
- `_toml_string()/_toml_array()` — serialization helper.
- `AppSettings.default_path()` — path nativo.
- `load()` — TOML→dataclass.
- `save()` — dataclass→TOML.

## `services/totp.py`

- `_decode_base32()` — decoding secret.
- `totp_from_secret()` — costruzione sicura config.
- `generate_totp()` — algoritmo OTP.
- `parse_otpauth_uri()` — URI→config.
- `build_otpauth_uri()` — config→URI.

## `services/actions.py`

- `_resolve_executable()` — risoluzione sicura executable.
- `_ssh_terminal()` — scelta terminal emulator.
- `_launch_ssh()` — costruzione/avvio SSH.
- `_linux_rdp()` — FreeRDP.
- `_windows_rdp()` — mstsc.
- `_macos_rdp()` — rdp URI/open.
- `launch_action()` — dispatcher pubblico.

## `services/clipboard.py`

- `copy_secret_qt()` — clipboard GUI con token.
- `_run_clipboard_command()` — subprocess clipboard.
- `available_native_clipboard_backend()` — scelta backend.
- `set_native_clipboard()` — scrittura stdin.
- `read_native_clipboard()` — verifica.
- `clear_native_clipboard()` — cancellazione.
- `copy_secret_cli()` — helper detached per CLI/TUI.

## `services/passwords.py`

- `generate_password()` — CSPRNG + classi obbligatorie.

## `services/ssh_options.py`

- `parse_ssh_options()` — stringa utente→argv.
- `validate_ssh_options()` — blocco override campi dedicati.
- `format_ssh_options()` — argv→testo editabile.

## `services/qr.py`

- `_decode_image()` — QR→otpauth.
- `parse_totp_qr_file()` — file immagine.
- `parse_totp_qimage()` — QImage.

## `storage/inbox.py`

- `deposit_entry()` — deposito write-only.
- `import_inbox()` — verifica/import.

## `migration/legacy_parser.py`

- `_unescape_single_quoted_legacy()` — unescape ristretto.
- `parse_legacy_record()` — parser data-only.

## `migration/migrator.py`

- `_legacy_kind()` — tipo da suffisso.
- `migrate_legacy_tree()` — conversione al nuovo vault.

## `migration/keepassxc.py`

- `_safe_xml_root()` — XML hardening.
- `_text()` — XML helper.
- `_strings()` — campi stringa KeePass.
- `_normalize_totp_algorithm()` — algoritmo TOTP.
- `_parse_totp()` — campi OTP.
- `_action_from_url()` — URL→Action.
- `_parse_tags()` — tags.
- `_entry_from_xml()` — XML Entry→Entry Keys NG.
- `import_keepassxc_xml()` — gruppi/record ricorsivi.
- `export_kdbx_to_xml()` — bridge keepassxc-cli.
- `import_keepassxc()` — entry point import.

## `i18n/manager.py`

- `_locales_dir()` — localizza `.mo`.
- `_language_code()` — normalizza locale.
- `configure_language()` — carica gettext.
- `current_language()` — lingua corrente.
- `_()/ngettext()/pgettext()` — traduzione.

## `platform/app_identity.py`

- `icon_bytes()` — asset icona.
- `configure_process_identity()` — identity Windows.
- `apply_qt_identity()` — identity GUI Qt.
- `set_textual_terminal_title()` — titolo TUI.

## `platform/desktop_integration.py`

- `_xdg_data_home()` — XDG path.
- `user_paths()` — file desktop/icon.
- `_resource_bytes()` — asset package.
- `install_user_desktop_integration()` — install per-user.
- `ensure_user_desktop_integration()` — auto repair best-effort.
- `uninstall_user_desktop_integration()` — remove.
- `desktop_integration_status()` — status.

---

# Appendice B — Debito tecnico e miglioramenti architetturali possibili

Il codice attuale è già ben separato per essere un progetto giovane, ma ci sono alcuni miglioramenti che potresti considerare man mano che cresce.

## B.1 Spezzare `gui/main.py`

È il file più grande. Una futura struttura più manutenibile potrebbe essere:

```text
gui/
├── main.py
├── window.py
├── entry_dialog.py
├── help_dialog.py
└── vault_tree.py
```

Nessun cambio funzionale, solo separazione.

## B.2 Spezzare il dispatcher CLI

`run()` crescerà con i comandi. Si può passare a handler separati:

```text
cli/commands/init.py
cli/commands/folder.py
cli/commands/importers.py
```

oppure `argparse.set_defaults(handler=...)`.

## B.3 Rendere pubblica la decrypt verificata

Come accennato, `inbox.py` usa `_decrypt()`. Un'API pubblica ridurrebbe il coupling a dettagli privati.

## B.4 Rendere atomico a livello logico record+catalogo

Attualmente l'atomicità è per singolo file. Un journal cifrato o una strategia “catalog rebuilt on startup if generation mismatch” potrebbe migliorare crash recovery.

## B.5 Separare repository da service

`Vault` oggi gestisce sia dominio sia storage. In un progetto più grande si potrebbe introdurre:

```text
VaultService
RecordRepository
CatalogRepository
FolderRepository
```

Non è indispensabile oggi, ma diventerebbe utile con sync, versioning o storage remoti.

---

# Appendice C — Regola pratica finale

Se devi orientarti rapidamente nel codice, usa questa mappa:

```text
"Che dati esistono?"              → models.py
"Come vengono cifrati?"           → crypto/
"Come vengono salvati/cercati?"   → storage/vault.py
"Come lancio qualcosa?"           → services/actions.py
"Come copio un segreto?"          → services/clipboard.py
"Come calcolo TOTP?"              → services/totp.py
"Come appare in GUI?"             → gui/main.py
"Come appare in terminale?"       → tui/main.py
"Come si invoca da script?"       → cli/main.py
"Come importo dati vecchi?"       → migration/
"Come configuro l'app?"           → storage/settings.py
"Come configuro un vault?"        → storage/config.py
```

Il principio da preservare quando modifichi Keys NG è:

> **i frontend raccolgono input e mostrano output; il core prende le decisioni; i services interagiscono con il sistema operativo; il backend crittografico interagisce con GnuPG.**

Se mantieni questo confine, il progetto rimane comprensibile, testabile e portabile.


---

# Appendice M1.11–M1.15 — Evoluzioni dell'architettura

## A.1 GUI multi-vault

Dalla M1.11 la GUI non possiede più un unico `Vault`. La struttura è:

```text
MainWindow
├── menu e shortcut globali
└── QTabWidget verticale
    ├── VaultPane -> Vault A
    ├── VaultPane -> Vault B
    └── VaultPane -> Vault C
```

`MainWindow` gestisce apertura/chiusura dei vault, recenti, hard-lock globale e dispatch degli shortcut. `VaultPane` possiede invece stato, ricerca, albero, selezione, timer e operazioni del singolo vault. Gli shortcut vengono inoltrati soltanto al tab attivo.

La GUI può partire senza argomenti e aprire i vault attraverso `QFileDialog.getExistingDirectory()`.

## A.2 Riferimenti UUID tra voci

`services/references.py` e i metodi `Vault.resolved_username()`, `Vault.resolved_password()` e `Vault.resolved_action()` implementano:

```text
{REF:U@I:<UUID>}
{REF:P@I:<UUID>}
```

La risoluzione avviene al momento dell'uso e segue catene di riferimenti. Un insieme `visited`/stack impedisce cicli. Il riferimento resta nel record consumatore: non viene sostituito permanentemente dal valore risolto.

## A.3 Import KeePassXC reference-safe

`migration/keepassxc.py` usa una migrazione in due passaggi:

1. legge l'intero XML e raccoglie UUID e struttura;
2. assegna gli UUID di destinazione;
3. conserva gli UUID liberi e rimappa le collisioni;
4. riscrive i riferimenti `REF`;
5. valida dangling reference e cicli;
6. solo dopo scrive cartelle e record cifrati;
7. effettua una validazione finale usando il normale resolver del vault.

Questo evita import apparentemente riusciti con riferimenti che puntano a una voce errata.

## A.4 Inbox con sola chiave pubblica

`keys-ng inbox-create` può usare un file di chiave pubblica senza importarlo nel keyring permanente. `GPGProcessBackend` viene istanziato con un `GNUPGHOME` temporaneo, vi importa la sola chiave pubblica, cifra il JSON della voce e distrugge il keyring temporaneo.

Un ciphertext creato in questo modo non può avere la firma del proprietario del vault. `import-inbox` continua quindi a rifiutare gli unsigned per default; `--accept-unsigned` rappresenta l'approvazione esplicita del proprietario. La voce approvata viene poi ricifrata e firmata secondo la normale configurazione del vault.

## A.5 Menu applicazioni multipiattaforma

`platform/desktop_integration.py` non è più limitato a Linux. La registrazione per utente è:

```text
Linux   -> .desktop XDG + icona hicolor
Windows -> collegamento .lnk nel menu Start
macOS   -> bundle launcher ~/Applications/Keys NG.app
```

`ensure_user_desktop_integration()` è best-effort e non deve mai impedire l'avvio della GUI. I comandi `keys-ng desktop install|status|uninstall` espongono invece gli eventuali errori.

## A.6 Export XML KeePassXC

Il nuovo modulo `migration/keepassxc_export.py` è l'inverso dell'importatore.

### `_keepass_uuid(value)`

Converte l'UUID RFC-4122 di Keys NG nei 16 byte codificati Base64 previsti dagli elementi `<UUID>` del formato XML KeePass.

### `_reference_to_keepass(value)`

Trasforma i riferimenti UUID canonici Keys NG nella forma a 32 cifre esadecimali utilizzata da KeePassXC:

```text
{REF:P@I:033054d4-...}
       ↓
{REF:P@I:033054D445C648C59092CC1D661B1B71}
```

### `_entry_xml(entry, vault, resolve_references=...)`

Costruisce un elemento `<Entry>` con UUID, Title, UserName, Password, URL, Notes, TOTP, tag, custom fields e metadati Keys NG dell'azione.

### `export_entry_xml(vault, entry_id)`

Produce un XML autonomo con una sola voce. Username/password referenziati vengono **risolti**, perché la voce sorgente non è necessariamente inclusa nel file.

### `export_vault_xml(vault)`

Produce l'intero albero di gruppi e voci. Mantiene UUID e riferimenti, consentendo a KeePassXC di ricostruire le credenziali condivise.

### `write_export(path, raw)`

Scrive il file XML in chiaro. Su Unix imposta `0600`. Questo file è un'eccezione intenzionale alla regola "nessun plaintext persistente": è una funzione di export esplicitamente richiesta dall'utente e tutte le interfacce devono avvertire che il file contiene segreti in chiaro.

## A.7 Superfici dell'export

CLI:

```bash
keys-ng export-entry VAULT UUID output.xml
keys-ng export-vault VAULT output.xml
```

TUI: il binding `E` esporta la voce selezionata nella directory corrente.

GUI: `Voce → Esporta come XML KeePassXC…` apre il dialog nativo di salvataggio.

## A.8 Aggiornamento della mappa dei moduli

Alla mappa della guida originale vanno aggiunti:

```text
migration/keepassxc_export.py   export interoperabile KeePassXC
platform/desktop_integration.py integrazione menu applicazioni Linux/Windows/macOS
```

Quando aggiungi un nuovo campo al modello `Entry`, ricorda ora di valutarlo in **entrambi** i sensi dell'interoperabilità: `keepassxc.py` (import) e `keepassxc_export.py` (export).

## A.9 Regole di sicurezza aggiuntive per l'export

Un contributo che modifica l'export deve verificare almeno che:

- il file sia chiaramente documentato come plaintext;
- password e TOTP non finiscano nel nome del file o nei log;
- su Unix il file venga creato con permessi restrittivi;
- l'export singolo non produca riferimenti dangling;
- l'export completo conservi gli UUID necessari ai riferimenti;
- il codice non usi shell per lanciare utility esterne;
- test di round-trip `Keys NG -> XML -> importer Keys NG` continuino a passare.

## Architettura M1.16: distribuzione e preferenze

M1.16 aggiunge tre livelli di distribuzione senza modificare il formato del
vault. Le ricette dei pacchetti nativi sono sotto `packaging/`, mentre
l'applicazione rimane un normale package Python. Windows e macOS usano
Briefcase; Linux usa la base Flathub `io.qt.PySide.BaseApp`, evitando di
ricompilare Qt/PySide nel progetto. Il backend Flatpak è particolare:
`keys_ng.platform.host` rileva il sandbox e antepone
`flatpak-spawn --host` agli argv di GnuPG/SSH/RDP. Non viene introdotta alcuna
shell. Dentro Flatpak l'auto-registrazione del launcher desktop è disabilitata,
perché l'export Flatpak possiede già il desktop ID dell'applicazione.

`keys_ng.services.doctor.collect_doctor_checks()` centralizza la diagnostica a
runtime e distingue intenzionalmente gli errori dei requisiti obbligatori dagli
avvisi relativi alle funzionalità opzionali.

La finestra globale delle preferenze è `keys_ng.gui.main.SettingsDialog`. Essa
modifica l'oggetto `AppSettings` esistente e chiama `AppSettings.save()`: GUI e
modifica manuale del TOML sono quindi due interfacce sullo stesso identico
modello. Le opzioni dei launcher, che sono liste, vengono modificate come un
argomento argv per riga e salvate come array TOML; non viene usato un parser di
riga di comando né una shell.

Gli shortcut GUI appartengono a `MainWindow` e vengono inoltrati soltanto al
`VaultPane` attivo. Nella TUI i binding devono essere compatibili con i terminali: `Ctrl+L` blocca, `Ctrl+P` sblocca e `F9` esegue l'hard lock. Nella GUI `Ctrl+Shift+L` continua a richiamare `MainWindow.hard_lock_all()` perché `gpg-agent` è una risorsa condivisa dalla sessione.

## M1.19 — Procedura di build MSI Windows

La procedura completa Windows/Briefcase, inclusi Git for Windows, metadata licenza PEP 639, packaging GUI/CLI/TUI, test runtime con Gpg4win, pulizia e troubleshooting, è documentata in [`WINDOWS_MSI_BUILD.md`](WINDOWS_MSI_BUILD.md). Il manutentore della release deve seguire quel documento senza ricostruire i comandi dalla sola configurazione CI.

## Logging diagnostico (M1.19.1)

Keys NG dispone di un logging diagnostico rotante e attivabile al bisogno per analizzare GUI, TUI, CLI e prestazioni di GnuPG. È disattivato per impostazione predefinita. Modificare il `config.toml` dell'utente aggiungendo o modificando:

```toml
[diagnostics]
enabled = true
level = "DEBUG"
log_file = ""
max_bytes = 2000000
backup_count = 3
```

Con `log_file` vuoto viene usata la directory log per-utente specifica della piattaforma. `keys-ng doctor` indica se la diagnostica è attiva e quale percorso verrà utilizzato. Dopo una modifica della configurazione occorre riavviare l'applicazione.

Il log registra avvio dei componenti, tipo di operazione GnuPG, metodo di discovery, durata/codice di ritorno/dimensione dei flussi dei sottoprocessi, tempi di lettura/decifratura/parsing/verifica del binding dei record e tempo totale di selezione nella GUI. Intenzionalmente **non** registra password, username, URL, seed/codici TOTP, contenuto degli appunti, corpo decifrato dei record, valori degli argomenti GnuPG, fingerprint, UUID dei record o titoli delle voci.

Il log contiene comunque metadati tecnici come timestamp, processo/thread, versione di piattaforma/Python, tipi di operazione e tempi. Prima di condividerlo pubblicamente va quindi revisionato. Dopo la raccolta della traccia è consigliato disattivare nuovamente la diagnostica, salvo necessità di logging continuativo.

Su Windows M1.19.1 avvia inoltre gli helper GnuPG e `gpgconf` con `CREATE_NO_WINDOW`: in questo modo viene eliminato il lampeggio della finestra console degli eseguibili console, mantenendo disponibile il `pinentry` grafico.

## Modello di autorizzazione Inbox M1.19.2

`GnuPG ownertrust` e `VaultConfig.trusted_signers` sono intenzionalmente indipendenti. GnuPG stabilisce se una firma è crittograficamente valida; Keys NG verifica poi se l'identità primaria di firma è autorizzata a inviare record a quello specifico vault. `services/trusted_signers.py` è l'unico percorso supportato per modificare questa allowlist: valida un fingerprint completo rispetto al keyring pubblico locale, rifiuta chiavi revocate/scadute/non abilitate alla firma, persiste `vault.json` e impedisce la rimozione del signer configurato del vault.

`storage/inbox.py` separa scansione, ispezione e modifica. `pending_inbox_paths()` effettua il solo conteggio dei ciphertext. `inspect_inbox_item()` decifra e classifica senza modificare lo stato del vault. `import_inbox_item()` accetta soltanto una firma valida e autorizzata, salvo approvazione unsigned esplicita; quindi delega la normale persistenza a `Vault.save_entry()`, così cifratura, firma e catalogo di destinazione coincidono con quelli dei record creati localmente. Il file sorgente viene eliminato solo dopo il salvataggio riuscito.

Il backend GnuPG conserva sia il fingerprint della chiave che ha materialmente firmato sia l'eventuale fingerprint della chiave primaria fornito da `VALIDSIG`. L'autorizzazione del vault usa il fingerprint primario quando disponibile, consentendo la rotazione delle signing subkey senza inserirle singolarmente nell'allowlist.

## Regola sul ciclo di vita Textual (M1.19.3)

Le sottoclassi TUI di `Screen`, `ModalScreen` e `Widget` non devono riutilizzare nomi di metodi/API del framework, come `refresh`, per il ricaricamento applicativo dei dati. Textual può invocare `Widget.refresh()` prima che i figli prodotti da `compose()` siano montati. Per il popolamento dell'interfaccia usare nomi espliciti come `refresh_inbox()` o `refresh_signers()`, richiamandoli da `on_mount()` o da gestori di eventi controllati.

## M1.20: contratto di parità interattiva

`keys_ng.services.ui_capabilities` dichiara le funzionalità ordinarie rivolte all'utente che devono essere raggiungibili sia dalla GUI sia dalla TUI. Il test di regressione sulla parità confronta gli insiemi dichiarati e verifica inoltre la presenza dei flussi M1.20 nei sorgenti di entrambi i frontend. I comandi CLI amministrativi/diagnostici sono intenzionalmente esclusi dal contratto.

L'importatore KeePassXC condiviso accetta ora una password opzionale e transitoria per i frontend interattivi. Quando presente, viene codificata esclusivamente per lo stdin di `keepassxc-cli`; non deve mai essere copiata in argv, variabili d'ambiente, log o file XML temporanei. I chiamanti CLI possono continuare a ometterla e lasciare che `keepassxc-cli` gestisca il prompt del terminale. Se `keepassxc-cli` non è nel `PATH`, vengono controllati anche i normali percorsi di installazione KeePassXC su Windows/macOS.

Nella GUI `Ctrl+C` è contestuale: se un `QLineEdit`/`QTextEdit` contiene testo selezionato viene eseguita la normale copia; altrimenti rimane il comportamento storico di copia password. Nella TUI il binding globale della password non è `priority`, così un `TextArea` con focus può gestire nativamente copia/incolla. L'azione esplicita di copia dell'intera nota usa il servizio clipboard temporizzato per dati sensibili.

La generazione delle password resta centralizzata in `services.passwords.generate_password()`. I frontend raccolgono soltanto le opzioni: non devono implementare RNG o alfabeti alternativi.

## M1.20.1 Compatibilità dei binding Textual

Textual interpreta la virgola nella specifica della chiave di un `Binding` come separatore tra scorciatoie alternative. Non usare quindi una scorciatoia letterale come `ctrl+,`: viene interpretata come un binding alternativo vuoto e può generare `InvalidBinding` già durante la creazione della classe dell'applicazione. Keys NG usa `F2` per le Preferenze TUI. M1.20.3 vieta inoltre i binding principali `Ctrl+Shift+<lettera>`, perché molti terminali collassano queste sequenze su `Ctrl+<lettera>`; `Ctrl+I` è ambiguo con Tab. I test di regressione verificano entrambe le regole.

## Regola PySide6 e shadowing del nome gettext `_` (M1.20.2)

`keys_ng.gui.main` importa gettext come `_`. Non usare `_` come variabile di scarto dentro una funzione che chiama anche `_()`. Python considera il nome assegnato locale per l'intera funzione, quindi costrutti come `path, _ = QFileDialog.getOpenFileName(..., _("Titolo"), ...)` generano `UnboundLocalError`. Usare invece un nome descrittivo, ad esempio `selected_filter`. Un test di regressione verifica questa regola.

## M1.20.4 modello di sessione multi-vault TUI

`services.vault_sessions.VaultSessionManager` mantiene l'insieme degli oggetti `Vault` aperti nella TUI e il puntatore al vault attivo. L'apertura di un vault aggiunge/riusa un oggetto invece di terminare e riavviare l'app Textual. Il cambio modifica il riferimento `vault` catturato dalle closure e aggiorna albero/dettaglio. Passare a un vault locked non ne provoca la decifratura. Il lock normale è per-vault; l'hard lock blocca prima tutti i vault aperti (svuotando tutte le cache decifrate) e solo dopo chiama una volta `hard_lock()` sul backend crittografico condiviso. La chiusura blocca il vault prima di rimuoverlo dalla sessione.

