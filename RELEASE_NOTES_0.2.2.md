# Keys NG 0.2.2

## Italiano

- Lista GUI: la colonna **Tag** sostituisce **Nome utente**.
- Editor: selezione multipla dei tag già utilizzati e inserimento di nuovi tag.
- Cartella speciale **Trash** creata automaticamente nei vault nuovi e all’apertura dell’albero/sblocco dei vault esistenti; icona dedicata e protezione da rinomina/spostamento/eliminazione.
- Elimina sposta nel cestino; dal cestino elimina definitivamente. **Svuota cestino**, nel menu contestuale di Trash, elimina tutte le voci dopo conferma. Per recuperare una voce usare lo spostamento verso un’altra cartella.
- Aggiornati modello di sicurezza, riferimenti, guide IT/EN, aiuto integrato e manuali di revisione del codice.

La semantica del cestino è condivisa anche da CLI/TUI. Le liste GUI ordinarie escludono Trash. I riferimenti UUID continuano a funzionare fino alla cancellazione definitiva. Con privacy catalogo `minimal` i tag non vengono mostrati nella lista, ma restano modificabili nell’editor.

## English

- GUI **Tags** column replaces **Username**.
- Editable multi-selection of existing tags, with support for new tags.
- Standard encrypted **Trash** folder, automatic migration on folder-tree open/unlock, dedicated icon and protection against rename/move/delete.
- Delete moves records to Trash; Delete in Trash permanently removes them. **Empty trash** in the Trash context menu purges all entries after confirmation. Restore by moving an entry to another folder.
- Updated bilingual security model, references, guides, bundled help and code review manuals.

Trash semantics also apply to CLI/TUI. Ordinary GUI lists exclude Trash. UUID references remain valid until permanent deletion. Minimal catalog privacy continues to omit tags from list metadata.

## Validation / Validazione

Regression tests, security static checks, installed-wheel GUI smoke and real GnuPG smoke are required by the release workflow on Python 3.11 and 3.12 before publishing wheel, source distribution and SHA-256 checksums. Native Windows/macOS validation and independent security review remain outstanding; this release does not claim either.
