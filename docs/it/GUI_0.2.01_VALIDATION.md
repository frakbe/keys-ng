# Validazione GUI 0.2.01

## Controlli obbligatori di rilascio

Il workflow `Release 0.2.01` verifica il ramo `release/0.2.01` e il commit finale
`Release 0.2.01` su main. Python 3.11 e 3.12 devono superare tutti i controlli prima
che il job di pubblicazione crei il tag `v0.2.01` e carichi wheel, archivio sorgenti
e checksum SHA-256. Il ramo di preparazione non pubblica release.

```sh
python -m pytest -q
python tools/security_static_check.py
python -m build
python -m venv .release-venv
.release-venv/bin/python -m pip install 'dist/keys_ng-0.2.1-py3-none-any.whl[gui,tui]'
.release-venv/bin/keys-ng --version
.release-venv/bin/keys-ng-tui version
QT_QPA_PLATFORM=offscreen .release-venv/bin/python tools/smoke_gui.py
.release-venv/bin/python tools/smoke_gpg.py
```

Lo smoke GUI usa widget Qt reali e voci sintetiche: ricerca per cartella/vault,
selezione, origine dei riferimenti, scadenza appunti, navigazione, anteprima senza
perdita della bozza, svuotamento editor al blocco, modifica e salvataggio,
spostamento, riferimenti incrociati protetti, layout persistente, blocco indipendente
e globale multi-vault. Non avvia client SSH/RDP. Lo smoke GnuPG usa un portachiavi
temporaneo isolato per verificare firma/cifratura, riferimenti, blocco/sblocco e
riapertura, senza usare le chiavi dell'utente. Agent e chiavi temporanei vengono
rimossi al termine.

Preparazione locale: 181 test di regressione e controllo statico di sicurezza
superati; smoke GUI offscreen superato su Linux/Python 3.12. GnuPG reale non è
eseguibile localmente perché l'ambiente vieta i socket dell'agent (`Operation not
permitted`). La verifica crittografica reale e Python 3.11 sono obbligatorie su
GitHub Actions: consultare l'esecuzione per il risultato finale. Non si dichiara
un controllo Ruff completo senza rilievi: il modulo GUI ha segnalazioni pregresse;
i nuovi moduli dei riferimenti superano il controllo mirato.

## Checklist desktop ancora manuale

- [ ] Linux Wayland/X11: appunti nativi, scadenza, pinentry e HiDPI.
- [ ] Windows/macOS: avvio, scala 100–200%, tema chiaro/scuro, tastiera,
      ripristino pannelli/colonne e pacchetti nativi.
- [ ] Trascinamento di voci/cartelle annidate e verifica dopo riapertura.
- [ ] Editor italiano con nomi, percorsi e catene di riferimenti lunghi.
- [ ] Avvio dei client SSH/RDP e browser configurati con account di prova.
- [ ] Origini non disponibili/non attendibili e richieste reali dell'agent.
- [ ] Review indipendente di sicurezza, non sostituita da questo rilascio.
