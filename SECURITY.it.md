# Modello di sicurezza (bozza di sviluppo)

Keys NG è software sensibile dal punto di vista della sicurezza. La versione `0.2.2` è una alpha utilizzabile in attesa di revisione indipendente e non è consigliata come unico archivio delle password.

## Invarianti di progetto

- Le normali operazioni sul vault non scrivono record decifrati su file persistenti. Le esportazioni esplicite in chiaro sono un’eccezione e devono essere protette dall’utente.
- Python non richiede, memorizza o inoltra la passphrase della chiave privata: GnuPG delega l'operazione a `gpg-agent`/Pinentry.
- Le operazioni crittografiche e la migrazione legacy non usano `shell=True`.
- Ogni credenziale è un ciphertext OpenPGP indipendente.
- I metadati di ricerca sono contenuti in un catalogo cifrato e ricostruibile.
- Catalogo decifrato e metadati delle cartelle possono restare in RAM soltanto mentre il vault è sbloccato; lock e hard-lock eliminano queste cache.
- Password e seed TOTP non entrano mai nel catalogo di ricerca.
- I file temporanei persistenti usati per scritture atomiche contengono esclusivamente ciphertext.
- I record Bash legacy vengono analizzati come dati e non vengono mai importati tramite `source` o eseguiti.
- Nei vault firmati vengono rifiutate firme mancanti, non valide o non autorizzate.

## Limiti noti prima di una release stabile

- Python non può garantire l'azzeramento deterministico degli oggetti segreti immutabili in memoria.
- Un clipboard manager esterno può conservare una copia anche dopo la cancellazione della clipboard attiva da parte di Keys NG.
- La protezione completa contro rollback richiede ulteriore progettazione oltre alle normali firme OpenPGP.
- La gestione dei conflitti cloud con più writer non è ancora completa.
- L'auto-type specifico per piattaforma non è ancora implementato.
- L’adattatore GPGME è disabilitato in questa build; il backend supportato invoca GnuPG. I token hardware richiedono ancora test sulle piattaforme.
- È necessario un audit di sicurezza esterno prima di una release stabile.

## Segnalazione di problemi

Non inserire mai in bug report credenziali reali, chiavi private, seed TOTP o dati decifrati del vault.

## Confine di autorizzazione Inbox (M1.19.2)

Una firma OpenPGP crittograficamente valida è necessaria ma non sufficiente per l'importazione firmata dalla Inbox. Il fingerprint della chiave primaria del firmatario deve essere presente in `trusted_signers` del vault di destinazione. L'ownertrust di GnuPG non viene considerato autorizzazione del vault. Le signing subkey vengono normalizzate al fingerprint primario quando GnuPG lo fornisce tramite `VALIDSIG`. L'import unsigned resta un'azione eccezionale esplicita; le firme non valide vengono rifiutate. Le importazioni riuscite vengono ricifrate e firmate secondo la policy del vault di destinazione prima di eliminare il file sorgente dalla Inbox.

## Archiviazione, tag ed eliminazione (0.2.2)

I record sono vincolati a UUID, SHA-256 del ciphertext e revisione nel catalogo:
questo rileva la sostituzione del singolo record, non il rollback di un intero
vault firmato. Trash è una cartella cifrata e conserva UUID e segreti originali.
Non è un confine di isolamento: riferimenti e letture esplicite restano possibili.
L’eliminazione definitiva rimuove il ciphertext e aggiorna il catalogo; non è una
cancellazione sicura di backup o snapshot. Gli aggiornamenti di più file non sono
un’unica transazione: dopo scritture interrotte usare i controlli di integrità del
catalogo e una ricostruzione dell’indice preceduta da verifica.

I tag restano nei record cifrati e, con privacy `standard`/`full`, nel catalogo
cifrato. `minimal` li esclude dal catalogo; i suggerimenti dell’editor leggono i
record solo a vault sbloccato. Non viene creato un database separato di tag in chiaro.

## Riferimenti per revisione e implementazione

- [Checklist di sicurezza della release](docs/it/RELEASE_SECURITY_CHECKLIST.md)
- [Review di sicurezza esterna](docs/it/EXTERNAL_SECURITY_REVIEW.md)
- [Manuale di revisione del codice 0.2.2](docs/it/CODE_REVIEW_MANUAL.md)
- [Implementazione del vault](src/keys_ng/storage/vault.py)
- [Agente GnuPG e opzioni della cache](https://www.gnupg.org/documentation/manuals/gnupg/Agent-Options.html)
- [Modello di fiducia GnuPG](https://www.gnupg.org/documentation/manuals/gnupg/GPG-Configuration-Options.html)
- [Sicurezza subprocess di Python](https://docs.python.org/3/library/subprocess.html#security-considerations)
