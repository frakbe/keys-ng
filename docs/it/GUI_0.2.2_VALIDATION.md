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
