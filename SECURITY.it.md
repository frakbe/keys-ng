# Modello di sicurezza (bozza di sviluppo)

Keys NG è software sensibile dal punto di vista della sicurezza. La versione `0.1.7.dev0` è ancora una base di sviluppo e non è consigliata come unico archivio delle password.

## Invarianti di progetto

- Le credenziali decifrate non vengono intenzionalmente scritte su file persistenti.
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
- Backend GPGME e token hardware richiedono ulteriori test di packaging e integrazione.
- È necessario un audit di sicurezza esterno prima di una release stabile.

## Segnalazione di problemi

Non inserire mai in bug report credenziali reali, chiavi private, seed TOTP o dati decifrati del vault.

## Confine di autorizzazione Inbox (M1.19.2)

Una firma OpenPGP crittograficamente valida è necessaria ma non sufficiente per l'importazione firmata dalla Inbox. Il fingerprint della chiave primaria del firmatario deve essere presente in `trusted_signers` del vault di destinazione. L'ownertrust di GnuPG non viene considerato autorizzazione del vault. Le signing subkey vengono normalizzate al fingerprint primario quando GnuPG lo fornisce tramite `VALIDSIG`. L'import unsigned resta un'azione eccezionale esplicita; le firme non valide vengono rifiutate. Le importazioni riuscite vengono ricifrate e firmate secondo la policy del vault di destinazione prima di eliminare il file sorgente dalla Inbox.
