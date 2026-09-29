# Guida utente di Keys NG

## 1. Cos'è Keys NG

Keys NG è un password manager basato su OpenPGP. Ogni voce viene salvata in un file cifrato separato, mentre i metadati necessari alla ricerca e l'albero logico delle cartelle sono conservati in file di metadati anch'essi cifrati. Lo stesso vault può essere utilizzato da CLI, TUI Textual e GUI PySide6.

Gli obiettivi principali sono:

- nessun file di credenziali in chiaro durante il normale utilizzo;
- possibilità di conservare il vault cifrato anche su cloud non fidato;
- delega di decifratura e passphrase a GnuPG e `gpg-agent`;
- supporto per password, TOTP, URL, SSH e RDP;
- cartelle logiche cifrate, non visibili come nomi di directory sul cloud;
- riuso delle credenziali tramite riferimenti UUID;
- possibilità per terzi di depositare una voce conoscendo soltanto la chiave pubblica del proprietario.

## 2. Installazione

È consigliato un ambiente virtuale:

```bash
python -m venv ~/.venvs/keys-ng
source ~/.venvs/keys-ng/bin/activate
pip install 'keys-ng[gui,tui,qr]'
```

GnuPG deve essere installato separatamente. PySide6 è necessario per la GUI, Textual per la TUI e le dipendenze QR per l'importazione dei codici QR.

Per registrare Keys NG nel menu applicazioni dell'utente:

```bash
keys-ng desktop install
```

Per controllare o rimuovere l'integrazione:

```bash
keys-ng desktop status
keys-ng desktop uninstall
```

L'implementazione è specifica per piattaforma:

- Linux: file `.desktop` freedesktop e icona hicolor;
- Windows: collegamento nel menu Start;
- macOS: bundle launcher `~/Applications/Keys NG.app`.

La GUI tenta anche di registrarsi automaticamente all'avvio.

## 3. Creazione di un vault

Per vedere le chiavi OpenPGP disponibili:

```bash
keys-ng keys
keys-ng keys --secret
```

Creazione del vault con fingerprint completi:

```bash
keys-ng init ~/vaults/personale \
  --recipient FINGERPRINT_COMPLETO_CIFRATURA \
  --signer FINGERPRINT_COMPLETO_FIRMA \
  --catalog-privacy standard
```

Il vault contiene record cifrati, catalogo cifrato, struttura cartelle cifrata e directory Inbox.

## 4. Avvio delle interfacce

CLI:

```bash
keys-ng list ~/vaults/personale
```

TUI:

```bash
keys-ng-tui ~/vaults/personale
```

Con M1.18 la TUI raggiunge la parità operativa quotidiana con la GUI. Nella vista ad albero:

- `N` crea una nuova voce nella cartella selezionata/corrente;
- `Ctrl+D` crea una nuova cartella;
- `E` modifica una voce oppure rinomina una cartella;
- `M` sposta una voce o una cartella;
- `Delete` elimina la voce selezionata o una cartella vuota dopo conferma;
- `X` esporta la voce selezionata come XML KeePass compatibile in chiaro.

L'editor supporta credenziali generiche, Web/URL, SSH e RDP, riferimenti UUID in username/password, tag, note, URI/secret TOTP, import TOTP da file immagine QR, forwarding X11 SSH e opzioni SSH avanzate in forma argv. I campi non pertinenti al tipo di voce selezionato vengono ignorati al salvataggio.

GUI senza aprire un vault:

```bash
keys-ng-gui
```

La GUI permette di selezionare i vault con il dialog nativo del sistema e di tenere più vault contemporaneamente in tab verticali. È anche possibile passarli all'avvio:

```bash
keys-ng-gui ~/vaults/personale ~/vaults/lavoro
```

## 5. Configurazione

Su Linux il file è normalmente:

```text
~/.config/keys-ng/config.toml
```

Negli altri sistemi `platformdirs` sceglie il percorso di configurazione nativo.

Esempio:

```toml
language = "it"

[clipboard]
password_timeout = 20
totp_timeout = 10

[security]
auto_lock_timeout = 300
crypto_backend = "auto"

[ui]
tree_startup_view = "compact"
recent_vaults = []

[ui.tui]
# Colori vuoti: usa i colori semantici del tema Textual.
clipboard_notice_background = ""
clipboard_notice_foreground = ""
clipboard_notice_seconds = 2.5

[launchers.ssh]
terminal = "auto"
terminal_options = []

[launchers.rdp.linux]
client = "auto"
options = ["/dynamic-resolution", "+clipboard"]

[launchers.rdp.windows]
client = "mstsc"
options = []

[launchers.rdp.macos]
client = "auto"
options = []
```

`tree_startup_view` accetta `expanded` oppure `compact`.

## 6. Voci e cartelle

Le voci possono essere organizzate in una gerarchia arbitraria di cartelle e sottocartelle. I nomi delle cartelle rimangono cifrati; il filesystem espone soltanto file con nomi UUID.

Una voce può contenere:

- titolo;
- uno o più username;
- password;
- configurazione TOTP;
- tag e note;
- campi personalizzati;
- azioni URL, SSH, RDP o comandi strutturati.

Nella GUI l'editor propone i tipi `Credenziale generica`, `Web / URL`, `Connessione SSH` e `Connessione RDP`.

## 7. Shortcut della GUI

```text
Ctrl+U       copia URL
Ctrl+B       copia username
Ctrl+C       copia password
Ctrl+T       copia TOTP
Ctrl+O       apre l'azione URL/SSH/RDP
Ctrl+Shift+I copia UUID della voce
Ctrl+F       ricerca
```

La clipboard viene cancellata dopo il timeout configurato quando Keys NG può verificare che contenga ancora il valore inserito dall'applicazione.

## 8. TOTP

Il TOTP può essere configurato mediante:

- secret Base32;
- URI `otpauth://`;
- QR code da file locale o clipboard nella GUI.

Il seed resta nel record cifrato. Il codice temporaneo viene calcolato in memoria.

## 9. SSH

Le voci SSH definiscono host, porta, username, X11 forwarding e opzioni avanzate.

L'X11 forwarding dispone di un campo dedicato:

```text
off
-X
-Y
```

Le opzioni avanzate possono contenere, ad esempio:

```text
-J bastion.example.org -o ServerAliveInterval=30
-L 8080:localhost:80
-D 1080
```

Keys NG non utilizza una shell per interpretarle: le converte in una lista di argomenti e avvia il client con `shell=False`.

Il terminale da utilizzare per SSH è configurato globalmente nel `config.toml`. La password non viene inserita nella command line del processo.

## 10. RDP

Le voci RDP contengono host, porta e username. Client e opzioni sono configurabili separatamente per Linux, Windows e macOS nel `config.toml`.

Anche in questo caso la password non viene inserita nella riga di comando del client.

## 11. Riuso delle credenziali tramite UUID

Keys NG implementa il sottoinsieme di riferimenti compatibile con KeePassXC:

```text
username = {REF:U@I:<UUID>}
password = {REF:P@I:<UUID>}
```

Esempio:

```text
{REF:U@I:033054d4-45c6-48c5-9092-cc1d661b1b71}
{REF:P@I:033054d4-45c6-48c5-9092-cc1d661b1b71}
```

Il riferimento viene risolto quando il valore viene utilizzato. Modificando la voce sorgente, tutte le voci che la referenziano usano immediatamente il nuovo valore. Cicli e riferimenti inesistenti vengono rifiutati.

## 12. Ricerca

La ricerca usa il catalogo cifrato. Dopo lo sblocco, i metadati del catalogo vengono mantenuti in RAM, evitando di richiamare GnuPG per ogni record/cartella.

GUI e TUI effettuano una ricerca globale, indipendente dalla cartella attualmente visualizzata.

## 13. Lock e hard-lock

Il lock normale elimina le cache di metadati decifrati del vault. L'hard-lock elimina anche l'autorizzazione memorizzata da `gpg-agent`. Poiché l'agent è condiviso dalla sessione utente, nella GUI multi-vault l'hard-lock è globale.

## 14. Vault recenti

La GUI conserva gli ultimi cinque vault aperti. Sono disponibili in `Vault → Recenti` e memorizzati nel file TOML di configurazione.

## 15. Workflow Inbox con sola chiave pubblica

Un altro utente può creare una voce cifrata senza possedere il vault o la tua chiave privata:

```bash
keys-ng inbox-create \
  --public-key proprietario-public.asc \
  --output nuovo-server.gpg \
  --title "Nuovo server" \
  --username admin \
  --ssh-host server.example.org
```

Il file `.gpg` risultante può essere copiato manualmente nella directory `inbox/` del vault.

Un record creato con la sola chiave pubblica non può essere firmato dal proprietario. Gli elementi unsigned vengono quindi rifiutati per default. Il proprietario può approvarli esplicitamente:

```bash
keys-ng import-inbox ~/vaults/personale --accept-unsigned
```

Dopo la validazione, la voce viene salvata nuovamente con destinatari e signer normali del vault.

## 16. Importazione da KeePassXC

Per un KDBX Keys NG delega la decifratura a `keepassxc-cli` e riceve l'XML tramite pipe:

```bash
keys-ng import-keepassxc Passwords.kdbx ~/vaults/personale
```

È possibile importare anche un XML già esportato:

```bash
keys-ng import-keepassxc Passwords.xml ~/vaults/personale --format xml
```

Vengono importati gruppi/cartelle, username, password, URL, TOTP, tag, note e campi stringa personalizzati. I riferimenti UUID KeePassXC vengono preservati oppure rimappati in modo sicuro in caso di collisione con UUID già presenti.

## 17. Esportazione XML compatibile con KeePassXC

### 17.1 Singola voce dalla CLI

```bash
keys-ng export-entry ~/vaults/personale UUID_VOCE voce.xml
```

Nell'export singolo i riferimenti a credenziali vengono risolti, perché la voce sorgente potrebbe non essere inclusa nel file.

### 17.2 Singola voce dalla TUI

Seleziona la voce e premi:

```text
E
```

Il file XML viene creato nella directory corrente con nome derivato da titolo e UUID.

### 17.3 Singola voce dalla GUI

Seleziona la voce e usa:

```text
Voce → Esporta come XML KeePassXC…
```

Viene aperto il dialog nativo di salvataggio.

### 17.4 Intero vault

```bash
keys-ng export-vault ~/vaults/personale vault-completo.xml
```

L'export completo mantiene gerarchia delle cartelle, UUID delle voci e riferimenti UUID, permettendo a KeePassXC di ricostruire le credenziali condivise.

> **Avvertenza di sicurezza:** l'XML KeePass è in chiaro. Contiene password, seed TOTP e altri segreti. Proteggilo, importalo appena possibile e rimuovilo in modo sicuro quando non serve più.

## 18. Migrazione dal vecchio Keys

La struttura legacy Bash può essere migrata senza eseguire (`source`) i record decifrati:

```bash
keys-ng migrate-legacy OLD_KEYROOT ~/vaults/personale --verify
```

Le directory legacy vengono trasformate in cartelle logiche cifrate.

## 19. Comandi di manutenzione

```bash
keys-ng reindex ~/vaults/personale
keys-ng catalog-health ~/vaults/personale
keys-ng doctor
keys-ng desktop status
```

`reindex` ricostruisce il catalogo cifrato dai record. `catalog-health` controlla la coerenza tra catalogo, record e cartelle.

## 20. Limiti di sicurezza da ricordare

Keys NG protegge i dati a riposo ed evita i normali file temporanei in chiaro, ma un endpoint già compromesso può comunque osservare memoria, clipboard, schermo, processi client, input da tastiera o ambiente GnuPG.

Memorizzare password e seed TOTP nello stesso vault è comodo, ma i due fattori non restano indipendenti in caso di compromissione del vault. Per una separazione forte è preferibile mantenere il TOTP su un autenticatore separato.


### Versione installata

```bash
keys-ng version
keys-ng-tui version
```

La GUI mostra la stessa versione in **? → Licenza**.

## M1.16: Preferenze e pacchetti desktop nativi

La GUI dispone ora di **Impostazioni → Preferenze…** (`Ctrl+,`), quindi non è
più necessario modificare manualmente `config.toml` per le normali opzioni. La
finestra modifica lo stesso file globale indicato da `keys-ng doctor` ed è
divisa nelle sezioni Generale, Appunti, SSH e RDP. Ogni parametro dispone di una
spiegazione in linea. Le opzioni dei launcher sono inserite come **un argomento
argv per riga** e non vengono interpretate da una shell. Per esempio, per fare
aprire a Ptyxis una connessione SSH in un nuovo tab si imposta il terminale SSH
su `ptyxis` e si inseriscono su due righe distinte:

```text
--tab
--
```

Alcune impostazioni (lingua, backend crittografico e vista iniziale dell'albero)
si applicano in modo più sicuro ai vault aperti successivamente o dopo un
riavvio di Keys NG; i timeout vengono invece usati immediatamente.

Le scorciatoie di blocco comuni a GUI e TUI sono:

- `Ctrl+L`: blocca il vault corrente;
- `Ctrl+Shift+L`: blocco completo con cancellazione della cache di gpg-agent; nella
  GUI multi-vault questa operazione è intenzionalmente globale;
- `Ctrl+P`: sblocca il vault corrente.

### Formati di installazione desktop raccomandati

Keys NG include ora le ricette per pacchetti nativi:

- Linux: Flatpak (`packaging/flatpak/`) basato su `io.qt.PySide.BaseApp`;
- Windows: installer MSI tramite Briefcase;
- macOS: bundle `.app` distribuito in DMG tramite Briefcase;
- wheel Python: mantenuta per sviluppatori e installazioni avanzate.

Il Flatpak delega intenzionalmente al sistema host GnuPG, SSH e RDP tramite
`flatpak-spawn --host`, così vengono riutilizzati keyring/gpg-agent, terminale e
client di desktop remoto già configurati dall'utente. Questo richiede il
permesso D-Bus `org.freedesktop.Flatpak` e va considerato nell'analisi di
sicurezza.

Eseguire:

```bash
keys-ng doctor
```

per controllare versione installata, Python, GnuPG, moduli opzionali GUI/TUI/QR,
backend degli appunti, strumenti SSH/RDP, integrazione nel menu applicazioni e
percorso del file di configurazione.

## Creazione di un nuovo vault da GUI o TUI (M1.19)

La GUI offre ora **Vault → Nuovo vault…** (`Ctrl+Shift+N`) e il pulsante **Crea nuovo vault…** quando non è aperto alcun vault. La procedura guidata permette di scegliere una directory vuota, una chiave OpenPGP destinataria esistente, una chiave privata di firma esistente e il livello di privacy del catalogo. Prima della creazione vengono mostrati i fingerprint completi. Keys NG esegue un self-test di cifratura/decifratura/firma prima di scrivere i file del vault e apre automaticamente il vault appena creato.

La TUI può ora essere avviata senza specificare un vault:

```text
keys-ng-tui
```

Viene mostrata una procedura guidata da tastiera per creare il nuovo vault. Keys NG non genera coppie di chiavi OpenPGP: vanno create/importate prima tramite GnuPG/Kleopatra.

Su Windows, M1.19 cerca automaticamente le normali installazioni Gpg4win/GnuPG anche quando `gpg.exe` non è nel `PATH`. Se necessario, i percorsi espliciti di `gpg` e `gpgconf` possono essere configurati nelle Preferenze.

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

## Inbox e firmatari attendibili (M1.19.2)

La Inbox è un confine di collaborazione in sola scrittura. Un collega può cifrare una credenziale verso la chiave pubblica del proprietario del vault e, opzionalmente, firmarla con la propria chiave. All'apertura del vault GUI e TUI contano i file `inbox/*.gpg` senza decifrarli. Se esistono elementi pendenti, la GUI propone di esaminarli subito e la TUI mostra un avviso `Inbox: N pending`; la Inbox resta sempre raggiungibile successivamente da **Vault → Inbox…** oppure con il tasto `I` nella TUI.

Aprendo esplicitamente la revisione Inbox, gli elementi vengono decifrati per l'ispezione e classificati come **VALID / TRUSTED**, **VALID SIGNATURE / SIGNER NOT AUTHORIZED**, **UNSIGNED**, **INVALID SIGNATURE**, **CANNOT DECRYPT** oppure **MALFORMED ENTRY**. Una firma OpenPGP valida non è sufficiente da sola: il fingerprint della chiave primaria deve essere autorizzato nella lista `trusted_signers` di quel vault. Questa autorizzazione per-vault è intenzionalmente distinta dall'ownertrust di GnuPG/Kleopatra.

Per un firmatario valido ma non autorizzato, GUI e TUI permettono di autorizzare esplicitamente la chiave per il vault corrente dopo averne mostrato il fingerprint completo. La gestione indipendente dei firmatari è disponibile anche dal dialogo GUI **Trusted signers…**, dalla scorciatoia TUI `F3` e dai comandi `keys-ng trust list/add/remove`.

Gli elementi non firmati restano rifiutati per default. L'Inbox interattiva può importarli solo dopo un avviso esplicito che ricorda che il mittente non è autenticabile. Una firma non valida non può essere aggirata trattando l'elemento come unsigned.

Un'importazione riuscita analizza la voce esterna, controlla eventuali collisioni UUID, crea un normale record cifrato per i recipient del vault e firmato dal signer del vault, aggiorna il catalogo cifrato e soltanto dopo elimina il file sorgente dalla Inbox. In caso di errore il ciphertext resta nella Inbox. La cancellazione senza import richiede conferma esplicita.

## M1.20: parità interattiva tra GUI e TUI

M1.20 definisce un contratto esplicito di parità per i normali flussi interattivi. GUI e TUI permettono entrambe creazione/apertura/chiusura e accesso ai vault recenti, gestione di voci e cartelle, Inbox/firmatari attendibili, preferenze/aiuto, esportazione XML KeePassXC della singola voce e dell'intero vault, import KeePassXC KDBX/XML, copia delle note e generazione password. Le operazioni amministrative/diagnostiche come `doctor`, `reindex`, `catalog-health`, integrazione desktop e migrazione legacy restano intenzionalmente orientate alla CLI.

### Note: copia e incolla

Le note sono considerate dati potenzialmente sensibili. Nella GUI il visualizzatore read-only delle note è selezionabile e **Copia note** copia l'intero contenuto applicando la stessa cancellazione temporizzata degli appunti usata per password/username. Durante l'editing, le normali scorciatoie del widget di testo (`Ctrl+C`, `Ctrl+X`, `Ctrl+V`) operano sul testo selezionato invece di richiamare la copia globale della password.

Nella TUI l'editor note è un `TextArea` Textual e, quando ha il focus, le sue scorciatoie native di copia/incolla hanno precedenza. Fuori dall'editor `Ctrl+C` continua a copiare la password della voce selezionata. `Ctrl+N` copia esplicitamente l'intera nota con cancellazione temporizzata.

### Generatore di password

Gli editor delle voci, sia GUI sia TUI, includono ora **Genera…**. Il generatore usa `secrets` tramite l'implementazione condivisa `services.passwords.generate_password()` e permette di scegliere lunghezza, maiuscole, minuscole, numeri, simboli e l'eventuale inclusione di caratteri ambigui. Il valore generato resta nel campo del generatore/editor fino al salvataggio; nella TUI il pulsante **Copia password generata** permette di copiarlo temporaneamente prima di applicarlo alla voce, così può essere provato sul servizio remoto.

### Import KeePassXC KDBX o XML

Entrambe le interfacce interattive possono importare nel vault attualmente aperto. La sorgente può essere un file `.kdbx` KeePassXC oppure un export XML. Per KDBX la decodifica viene delegata a `keepassxc-cli`; l'XML viene ricevuto tramite stdout e non viene creato alcun file XML plaintext intermedio. Nell'import interattivo l'eventuale password del database KDBX esiste solo temporaneamente in memoria e viene passata a `keepassxc-cli` via stdin: non viene inserita in argv, variabili d'ambiente o file. Questa password non è la passphrase della chiave privata OpenPGP, che Keys NG continua a delegare esclusivamente a GnuPG/gpg-agent/pinentry.

La procedura supporta key file, database senza componente password e parametri YubiKey, con dry-run/anteprima prima della scrittura. Restano attive tutte le protezioni già previste: rifiuto di dichiarazioni XML non sicure, rimappatura delle collisioni UUID, riscrittura/validazione dei riferimenti e validazione finale riaprendo i record cifrati.

Le esportazioni XML, sia dell'intero vault sia della singola voce, contengono credenziali in chiaro. Keys NG mostra un avviso e applica permessi restrittivi dove supportati dalla piattaforma.

### M1.20.1 Scorciatoia Preferenze TUI

Nella TUI M1.20.3 le Preferenze si aprono con `F2`. Le combinazioni `Ctrl+Shift+<lettera>` sono state eliminate dai binding principali perché molti terminali non distinguono Shift quando è combinato con Ctrl; `Ctrl+I` è inoltre un alias di Tab. La guida rapida dei comandi si apre con `?`.

### M1.20.4 TUI multi-vault

`F5`/`F6` mantengono aperti altri vault nella sessione TUI corrente. `Ctrl+J` apre il selettore dei vault; ogni vault conserva il proprio stato di lock. `Ctrl+L` blocca il vault attivo, mentre `F9` esegue hard lock di tutti i vault aperti e svuota la cache condivisa di gpg-agent.

