# Keys NG M1.18 — Revisione memoria e vita dei segreti

Keys NG evita intenzionalmente file persistenti in plaintext, ma questo **non** significa che il plaintext non esista mai. La decifratura crea necessariamente plaintext nella memoria del processo.

## Oggetti che possono contenere segreti

- `DecryptionResult.plaintext`: `bytes` Python immutabili restituiti dal backend crypto.
- `Entry.password`: `str` Python dopo il decoding JSON.
- `TotpConfig.secret`: `str` Python.
- Riferimenti UUID risolti: stringhe Python che possono duplicare temporaneamente username/password di un'altra entry.
- Password e codici TOTP generati: stringhe Python.
- Testo dei widget GUI e MIME data clipboard: copie gestite in parte da Qt/servizi di piattaforma.
- stdin dell'helper clipboard CLI: pipe con i byte UTF-8 del segreto finché l'helper non li consuma.

## Aspetti positivi di M1.18

- I record decifrati non sono intenzionalmente scritti su storage persistente.
- Il catalogo cifrato non contiene mai password o seed TOTP.
- Le cache plaintext di catalogo/cartelle sono eliminate da `Vault.lock()`; il servizio core Vault non mantiene una cache globale delle Entry.
- I segreti non vengono intenzionalmente inseriti in argv o variabili d'ambiente nei percorsi clipboard/GnuPG.
- L'helper clipboard riceve il segreto via stdin, non argv.
- Le passphrase GnuPG rimangono fuori da Python.

## Limiti di Python/Qt

Gli oggetti immutabili `str` e `bytes` non possono essere azzerati in-place in modo affidabile. Parsing JSON e assegnazione ai widget possono creare copie ulteriori la cui durata dipende dagli internals di CPython/Qt. Eliminare un riferimento Python o farlo uscire dallo scope non prova che la memoria sottostante sia stata sovrascritta immediatamente.

Per questo M1.18 non dichiara alcuna garanzia `secure_zero()`. Un revisore deve considerare un attaccante same-user capace di leggere memoria fuori dalla garanzia di confidenzialità dopo l'uso recente di un segreto.

## Lavoro futuro raccomandato

- Ridurre conversioni `bytes`/`str` nei percorsi sensibili.
- Evitare cache a lunga vita di Entry contenenti password/TOTP.
- Cancellare immediatamente i widget dettaglio al lock/chiusura tab.
- Valutare un buffer mutabile per segreti solo dove riduca misurabilmente le copie; non dichiarare zeroizzazione garantita senza verifica dell'intero percorso Python/Qt.
- Aggiungere esperimenti sulla memoria di processo per ogni OS supportato, distinguendoli chiaramente dalle garanzie formali.

## Vita dei segreti nell'editor TUI M1.18

La schermata modale `EntryEditorScreen` mantiene username/password/TOTP negli oggetti widget Textual mentre l'editor è visibile. La chiusura della schermata rilascia i riferimenti applicativi, ma Python e Textual non offrono una garanzia verificabile di secure-zero. L'implementazione evita persistenza prima di `Vault.save_entry()` e non inserisce questi segreti negli argomenti della command line; un revisore deve comunque considerare i segreti modificati di recente potenzialmente recuperabili dalla memoria del processo in caso di compromissione same-user con lettura della memoria.
