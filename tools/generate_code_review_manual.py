#!/usr/bin/env python3
"""Generate the bilingual, exhaustive Keys NG code-review manual.

The manual is intentionally source-derived. Every Python class and function in
``src/keys_ng`` receives a stable marker, signature, source range, direct-call
inventory, explicit raises, control-flow counts and security-effect hints.  The
corresponding regression test fails if a symbol is added without regenerating
these manuals.
"""
from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "keys_ng"

MODULE_PURPOSE = {
    "keys_ng.cli.main": ("Command-line parser and dispatcher for all CLI workflows.", "Parser e dispatcher della riga di comando per tutti i flussi CLI."),
    "keys_ng.crypto.backend": ("Cryptographic backend contracts and immutable result/key records.", "Contratti dei backend crittografici e record immutabili per risultati e chiavi."),
    "keys_ng.crypto.factory": ("Selects the configured cryptographic backend.", "Seleziona il backend crittografico configurato."),
    "keys_ng.crypto.discovery": ("Cross-platform GnuPG executable discovery, including Windows Gpg4win/GnuPG installations.", "Rilevamento multipiattaforma degli eseguibili GnuPG, incluse le installazioni Gpg4win/GnuPG su Windows."),
    "keys_ng.crypto.gpg_process": ("GnuPG subprocess backend; all data crosses pipes and no shell is used.", "Backend GnuPG a sottoprocesso; i dati passano via pipe e non viene usata una shell."),
    "keys_ng.crypto.gpgme_backend": ("Reserved module for a future GPGME backend; currently contains no executable symbols.", "Modulo riservato a un futuro backend GPGME; attualmente non contiene simboli eseguibili."),
    "keys_ng.errors": ("Project exception hierarchy.", "Gerarchia delle eccezioni del progetto."),
    "keys_ng.gui.main": ("PySide6 desktop GUI, including dialogs, per-vault panes, menus and multi-vault orchestration.", "GUI desktop PySide6, inclusi dialoghi, pannelli per vault, menu e orchestrazione multi-vault."),
    "keys_ng.i18n.manager": ("gettext language discovery and translation helpers.", "Rilevamento lingua gettext e helper di traduzione."),
    "keys_ng.migration.keepassxc": ("KeePassXC XML/KDBX import, UUID mapping and reference-safe validation.", "Import XML/KDBX KeePassXC, mappatura UUID e validazione sicura dei riferimenti."),
    "keys_ng.migration.keepassxc_export": ("KeePass-compatible XML export for one entry or an entire vault.", "Esportazione XML compatibile KeePass per una voce o per l'intero vault."),
    "keys_ng.migration.legacy_parser": ("Non-executing parser for legacy Bash record syntax.", "Parser non esecutivo per la sintassi dei record Bash legacy."),
    "keys_ng.migration.migrator": ("Converts a legacy filesystem tree into encrypted Keys NG entries/folders.", "Converte un albero filesystem legacy in voci/cartelle cifrate Keys NG."),
    "keys_ng.models": ("Validated in-memory and JSON-serializable domain model.", "Modello di dominio validato in memoria e serializzabile JSON."),
    "keys_ng.platform.app_identity": ("Desktop/process identity and application icon integration.", "Identità desktop/processo e integrazione dell'icona applicativa."),
    "keys_ng.platform.desktop_integration": ("Per-user desktop launcher installation/status/removal.", "Installazione/stato/rimozione del launcher desktop per utente."),
    "keys_ng.platform.host": ("Flatpak host-command bridge and executable resolution.", "Bridge Flatpak verso comandi host e risoluzione degli eseguibili."),
    "keys_ng.platform.paths": ("Cross-platform application config/data paths.", "Percorsi multipiattaforma per configurazione e dati applicativi."),
    "keys_ng.services.actions": ("Launches URL, SSH, RDP and argv-based command actions without a shell.", "Avvia azioni URL, SSH, RDP e comandi basati su argv senza shell."),
    "keys_ng.services.clipboard": ("Secret clipboard backends, ownership checking and timed clearing.", "Backend clipboard per segreti, verifica della proprietà e cancellazione temporizzata."),
    "keys_ng.services.clipboard_helper": ("Detached helper process used by terminal clipboard operations.", "Processo helper distaccato usato dalle operazioni clipboard da terminale."),
    "keys_ng.services.doctor": ("Runtime/environment diagnostics.", "Diagnostica dell'ambiente e del runtime."),
    "keys_ng.services.diagnostics": ("Opt-in rotating diagnostic logging with privacy-preserving operation/timing summaries.", "Logging diagnostico rotante opt-in con riepiloghi di operazioni e tempi che preservano la privacy."),
    "keys_ng.services.vault_sessions": ("Multi-vault session state for interactive frontends, preserving one Vault object and lock/cache state per open vault.", "Stato di sessione multi-vault per i frontend interattivi, mantenendo un oggetto Vault e lo stato lock/cache per ogni vault aperto."),
    "keys_ng.services.entry_editor": ("Frontend-neutral credential editor draft and validation shared by GUI and TUI.", "Bozza e validazione dell'editor credenziali indipendenti dal frontend, condivise da GUI e TUI."),
    "keys_ng.services.passwords": ("Cryptographically secure password generation.", "Generazione crittograficamente sicura di password."),
    "keys_ng.services.qr": ("QR decoding and conversion to TOTP configuration.", "Decodifica QR e conversione in configurazione TOTP."),
    "keys_ng.services.references": ("KeePassXC-style UUID reference parsing and construction.", "Parsing e costruzione dei riferimenti UUID in stile KeePassXC."),
    "keys_ng.services.ssh_options": ("Parses and validates advanced OpenSSH argv options.", "Analizza e valida opzioni argv avanzate di OpenSSH."),
    "keys_ng.services.totp": ("RFC-style TOTP generation and otpauth URI parsing/building.", "Generazione TOTP e parsing/costruzione di URI otpauth."),
    "keys_ng.services.ui_capabilities": ("Declares the interactive GUI/TUI parity contract.", "Dichiara il contratto di parità interattiva GUI/TUI."),
    "keys_ng.services.trusted_signers": ("Per-vault authorization list for cryptographically valid Inbox signers.", "Lista di autorizzazione per-vault dei firmatari Inbox crittograficamente validi."),
    "keys_ng.services.vault_init": ("Shared vault-creation validation, key selection and pre-write cryptographic self-test.", "Validazione condivisa della creazione vault, selezione chiavi e self-test crittografico prima della scrittura."),
    "keys_ng.storage.atomic": ("Crash-resistant ciphertext-only atomic file replacement and stale-temp cleanup.", "Sostituzione atomica crash-resistant di soli ciphertext e pulizia dei temporanei residui."),
    "keys_ng.storage.config": ("Cleartext vault policy/configuration file model.", "Modello del file di policy/configurazione in chiaro del vault."),
    "keys_ng.storage.inbox": ("Public-key-only deposit and controlled inbox import.", "Deposito con sola chiave pubblica e import controllato dell'inbox."),
    "keys_ng.storage.settings": ("Per-user TOML application settings.", "Impostazioni applicative TOML per utente."),
    "keys_ng.storage.vault": ("Central vault service: encryption, signatures, catalog, records, folders, references and integrity binding.", "Servizio centrale del vault: cifratura, firme, catalogo, record, cartelle, riferimenti e binding d'integrità."),
    "keys_ng.tui.main": ("Textual terminal UI and its actions/bindings.", "Interfaccia terminale Textual e relative azioni/scorciatoie."),
}

CLASS_PURPOSE = {
    "Vault": ("Owns one vault instance and enforces its storage/security policy.", "Rappresenta un singolo vault e ne applica la policy di storage/sicurezza."),
    "Entry": ("Credential record persisted inside one encrypted record file.", "Record di credenziale persistito in un singolo file cifrato."),
    "Catalog": ("Encrypted searchable metadata snapshot; rebuildable from records.", "Snapshot cifrato dei metadati ricercabili; ricostruibile dai record."),
    "CatalogItem": ("One catalog row derived from an Entry and its ciphertext hash.", "Una riga del catalogo derivata da una Entry e dall'hash del ciphertext."),
    "FolderStore": ("Encrypted logical folder tree.", "Albero cifrato delle cartelle logiche."),
    "Folder": ("Logical folder node identified by UUID.", "Nodo di cartella logica identificato da UUID."),
    "Action": ("Validated external action attached to an entry.", "Azione esterna validata associata a una voce."),
    "TotpConfig": ("Validated TOTP seed and algorithm parameters.", "Seed TOTP validato e parametri dell'algoritmo."),
    "GPGProcessBackend": ("Concrete CryptoBackend implemented by invoking GnuPG safely via argv/pipes.", "CryptoBackend concreto implementato invocando GnuPG in sicurezza via argv/pipe."),
    "CryptoBackend": ("Abstract interface isolating vault logic from crypto implementation.", "Interfaccia astratta che isola la logica del vault dall'implementazione crittografica."),
    "VaultPane": ("GUI state and widgets for exactly one independently locked vault tab.", "Stato e widget GUI per una singola scheda vault con lock indipendente."),
    "MainWindow": ("Top-level GUI window coordinating multiple VaultPane instances.", "Finestra GUI principale che coordina più istanze VaultPane."),
    "KeysApp": ("Top-level Textual application for one vault.", "Applicazione Textual principale per un vault."),
    "AppSettings": ("Validated application preferences loaded from/saved to TOML.", "Preferenze applicative validate caricate/salvate in TOML."),
}


def module_name(path: Path) -> str:
    rel = path.relative_to(ROOT / "src").with_suffix("")
    return ".".join(rel.parts)


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = dotted_name(node.value)
        return f"{left}.{node.attr}" if left else node.attr
    return None


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = ast.unparse(node.args)
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"{prefix} {node.name}({args}){ret}"


def symbol_facts(node: ast.AST) -> dict:
    calls = []
    raises = []
    writes = []
    counts = Counter()
    for child in ast.walk(node):
        if child is node:
            continue
        counts[type(child).__name__] += 1
        if isinstance(child, ast.Call):
            name = dotted_name(child.func)
            if name:
                calls.append(name)
        elif isinstance(child, ast.Raise) and child.exc is not None:
            if isinstance(child.exc, ast.Call):
                name = dotted_name(child.exc.func)
                if name:
                    raises.append(name)
            else:
                name = dotted_name(child.exc)
                if name:
                    raises.append(name)
        elif isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = child.targets if isinstance(child, ast.Assign) else [child.target]
            for target in targets:
                if isinstance(target, ast.Attribute):
                    name = dotted_name(target)
                    if name:
                        writes.append(name)
    return {
        "calls": sorted(set(calls)),
        "raises": sorted(set(raises)),
        "writes": sorted(set(writes)),
        "ifs": counts["If"],
        "loops": counts["For"] + counts["While"],
        "tries": counts["Try"],
        "withs": counts["With"] + counts["AsyncWith"],
        "returns": counts["Return"],
    }


def security_effects(calls: list[str]) -> list[str]:
    joined = " ".join(calls).lower()
    effects=[]
    tests=[
        (("subprocess", "popen", "_run"), "process"),
        (("read_text", "read_bytes", "write_text", "write_bytes", "open", "unlink", "replace", "chmod", "mkdir"), "filesystem"),
        (("encrypt", "decrypt", "hard_lock"), "cryptography/key-agent"),
        (("clipboard", "mime", "wl-copy", "xclip", "xsel"), "clipboard"),
        (("webbrowser",), "desktop URL launcher"),
        (("tomllib", "json.", "et."), "parser/serialization"),
    ]
    for needles,label in tests:
        if any(n in joined for n in needles): effects.append(label)
    return effects


def purpose_for(name: str, kind: str, lang: str, doc: str | None) -> str:
    if doc:
        first=" ".join(doc.strip().split())
        return first
    if kind == "class" and name in CLASS_PURPOSE:
        return CLASS_PURPOSE[name][0 if lang=="en" else 1]
    patterns_en = {
        "load_": "Loads and validates ", "save": "Validates and persists state for ", "create_": "Creates ",
        "delete_": "Deletes ", "copy_": "Copies a value using ", "parse_": "Parses and validates ",
        "build_": "Builds ", "resolve_": "Resolves ", "import_": "Imports ", "export_": "Exports ",
        "launch_": "Validates and launches ", "validate": "Validates the invariants of ", "to_": "Serializes/converts ",
        "from_": "Deserializes/constructs ", "list_": "Returns a filtered/listed view of ", "get_": "Retrieves ",
        "_": "Internal helper implementing ",
    }
    patterns_it = {
        "load_": "Carica e valida ", "save": "Valida e persiste lo stato per ", "create_": "Crea ",
        "delete_": "Elimina ", "copy_": "Copia un valore usando ", "parse_": "Analizza e valida ",
        "build_": "Costruisce ", "resolve_": "Risolve ", "import_": "Importa ", "export_": "Esporta ",
        "launch_": "Valida e avvia ", "validate": "Valida gli invarianti di ", "to_": "Serializza/converte ",
        "from_": "Deserializza/costruisce ", "list_": "Restituisce una vista filtrata/elencata di ", "get_": "Recupera ",
        "_": "Helper interno che implementa ",
    }
    pats=patterns_en if lang=="en" else patterns_it
    for pre,text in pats.items():
        if name.startswith(pre): return text+f"`{name}`."
    return (f"Implements the `{name}` operation in this module." if lang=="en" else f"Implementa l'operazione `{name}` in questo modulo.")


def collect_symbols(path: Path):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    out=[]
    def walk(body, parent=""):
        for node in body:
            if isinstance(node, ast.ClassDef):
                q=f"{parent}.{node.name}" if parent else node.name
                out.append((q,"class",node))
                walk(node.body,q)
            elif isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                q=f"{parent}.{node.name}" if parent else node.name
                out.append((q,"function",node))
                # Nested helper functions are executable code and are documented too.
                walk(node.body,q)
    walk(tree.body)
    return tree,out


def render(lang: str) -> str:
    en=lang=="en"
    title = "Keys NG M1.20.4 — Complete Code Review Manual" if en else "Keys NG M1.20.4 — Manuale completo per la revisione del codice"
    lines=[f"# {title}", "", ("Version: `0.1.20.dev4`. This document is generated from the exact Python source tree shipped with M1.20.4." if en else "Versione: `0.1.20.dev4`. Questo documento è generato dall'esatto albero sorgente Python distribuito con M1.20.4."), ""]
    lines += ["## " + ("Purpose and reading method" if en else "Scopo e metodo di lettura"), "",
        ("This manual is a reviewer-oriented map, not a substitute for reading the source. It documents every Python class and function (including nested helpers) with its signature, source range, direct calls, explicit exceptions, state writes, control-flow shape and security-relevant effects. Stable `symbol:` markers are machine-checked by the test suite so undocumented executable symbols cannot silently enter the release." if en else "Questo manuale è una mappa orientata al revisore, non sostituisce la lettura del sorgente. Documenta ogni classe e funzione Python (inclusi gli helper annidati) con firma, intervallo di righe, chiamate dirette, eccezioni esplicite, scritture di stato, forma del flusso di controllo ed effetti rilevanti per la sicurezza. I marker stabili `symbol:` sono verificati automaticamente dai test, così nessun simbolo eseguibile non documentato può entrare silenziosamente nella release."), ""]
    lines += ["## " + ("Architecture and trust boundaries" if en else "Architettura e confini di fiducia"), ""]
    architecture = [
        ("`models` contains validated plaintext domain objects. Plaintext exists in Python memory only while needed.", "`models` contiene gli oggetti di dominio plaintext validati. Il plaintext esiste nella memoria Python solo quando necessario."),
        ("`storage.vault` is the central policy boundary. It encrypts before persistence, verifies signatures after decryption, binds records to the signed catalog, and clears decrypted metadata caches on lock.", "`storage.vault` è il confine centrale di policy. Cifra prima della persistenza, verifica le firme dopo la decifratura, collega i record al catalogo firmato e svuota le cache di metadati decifrati al lock."),
        ("`crypto` delegates private-key passphrase handling to GnuPG/gpg-agent/pinentry; Keys NG never requests that passphrase.", "`crypto` delega la passphrase della chiave privata a GnuPG/gpg-agent/pinentry; Keys NG non richiede mai tale passphrase."),
        ("Persistent credential data is per-record OpenPGP ciphertext. `catalog.gpg` and `folders.gpg` are also encrypted and signed. `vault.json` is intentionally cleartext policy metadata and must not contain credentials.", "I dati persistenti delle credenziali sono ciphertext OpenPGP per-record. Anche `catalog.gpg` e `folders.gpg` sono cifrati e firmati. `vault.json` è intenzionalmente metadata di policy in chiaro e non deve contenere credenziali."),
        ("External actions are argv-based and use `shell=False`. Advanced SSH options remain a trusted-record boundary because OpenSSH itself can execute commands through options such as ProxyCommand/LocalCommand.", "Le azioni esterne sono basate su argv e usano `shell=False`. Le opzioni SSH avanzate restano un confine di fiducia del record perché OpenSSH stesso può eseguire comandi tramite opzioni come ProxyCommand/LocalCommand."),
        ("The encrypted catalog detects single-record replacement/rollback through ciphertext SHA-256 plus revision. Coordinated rollback of both record and catalog remains a documented residual risk.", "Il catalogo cifrato rileva sostituzione/rollback di un singolo record tramite SHA-256 del ciphertext più revisione. Il rollback coordinato di record e catalogo resta un rischio residuo documentato."),
    ]
    for a,b in architecture: lines += [f"- {a if en else b}"]
    lines += ["", "## " + ("Primary execution flows" if en else "Flussi di esecuzione principali"), "",
        "```text",
        "CLI/TUI/GUI -> Vault -> CryptoBackend -> GnuPG -> gpg-agent/pinentry",
        "                    |",
        "                    +-> records/<uuid>.gpg",
        "                    +-> catalog.gpg",
        "                    +-> folders.gpg",
        "public-key contributor -> inbox/<random>.gpg -> explicit import -> Vault.save_entry()",
        "```", ""]
    lines += ["## " + ("Module-by-module exhaustive reference" if en else "Riferimento esaustivo modulo per modulo"), ""]

    total=0
    for path in sorted(SRC.rglob("*.py")):
        mod=module_name(path)
        tree,symbols=collect_symbols(path)
        if not symbols and path.name=="__init__.py":
            continue
        total += len(symbols)
        lines += [f"### `{mod}`", "", MODULE_PURPOSE.get(mod,("Source module.","Modulo sorgente."))[0 if en else 1], "", f"**{'Source' if en else 'Sorgente'}:** `{path.relative_to(ROOT)}`  ", f"**{'Executable symbols' if en else 'Simboli eseguibili'}:** {len(symbols)}", ""]
        imports=[]
        for n in tree.body:
            if isinstance(n,ast.Import): imports += [a.name for a in n.names]
            if isinstance(n,ast.ImportFrom): imports.append(n.module or "")
        if imports:
            lines += [f"**{'Direct module dependencies' if en else 'Dipendenze dirette del modulo'}:** " + ", ".join(f"`{x}`" for x in sorted(set(imports))), ""]
        for q,kind,node in symbols:
            marker=f"{mod}:{q}"
            lines += [f"<!-- symbol:{marker} -->", f"#### `{q}`", ""]
            doc=ast.get_docstring(node,clean=True)
            if kind=="class":
                desc=purpose_for(node.name,"class",lang,doc)
                bases=[ast.unparse(b) for b in node.bases]
                methods=[n.name for n in node.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
                fields=[n.target.id for n in node.body if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name)]
                lines += [f"**{'Kind' if en else 'Tipo'}:** {'class' if en else 'classe'}  ", f"**{'Lines' if en else 'Righe'}:** {node.lineno}-{getattr(node,'end_lineno',node.lineno)}  "]
                if bases: lines += [f"**{'Bases' if en else 'Basi'}:** " + ", ".join(f"`{x}`" for x in bases)+"  "]
                if fields: lines += [f"**{'Declared fields' if en else 'Campi dichiarati'}:** " + ", ".join(f"`{x}`" for x in fields)+"  "]
                if methods: lines += [f"**{'Methods' if en else 'Metodi'}:** " + ", ".join(f"`{x}`" for x in methods)+"  "]
                lines += [f"**{'Responsibility' if en else 'Responsabilità'}:** {desc}", ""]
            else:
                facts=symbol_facts(node)
                effects=security_effects(facts['calls'])
                lines += [f"**{'Kind' if en else 'Tipo'}:** {'function/method' if en else 'funzione/metodo'}  ", f"**{'Lines' if en else 'Righe'}:** {node.lineno}-{getattr(node,'end_lineno',node.lineno)}  ", f"**{'Signature' if en else 'Firma'}:** `{signature(node)}`  ", f"**{'Purpose' if en else 'Scopo'}:** {purpose_for(node.name,'function',lang,doc)}", ""]
                if facts['calls']:
                    lines += [f"**{'Direct calls observed in the function body' if en else 'Chiamate dirette osservate nel corpo'}:** " + ", ".join(f"`{x}`" for x in facts['calls']) + ".", ""]
                if facts['raises']:
                    lines += [f"**{'Explicitly raised exceptions' if en else 'Eccezioni sollevate esplicitamente'}:** " + ", ".join(f"`{x}`" for x in facts['raises']) + ".", ""]
                if facts['writes']:
                    lines += [f"**{'Object attributes written' if en else 'Attributi oggetto modificati'}:** " + ", ".join(f"`{x}`" for x in facts['writes']) + ".", ""]
                cf=(f"{facts['ifs']} conditional blocks, {facts['loops']} loops, {facts['tries']} try blocks, {facts['withs']} context managers, {facts['returns']} explicit returns" if en else f"{facts['ifs']} blocchi condizionali, {facts['loops']} cicli, {facts['tries']} blocchi try, {facts['withs']} context manager, {facts['returns']} return espliciti")
                lines += [f"**{'Control-flow shape' if en else 'Forma del flusso di controllo'}:** {cf}.", ""]
                if effects:
                    lines += [f"**{'Security-relevant effect categories' if en else 'Categorie di effetti rilevanti per la sicurezza'}:** " + ", ".join(effects) + ".", ""]
                review=("Review the listed direct calls together with validation before them and cleanup/error handling after them; source line numbers above are normative." if en else "Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.")
                lines += [f"**{'Reviewer note' if en else 'Nota per il revisore'}:** {review}", ""]
    lines += ["## " + ("Coverage guarantee" if en else "Garanzia di copertura"), "", (f"This edition documents **{total}** class/function symbols discovered by AST traversal. `tests/test_code_review_manual_coverage.py` independently traverses the release source and requires one marker for every symbol in both language editions." if en else f"Questa edizione documenta **{total}** simboli classe/funzione rilevati tramite attraversamento AST. `tests/test_code_review_manual_coverage.py` attraversa indipendentemente il sorgente della release e richiede un marker per ogni simbolo in entrambe le edizioni linguistiche."), "",
        ("Generated fields such as direct calls and control-flow counts are descriptive static-analysis aids; they do not prove security. The reviewer must inspect the referenced source and the separate threat model/security review." if en else "I campi generati, come chiamate dirette e conteggi del flusso di controllo, sono ausili descrittivi di analisi statica; non dimostrano la sicurezza. Il revisore deve ispezionare il sorgente referenziato e il threat model/security review separati."), ""]
    return "\n".join(lines)


def main():
    out_en=ROOT/'docs/en/CODE_REVIEW_MANUAL.md'
    out_it=ROOT/'docs/it/CODE_REVIEW_MANUAL.md'
    out_en.write_text(render('en'),encoding='utf-8')
    out_it.write_text(render('it'),encoding='utf-8')
    print(out_en)
    print(out_it)

if __name__=='__main__': main()
