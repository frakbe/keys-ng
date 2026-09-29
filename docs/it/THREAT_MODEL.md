# Keys NG M1.18 — Threat Model

## Ambito

Questo threat model copre Keys NG `0.1.18.dev1`, il core Python, i frontend CLI/TUI/GUI, il backend GnuPG a sottoprocesso, il layout cifrato del vault, gli helper clipboard, i launcher di azioni esterne, i percorsi import/export e il packaging desktop. Non pretende di proteggere un sistema operativo completamente compromesso.

## Asset

Gli asset principali sono password, username quando sensibili, seed TOTP, note/campi personalizzati, chiavi private OpenPGP, integrità dei record/cartelle/catalogo e capacità dell'utente di recuperare il vault. Fingerprint pubblici OpenPGP, nomi file UUID, impostazioni applicative e policy `vault.json` non sono considerati segreti, anche se possono rivelare metadati operativi.

## Confini di fiducia

1. **Memoria del processo Python.** Entry decifrate e stringhe OTP/password esistono qui. Python non garantisce la zeroizzazione deterministica degli oggetti immutabili.
2. **GnuPG / gpg-agent / Pinentry.** Keys NG delega a questi componenti le operazioni con chiavi private e l'inserimento/cache della passphrase. Keys NG non richiede intenzionalmente la passphrase della chiave privata.
3. **Storage persistente del vault.** Record, catalogo e cartelle devono essere ciphertext OpenPGP. I file temporanei delle scritture atomiche contengono solo ciphertext.
4. **Configurazione in chiaro.** `vault.json` e il TOML utente contengono policy/preferenze, mai segreti di credenziali per design.
5. **Clipboard.** Dopo la copia di un segreto, il servizio clipboard desktop e gli eventuali history manager entrano nel confine di fiducia.
6. **Programmi esterni.** Le azioni SSH/RDP/browser/command eseguono programmi esterni. `shell=False` evita il parsing di shell, ma opzioni OpenSSH come `ProxyCommand` e `LocalCommand` possono eseguire comandi e sono quindi configurazione trusted del record.
7. **Bridge host Flatpak.** Nel pacchetto Flatpak, la delega all'host attraversa intenzionalmente il sandbox per usare GnuPG agent e launcher dell'host. Il permesso è sensibile e va riesaminato con l'evoluzione del packaging.

## Classi di attaccante

### Solo vault rubato o copiato

L'attaccante ottiene la directory del vault o una copia cloud ma non una chiave privata utilizzabile. La confidenzialità dipende dalla cifratura OpenPGP ai recipient. Gli oggetti firmati forniscono anche autenticità contro sostituzioni arbitrarie del ciphertext.

### Attaccante della sincronizzazione cloud

Può aggiungere, rimuovere, sostituire o riprodurre ciphertext. M1.18 verifica le firme e collega ogni record aperto al catalogo firmato tramite SHA-256 del ciphertext e revisione. Questo rileva rollback/sostituzione del solo record quando il catalogo rimane corrente. Il rollback coordinato di record e catalogo firmato **non** è impedito senza stato monotono esterno o servizio di versioning fidato.

### Processo locale non privilegiato

Un processo di un altro account non deve poter leggere il vault. Su POSIX M1.18 crea root del vault, `records/` e `inbox/` con modalità `0700`; i file ciphertext/config sono scritti con permessi restrittivi. ACL del sistema e accesso amministratore/root restano fuori da questo controllo.

### Malware con lo stesso utente

Un processo eseguito come lo stesso utente può leggere memoria, clipboard, eventi input, socket di gpg-agent o invocare GnuPG mentre l'autorizzazione è in cache. Nessun password manager può offrire forte confidenzialità contro una sessione utente completamente compromessa. L'hard lock termina il `gpg-agent` condiviso, con effetti globali anche su altre applicazioni.

### Dati importati malevoli

XML KeePassXC, record legacy, depositi inbox, QR e configurazione sono input non fidati. I record legacy sono analizzati come dati e mai `source`-ati. L'import XML rifiuta DTD/entity. La validazione dei modelli limita UUID, azioni, parametri TOTP e topologia cartelle. Test regressivi orientati al fuzzing esercitano i percorsi di errore dei parser.

### Autore malevolo del vault / record trusted

Un firmatario autorizzato può inserire azioni command e opzioni SSH avanzate. Keys NG non invoca una shell, ma l'esecuzione di un comando trusted o di opzioni OpenSSH può intenzionalmente eseguire codice esterno. È un confine di autorizzazione, non un fallimento della protezione da injection.

## Obiettivi di sicurezza

- Nessuna persistenza intenzionale di credenziali plaintext.
- Nessuna gestione della passphrase della chiave privata da parte di Python.
- Nessuna interpretazione shell nei percorsi crypto/import/launcher.
- Verifica completa della firma per la policy dei vault firmati.
- Compartimentazione crittografica per record.
- Metadati di ricerca/cartelle cifrati con cache solo RAM mentre sbloccato.
- Fail closed su mismatch record/catalogo.
- Opt-in esplicito per import inbox non firmato.
- Risoluzione ricorsiva dei riferimenti limitata e con rilevamento cicli.
- Recupero d'emergenza portabile via CLI/GnuPG.

## Non-obiettivi e rischi residui espliciti

- Protezione da compromissione kernel/root o malware same-user con accesso a memoria/input.
- Cancellazione garantita dalla RAM di stringhe/bytes Python.
- Cancellazione garantita dagli history manager della clipboard.
- Protezione dal rollback coordinato dell'intero snapshot firmato del vault.
- Nascondere esistenza del vault, numero di record, UUID dei file, dimensioni o tempi di modifica.
- Impedire a programmi esterni trusted di gestire male un segreto dopo il passaggio di controllo.
- Verifica formale di OpenPGP/GnuPG o delle librerie GUI/runtime di terze parti.

## Punti prioritari per un revisore indipendente

La revisione dovrebbe concentrarsi su `storage/vault.py`, `crypto/gpg_process.py`, `storage/atomic.py`, `storage/inbox.py`, `services/clipboard*.py`, `services/actions.py`, `services/ssh_options.py`, parser di migrazione e tutto il codice che converte input serializzato non fidato in oggetti di dominio. I file bilingui `CODE_REVIEW_MANUAL.md` forniscono indice per righe sorgente e call-map di ogni simbolo eseguibile.

### Confine delle modifiche interattive TUI

M1.18 aggiunge alla TUI Textual i flussi crea/modifica/sposta/elimina. La TUI non scrive direttamente i file del vault: converte lo stato dell'editor tramite il percorso di validazione condiviso `services.entry_editor` e delega persistenza/riorganizzazione a `Vault`. Password e valori TOTP sono plaintext nella memoria dei widget Textual/Python finché l'editor resta aperto; un attaccante same-user capace di leggere la memoria del processo resta fuori dalla garanzia di confidenzialità.
