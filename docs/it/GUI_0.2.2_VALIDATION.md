# Validazione release 0.2.2

Il workflow `.github/workflows/release-0.2.2.yml` esegue regressioni e controlli
statici di sicurezza su Python 3.11 e 3.12, crea i pacchetti, installa il wheel in
un ambiente pulito e verifica CLI/TUI, GUI Qt offscreen e GnuPG reale con un
portachiavi temporaneo. Pubblica da main soltanto se tutta la matrice passa.
Le esecuzioni sul ramo di preparazione non pubblicano la release. I risultati
definitivi della matrice sono disponibili in GitHub Actions.

Preparazione locale Linux/Python 3.12: superati 187 test, controllo statico e
smoke GUI offscreen. L’ambiente locale non riesce ad avviare gpg-agent: la prova
OpenPGP reale è obbligatoria nel workflow prima della pubblicazione. Lo smoke GUI
copre selezione multipla e nuovi tag, persistenza nella lista, spostamento nel
cestino, annullamento, ripristino, cancellazione definitiva, svuotamento annullato
e confermato, riferimenti, scadenza clipboard e blocco vault. I test storage coprono
migrazione, idempotenza, protezione di Trash, sottocartelle, riapertura, integrità
del catalogo e tutti e tre i livelli di privacy.

Restano manuali le verifiche clipboard/Pinentry sui desktop Linux, avvio e
pacchettizzazione Windows/macOS, HiDPI, temi e revisione indipendente della
sicurezza. I test offscreen non sostituiscono queste verifiche.

## Correzione Preferenze successiva alla release (2026-11-23, main)

Il salvataggio delle Preferenze chiamava il metodo inesistente
`VaultPane.reset_auto_lock_timer` dopo aver scritto le impostazioni. Il metodo
condiviso ora applica il timeout a tutti i vault aperti, ferma il timer precedente
quando il valore è zero e mantiene fermi i timer dei vault bloccati. Avvio,
attività, sblocco, blocco normale, hard lock e chiusura seguono la stessa regola.
Annulla non modifica impostazioni o intervalli dei timer.

Lo smoke GUI esteso ha riprodotto l’AttributeError prima della correzione, poi ha
superato le prove con due vault: timer disattivati/attivati, vault bloccato,
annullamento, scadenza reale, sblocco e hard lock. Superati anche tutti i 188 test
e il controllo statico di sicurezza su Linux/Python 3.12. I pacchetti originali
v0.2.2 non includono questa correzione successiva: ricostruire da main aggiornato.
