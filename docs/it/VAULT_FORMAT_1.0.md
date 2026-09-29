# Keys NG — Formato Vault 1.0

Stato: **congelato per il ciclo di revisione M1.17**. Il valore dello schema dei modelli serializzati è `1`. Qualunque futura modifica incompatibile deve usare un nuovo valore di schema e un percorso esplicito di migrazione.

## Layout filesystem

```text
vault/
├── vault.json
├── catalog.gpg
├── folders.gpg
├── records/
│   └── <entry-uuid>.gpg
└── inbox/
    └── <deposit-uuid>.gpg
```

Su POSIX M1.17 crea root del vault, `records/` e `inbox/` come `0700`. I file ciphertext/config temporanei/atomici usano modalità di creazione `0600`. I nomi UUID non contengono titoli o username.

## `vault.json`

Policy JSON in chiaro, schema `1`:

- `recipients`: fingerprint OpenPGP usati per la cifratura.
- `signer`: fingerprint di firma o `null`.
- `trusted_signers`: fingerprint accettati in decifratura quando la firma è richiesta.
- `require_signature`: rifiuto di oggetti vault non firmati/non validi/non fidati.
- `catalog_privacy`: `minimal`, `standard` o `full`.
- `schema`: schema configurazione (`1`).

Questo file non deve mai contenere password, seed TOTP o contenuti decifrati delle entry.

## Plaintext del record prima della cifratura OpenPGP

JSON UTF-8 canonico prodotto con chiavi ordinate e separatori compatti. Campi:

- `schema`: `1`.
- `id`: UUID; all'apertura tramite vault deve corrispondere all'UUID del nome file.
- `title`: titolo non vuoto.
- `kind`: tipo descrittivo usato da UI/importer.
- `usernames`: lista di stringhe.
- `password`: stringa o `null`; può essere un riferimento UUID sull'intero campo.
- `totp`: lista di oggetti TOTP (`secret`, `issuer`, `account_name`, `algorithm`, `digits`, `period`).
- `actions`: lista di azioni validate (`url`, `ssh`, `rdp`, `command`).
- `tags`: lista di stringhe.
- `notes`: stringa.
- `custom_fields`: mappa stringa-stringa.
- `folder_id`: UUID o `null`.
- `revision`: intero positivo.
- `created_at`, `updated_at`: timestamp UTC prodotti da Keys NG.

Ogni record è cifrato indipendentemente ai recipient configurati e normalmente firmato dal signer configurato.

## Plaintext delle cartelle

`folders.gpg` cifra JSON con `schema: 1` e lista `folders`. Ogni cartella ha UUID `id`, `name` non vuoto e senza separatori, UUID padre opzionale e timestamp. I parent devono esistere e i cicli sono rifiutati.

## Plaintext del catalogo

`catalog.gpg` cifra uno snapshot JSON ricostruibile contenente `schema: 1`, `items` e uno snapshot di `folders`.

Ogni item contiene UUID, titolo, kind, username/tag/host URL in base alla privacy, capability, revisione entry, SHA-256 del ciphertext e UUID cartella opzionale. Password e seed TOTP non sono mai campi del catalogo.

M1.17 usa `ciphertext_sha256` più `revision` come binding tra record e catalogo firmato. Rileva la sostituzione isolata di un record, ma non è un contatore anti-rollback globale.

## Riferimenti

Forme supportate sull'intero campo:

```text
{REF:U@I:<UUID>}
{REF:P@I:<UUID>}
```

`U` risolve il primo username, `P` la password. La risoluzione è nello stesso vault, ricorsiva, con rilevamento cicli e limite di 32 riferimenti annidati.

## Inbox

I depositi inbox usano lo stesso payload Entry cifrato ma non appartengono al catalogo. Contributor con sola chiave pubblica possono creare depositi non firmati. L'import normale li rifiuta salvo approvazione esplicita `accept_unsigned`; le entry accettate vengono validate e ricifrate/rifirmate secondo la policy del vault.

## Regola di compatibilità

I reader devono rifiutare numeri di schema non supportati anziché tentare interpretazioni. Modifiche additive non rappresentabili in sicurezza da reader vecchi richiedono un bump dello schema. M1.17 non dichiara compatibilità con futuri valori di schema.
