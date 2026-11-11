# Keys NG 0.2.01 — GUI workspace and readable credential references

## Italiano

- GUI a tre aree ridimensionabili: cartelle, elenco ordinabile a colonne, dettagli.
- Ricerca nel vault o nella cartella selezionata, conteggio risultati, righe compatte opzionali.
- Dimensioni dei pannelli, ordine/larghezza/ordinamento delle colonne e densità memorizzati; colori e icone nativi seguono il sistema.
- Azione contestuale Web/SSH/RDP, copia accanto ai campi, menu contestuali per voci/cartelle e spostamento tramite menu o trascinamento sulla cartella.
- Dettagli tecnici e campi avanzati dell'editor richiudibili. Ctrl+N crea, Ctrl+E modifica; doppio clic modifica, Ctrl+O apre/connetti. Scorciatoie precedenti conservate.
- Riferimenti username/password leggibili con titolo, percorso e campo di origine; catene visibili e UUID nel tooltip. Errori distinti per origine mancante, non leggibile/verificabile, campo vuoto, ciclo e riferimento non valido.
- “Apri voce di origine” seleziona l'origine nel pannello principale; dall'editor apre un'anteprima in sola lettura preservando la bozza. Le password non vengono rivelate dalla descrizione del riferimento.
- Il blocco cancella dettagli, riferimenti, appunti ed editor aperti. Nessuna modifica al formato del vault.
- Notifiche di copia password/TOTP con tempo di cancellazione dagli appunti. Note e titoli trattati come testo, non HTML.
- Correzione di una sintassi preesistente della guida GUI non compatibile con Python 3.11.

## English

- Resizable folder/list/detail workspace with sortable columns, vault/folder search, result count and optional compact rows.
- Persisted splitter/header state and density; native system palette/icons, contextual Web/SSH/RDP actions, field-adjacent copy controls and entry/folder context menus.
- Collapsible technical/editor fields; Ctrl+N creates and Ctrl+E edits, double-click edits, Ctrl+O launches. Existing shortcuts retained.
- Readable reference chains show source titles, folders and fields, with UUID tooltips and explicit missing/unreadable/empty/cycle/invalid errors.
- Source navigation from details; read-only source preview from the editor preserves unsaved changes. Reference descriptions never expose resolved passwords.
- Lock clears details, reference metadata, clipboard and open editors. No vault format changes.
- Password/TOTP copy feedback, plain-text notes/titles and a pre-existing Python 3.11 syntax fix.

## Installation and validation

The release/tag uses **0.2.01** as requested. Python packaging normalizes it to
**0.2.1**, hence `keys_ng-0.2.1-py3-none-any.whl` and `keys_ng-0.2.1.tar.gz`.

```sh
python -m pip install --upgrade 'keys_ng-0.2.1-py3-none-any.whl[gui,tui]'
```

Publication is gated by regression/security checks and clean-wheel GUI/OpenPGP
smokes on Linux, Python 3.11 and 3.12. GUI smoke uses synthetic test records;
OpenPGP smoke uses a disposable real GnuPG keyring. See
`docs/en/GUI_0.2.01_VALIDATION.md` / `docs/it/GUI_0.2.01_VALIDATION.md`.
Native Windows/macOS packaging, interactive pinentry, external RDP/SSH clients,
and independent security review still require platform/manual validation.
