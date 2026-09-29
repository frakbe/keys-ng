# Keys NG

Keys NG è una riscrittura di nuova generazione del password manager Bash originale **Keys**. Mantiene l'idea originale di salvare ogni credenziale come oggetto OpenPGP cifrato in modo indipendente, eliminando i file temporanei in chiaro dal normale flusso operativo.

## Stato attuale

Il repository è attualmente nello sviluppo **M1.18.1 alpha di manutenzione con parità funzionale TUI**. Non è ancora una release di sicurezza pronta per uso di produzione.

Funzionalità principali già implementate:

- formato JSON versionato e un record `.gpg` cifrato per ogni voce;
- catalogo di ricerca cifrato e ricostruibile, con privacy dei metadati configurabile e cache RAM durante la sessione sbloccata;
- cartelle e sottocartelle logiche cifrate in `folders.gpg`, mentre i filename delle voci restano UUID opachi;
- GUI PySide6 multi-vault con tab verticali, selettore nativo delle directory, albero con drag & drop, icone, ricerca live (`Ctrl+F`), menu applicativi e guida integrata;
- TUI Textual opzionale (`keys-ng-tui`) con navigazione ad albero, ricerca veloce, creazione/modifica/spostamento/eliminazione di voci e cartelle, campi TOTP/SSH e avvisi clipboard ad alta visibilità;
- integrazione GnuPG/gpg-agent tramite pipe, senza gestione della passphrase privata in Python;
- selezione delle chiavi tramite fingerprint completo e verifica delle firme OpenPGP;
- lock applicativo e hard-lock globale di GnuPG;
- generatore password basato su `secrets`;
- TOTP RFC 6238, URI `otpauth://`, inserimento manuale del secret Base32 e import QR opzionale;
- shortcut GUI: `Ctrl+U` URL, `Ctrl+B` username, `Ctrl+C` password, `Ctrl+T` TOTP, `Ctrl+O` apertura URL/azione;
- clipboard temporizzata: GUI tramite Qt; CLI/TUI preferibilmente tramite backend nativi Wayland/X11/macOS/Windows, con Qt come fallback;
- azioni strutturate URL, SSH e RDP senza invocazione della shell;
- workflow inbox cifrata write-only;
- CRUD via CLI e GUI;
- internazionalizzazione GNU gettext `.po/.mo`;
- migrazione sicura da Keys 1.0.1 senza eseguire i record Bash;
- import KeePassXC da `.kdbx` tramite `keepassxc-cli` o da export XML;
- impostazioni TOML in directory native della piattaforma;
- controlli di consistenza del catalogo e test automatici.

## Stato di sicurezza

**Non usare ancora questa snapshot di sviluppo come unico archivio delle password.** Sono ancora necessari audit esterno e validazione completa del packaging multipiattaforma.

Keys NG non scrive intenzionalmente le voci decifrate in file temporanei persistenti. Il ciphertext viene passato a GnuPG tramite stdin; il JSON decifrato esiste soltanto nella memoria del processo. Python non può garantire l'azzeramento deterministico di stringhe e byte immutabili, perciò durata del processo e semantica del lock fanno parte del threat model.

## Avvio rapido

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\\Scripts\\activate
pip install -e .

keys-ng keys
keys-ng keys --secret

keys-ng init ~/my-vault \
  --recipient FINGERPRINT_CIFRATURA \
  --signer FINGERPRINT_FIRMA \
  --catalog-privacy standard

keys-ng add ~/my-vault --url https://example.org
keys-ng list ~/my-vault
keys-ng search ~/my-vault example
keys-ng password ~/my-vault ENTRY_ID --copy
keys-ng otp ~/my-vault ENTRY_ID --copy
keys-ng catalog-health ~/my-vault
keys-ng lock --hard
```

Per la GUI:

```bash
pip install -e '.[gui]'
keys-ng-gui ~/my-vault
```

Per l'import TOTP da QR:

```bash
pip install -e '.[gui,qr]'
```

Per la TUI:

```bash
pip install -e '.[tui]'
keys-ng-tui ~/my-vault
```

## Ricerca e shortcut GUI

Finché il vault è sbloccato, Keys NG conserva in RAM soltanto il **catalogo decifrato e i metadati delle cartelle**. Password, seed TOTP e JSON completo vengono decifrati soltanto quando si apre una specifica voce. Le cache vengono eliminate con lock e hard-lock.

Shortcut principali:

- `Ctrl+F`: ricerca;
- `Ctrl+U`: copia URL;
- `Ctrl+B`: copia username;
- `Ctrl+C`: copia password;
- `Ctrl+T`: copia TOTP;
- `Ctrl+O`: apre l'URL o esegue l'azione strutturata selezionata.

Il menu `?` apre localmente questa guida, il modello di sicurezza e le note di licenza nella lingua dell'interfaccia, con fallback all'inglese.

## Cartelle

```bash
keys-ng folder create ~/my-vault 'Personali/Cloud'
keys-ng folder list ~/my-vault
keys-ng add ~/my-vault --folder 'Personali/Cloud' --title Aruba
keys-ng move ~/my-vault ENTRY_ID 'Personali/Conti'
```

I nomi delle cartelle non compaiono nei filename del vault e restano all'interno di metadati cifrati.

## Migrazione KeePassXC

Il percorso preferito importa direttamente il database KDBX. Keys NG esegue `keepassxc-cli export --format xml` e legge l'XML da stdout, senza implementare internamente la crittografia KDBX e senza creare un export XML temporaneo persistente.

```bash
keys-ng import-keepassxc ~/Passwords.kdbx ~/my-vault
keys-ng import-keepassxc ~/Passwords.kdbx ~/my-vault --key-file ~/db.keyx
keys-ng import-keepassxc ~/Passwords.kdbx ~/my-vault --yubikey 2:SERIAL
keys-ng import-keepassxc ~/Passwords.kdbx ~/my-vault --dry-run
```

È supportato anche un export XML già esistente:

```bash
keys-ng import-keepassxc ~/Passwords.xml ~/my-vault --format xml
```

### UUID e riferimenti durante la migrazione

L'import KeePassXC avviene in due passaggi. Gli UUID originali delle voci vengono conservati quando non entrano in conflitto con una voce già presente nel vault Keys NG. In caso di collisione, Keys NG genera un nuovo UUID per la voce importata e riscrive automaticamente i riferimenti UUID `{REF:U@I:...}` e `{REF:P@I:...}` affinché continuino a puntare alla voce importata corretta. Prima di scrivere cartelle e record viene eseguita una validazione delle catene di riferimenti: riferimenti mancanti, cicli o campi username/password sorgente vuoti interrompono l'importazione invece di lasciare un database apparentemente importato ma non coerente. Anche `--dry-run` esegue questa verifica senza scrivere le voci.

Vengono preservati gruppi/cartelle, username, password, URL, note, tag, TOTP e campi stringa personalizzati ove supportati. Attachment, history e custom icon non vengono ancora migrati.

## Configurazione

Esempio TOML:

```toml
language = "auto"

[clipboard]
password_timeout = 20
totp_timeout = 10

[security]
auto_lock_timeout = 300
crypto_backend = "auto"

[ui]
# "expanded" apre tutte le cartelle; "compact" le avvia chiuse.
tree_startup_view = "expanded"

[launchers.ssh]
# "auto" preferisce xdg-terminal-exec/xdg-terminal su Linux e poi i terminali comuni.
# È possibile indicare un comando o un percorso assoluto per forzare il terminale.
terminal = "auto"
# Argomenti inseriti tra l'eseguibile del terminale e il comando ssh.
terminal_options = []

[launchers.rdp.linux]
# "auto" seleziona xfreerdp3 e poi xfreerdp.
client = "auto"
options = ["/dynamic-resolution", "+clipboard"]

[launchers.rdp.windows]
client = "mstsc"
options = []

[launchers.rdp.macos]
# "auto" usa il launcher macOS `open` con un URI rdp://.
# Per forzare Microsoft Windows App, ad esempio: options = ["-a", "Windows App"]
client = "auto"
options = []
```


GUI e TUI accettano anche una scelta valida solo per quell'avvio:

```bash
keys-ng-gui ~/my-vault --tree-view compact
keys-ng-tui ~/my-vault --tree-view expanded
```


### Launcher SSH e RDP

Nel dialog della GUI una voce può ora essere definita esplicitamente come **Web / URL**, **connessione SSH**, **connessione RDP** o **credenziale generica**. Per SSH e RDP vengono mostrati Host e Porta al posto dell'URL. Le password non vengono mai inserite nella command line dei processi.

Su Linux, SSH viene aperto in un terminale. Con `terminal = "auto"`, Keys NG preferisce `xdg-terminal` quando disponibile e poi `xdg-terminal-exec` e quindi i terminali più comuni. `terminal_options` è un array di argomenti, non una stringa interpretata da una shell. Per RDP ogni sistema operativo dispone di una sezione propria per client e opzioni. Le opzioni Linux vengono passate a FreeRDP prima di `/v:` e `/u:`; quelle Windows a `mstsc` prima di `/v:`; quelle macOS a `open` prima dell'URI `rdp://`.


Per ogni singola connessione SSH la GUI offre inoltre **X11 forwarding** separato (`off`, `-X`, `-Y`) e un campo **Opzioni SSH avanzate**. Il campo accetta opzioni OpenSSH come `-J bastion.example.org`, `-L 8080:localhost:80`, `-R`, `-D` o `-o ServerAliveInterval=30`. Il testo viene convertito in una lista `argv` senza usare una shell. Username, porta e `-X`/`-Y` restano campi gestiti separatamente e non possono essere ridefiniti nelle opzioni avanzate.

Esempio CLI:

```bash
keys-ng add ~/my-vault --title "Server via bastion" --username mario \
  --ssh-host server.internal --ssh-port 22 --ssh-x11 Y \
  --ssh-options '-J bastion.example.org -o ServerAliveInterval=30'
```

## Localizzazione

Le stringhe dell'interfaccia usano GNU gettext. I traduttori lavorano sui file `.po` in `locales/<lingua>/LC_MESSAGES/keys-ng.po`; i `.mo` compilati vengono inclusi nel pacchetto.

Anche i documenti della guida sono localizzati. Sono incluse almeno le versioni inglese e italiana di README, SECURITY e note di licenza.

## Migrazione da Keys 1.0.1

Il migratore non usa mai `source` e non esegue il contenuto decifrato dei vecchi record Bash:

```bash
keys-ng migrate-legacy ~/old-keystore/KEYROOT ~/my-vault --dry-run
keys-ng migrate-legacy ~/old-keystore/KEYROOT ~/my-vault --verify
```

Le directory legacy vengono ricreate come cartelle logiche cifrate nel nuovo vault.

## Licenza e autore

Keys NG è distribuito con licenza **GPL-3.0-or-later**.

Autore: **Franco 'frakbe' Bersani**, autore anche del progetto originale Keys.

### Integrazione desktop Linux / GNOME Wayland

Alla prima apertura della GUI su Linux, Keys NG installa in modo best-effort per il solo utente:

```text
~/.local/share/applications/org.keysng.KeysNG.desktop
~/.local/share/icons/hicolor/64x64/apps/org.keysng.KeysNG.png
```

Questo permette a GNOME/Wayland di associare la finestra all’icona dell’applicazione. L’integrazione può essere gestita esplicitamente con:

```bash
keys-ng desktop install
keys-ng desktop status
keys-ng desktop uninstall
```

`XDG_DATA_HOME`, se impostata, viene rispettata. Non sono richiesti privilegi di root.


## GUI multi-vault (M1.17)

La GUI può essere avviata senza specificare alcun vault:

```bash
keys-ng-gui
```

Dal menu **Vault → Apri vault…** (`Ctrl+Shift+O`) viene aperta la finestra nativa del sistema operativo per selezionare la directory del vault. È inoltre possibile aprire più vault direttamente dalla riga di comando:

```bash
keys-ng-gui ~/vault-personale ~/vault-lavoro
```

Ogni vault viene mostrato in un tab verticale separato, con il nome della directory come titolo e il percorso completo come tooltip. Ricerca, albero, selezione, TOTP e auto-lock restano indipendenti per ogni tab. `Ctrl+W` chiude soltanto il vault attivo. Il **blocco completo** è invece globale: svuota lo stato in RAM di tutti i vault aperti prima di terminare il `gpg-agent` condiviso.

## Credenziali riutilizzabili e riferimenti UUID (M1.12)

Keys NG supporta un sottoinsieme compatibile con la sintassi di riferimento UUID di KeePassXC per riutilizzare credenziali memorizzate in un'altra voce dello **stesso vault**:

```text
username = {REF:U@I:<UUID>}
password = {REF:P@I:<UUID>}
```

Sono accettati sia gli UUID canonici con trattini sia gli UUID KeePass in formato esadecimale a 32 caratteri. I riferimenti possono essere concatenati; cicli, voci mancanti e riferimenti a campi vuoti vengono segnalati al momento della risoluzione.

La GUI mostra l'UUID della voce selezionata e offre **Copia UUID** (`Ctrl+Shift+I`). La TUI mostra l'UUID nel pannello dei dettagli e lo copia con `F4`. La copia di username/password e l'apertura di connessioni SSH/RDP risolvono il riferimento al momento dell'uso: cambiando le credenziali nella voce sorgente, la modifica diventa quindi immediatamente effettiva per tutte le voci che la referenziano.

Esempio:

```text
UUID credenziali condivise: 8b14aa0e-4e79-4e4d-8ef8-8bf95d4594da

Username Server A: {REF:U@I:8b14aa0e-4e79-4e4d-8ef8-8bf95d4594da}
Password Server A: {REF:P@I:8b14aa0e-4e79-4e4d-8ef8-8bf95d4594da}
```

Al momento Keys NG risolve i campi `U` (username) e `P` (password) tramite UUID (`@I`). Le altre modalità di cross-reference di KeePassXC non sono ancora implementate.

### Vault recenti e deposito inbox con sola chiave pubblica

La GUI mantiene gli ultimi cinque vault aperti nel menu **Vault > Recenti**.

Un collaboratore che possiede soltanto la chiave pubblica del proprietario può
creare una voce cifrata autonoma senza possedere né aprire il vault:

```bash
keys-ng inbox-create --public-key proprietario.asc --output nuova-voce.gpg \
  --title "Nuovo server" --username alice --ssh-host host.example.org
```

Il file `nuova-voce.gpg` può essere copiato manualmente nella directory
`inbox/` del vault. Poiché un deposito creato con la sola chiave pubblica non è
firmato, il proprietario deve approvarlo esplicitamente:

```bash
keys-ng import-inbox ~/vault --accept-unsigned
```

## M1.15: documentazione, menu applicazioni ed export XML KeePassXC

La documentazione consolidata è ora organizzata in:

- `docs/en/USER_GUIDE.md`
- `docs/en/DEVELOPER_GUIDE.md`
- `docs/it/USER_GUIDE.md`
- `docs/it/DEVELOPER_GUIDE.md`

L'integrazione per utente nel menu applicazioni è disponibile su Linux, Windows e macOS:

```bash
keys-ng desktop install
keys-ng desktop status
keys-ng desktop uninstall
```

L'export XML in chiaro compatibile con KeePassXC è disponibile per la singola voce e per l'intero vault:

```bash
keys-ng export-entry VAULT UUID_VOCE voce.xml
keys-ng export-vault VAULT vault.xml
```

La GUI espone l'export singolo in `Voce -> Esporta come XML KeePassXC...`; nella TUI si usa il tasto `E` sulla voce selezionata. I file XML sono in chiaro e devono essere protetti e rimossi in modo sicuro dopo l'uso.


### Versione installata

```bash
keys-ng version
keys-ng-tui version
```

La GUI mostra la stessa versione in **? → Licenza**.

## M1.16: packaging nativo e Preferenze

M1.16 aggiunge **Impostazioni → Preferenze…** per modificare il `config.toml`
globale con spiegazioni in linea, oltre a `Ctrl+L` (blocco), `Ctrl+Shift+L`
(blocco completo) e `Ctrl+P` (sblocco) sia in GUI sia in TUI. `keys-ng doctor`
controlla ora l'intero ambiente di esecuzione.

Sono incluse le ricette di distribuzione per Flatpak Linux, MSI Windows e DMG
macOS. Vedere `packaging/flatpak/` e `.github/workflows/distribution.yml`.

## M1.20: parità interattiva

M1.20 allinea i normali flussi utente di GUI e TUI: import KeePassXC KDBX/XML, export XML dell'intero vault e della singola voce, note copiabili/modificabili, generatore password integrato, apertura/chiusura/vault recenti, preferenze e aiuto. I comandi amministrativi/diagnostici restano intenzionalmente orientati alla CLI. Vedere `RELEASE_NOTES_M1.20.md` e le guide utente/sviluppatore EN/IT.

### M1.20.3 scorciatoie TUI portabili tra terminali

La TUI non usa più `Ctrl+Shift+<lettera>` per i comandi principali. Usare `F2` Preferenze, `F3` Firmatari attendibili, `F5` Apri vault, `F6` Vault recenti, `F7` Import KeePassXC, `F8` export XML dell'intero vault e `F9` hard lock. `Ctrl+N` copia le Note, `Ctrl+D` crea una cartella e `?` apre la guida comandi in linea. Le scorciatoie GUI restano invariate.

### M1.20.4 cambio vault nella TUI

La TUI mantiene ora più vault aperti nella stessa sessione. `F5`/`F6` aggiungono vault, `Ctrl+J` apre il selettore dei vault, `Ctrl+W` chiude il vault attivo, `Ctrl+L` blocca soltanto il vault attivo e `F9` esegue hard lock di tutti i vault aperti oltre alla cache condivisa di gpg-agent.

