# Comandi TUI di Keys NG

Questa schermata elenca le scorciatoie stabili dell'interfaccia terminale.

## Schermata principale

- `?` — apre questa guida ai comandi.
- `F1` — apre Help / Guida utente / Sicurezza / Licenza.
- `F2` — Preferenze.
- `F3` — Firmatari Inbox attendibili.
- `F4` — copia l'UUID della voce selezionata.
- `F5` — apre un altro vault.
- `F6` — apre un vault recente.
- `Ctrl+J` — apre il selettore dei vault e permette di attivare/chiudere uno dei vault già aperti nella sessione TUI.
- `F7` — importa un database KeePassXC o un file XML.
- `F8` — esporta l'intero vault come XML KeePassXC.
- `F9` — hard lock e cancellazione della cache di gpg-agent.
- `Ctrl+Q` — esce.
- `Ctrl+F` — porta il focus sulla ricerca.
- `N` — crea una nuova voce.
- `Ctrl+D` — crea una nuova cartella.
- `E` — modifica la voce selezionata o rinomina la cartella selezionata.
- `M` — sposta la voce o cartella selezionata.
- `Delete` — elimina la voce o cartella selezionata.
- `Ctrl+U` — copia URL.
- `Ctrl+B` — copia username.
- `Ctrl+C` — copia password quando il focus non è dentro un editor di testo.
- `Ctrl+T` — copia TOTP.
- `Ctrl+N` — copia l'intero campo Note con cancellazione temporizzata della clipboard.
- `Ctrl+O` — esegue/apre l'azione della voce selezionata.
- `X` — esporta la voce selezionata in XML KeePassXC plaintext dopo conferma.
- `Ctrl+W` — chiude il vault corrente; se altri vault sono aperti, diventa attivo il più recente tra quelli rimasti.
- `Ctrl+L` — blocca il vault.
- `Ctrl+P` — sblocca il vault.
- `R` — ricarica l'albero del vault.
- `I` — apre la Inbox.

## Modifica del testo

Quando un Input o TextArea ha il focus, le normali scorciatoie dell'editor hanno precedenza quando applicabile. In particolare `Ctrl+C`, `Ctrl+X` e `Ctrl+V` mantengono il significato normale di copia/taglia/incolla dentro gli editor.

## Generatore di password

- **Genera** crea una nuova password candidata.
- **Copia password generata** copia la candidata senza applicarla alla voce. Quando è disponibile l'helper clipboard nativo, la clipboard viene cancellata secondo il timeout configurato per i segreti.
- **Usa password** applica la candidata all'editor della voce.
- **Annulla** chiude il generatore senza modificare la voce.

## Vault bloccato

L'albero resta visibile dopo il blocco per permettere all'utente di mantenere l'orientamento nel vault. Aprire una voce mentre il vault è bloccato non la decifra: Keys NG chiede di premere `Ctrl+P` per sbloccarlo prima.

## Più vault aperti

`F5` e `F6` aggiungono vault alla sessione TUI corrente invece di sostituire quello attivo. Usa `Ctrl+J` per passare da un vault all'altro. Ogni vault conserva in modo indipendente il proprio stato locked/unlocked. `Ctrl+L` blocca solo il vault attivo; `F9` esegue hard lock di tutti i vault aperti e svuota la cache condivisa di gpg-agent.
