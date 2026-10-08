# Generare il Flatpak di Keys NG su Linux

Questa guida descrive il flusso supportato per creare il Flatpak di Keys NG. Il manifest e lo script di supporto si trovano in packaging/flatpak/.

## 1. Struttura del pacchetto

Il Flatpak usa KDE Platform 6.11 e io.qt.PySide.BaseApp. Il pacchetto contiene GUI, TUI e CLI. La GUI è il comando predefinito; TUI e CLI si avviano esplicitamente con l'opzione `--command`.

Keys NG delega intenzionalmente GnuPG, SSH e RDP al sistema host tramite flatpak-spawn --host. L'host deve fornire GnuPG/gpg-agent, pinentry, il terminale/client SSH e il client RDP configurati.

## 2. Prerequisiti

Su Debian o Ubuntu:

    sudo apt install flatpak flatpak-builder git python3 python3-venv

Su Fedora:

    sudo dnf install flatpak flatpak-builder git python3

Aggiungi Flathub e installa runtime e SDK KDE:

    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    flatpak install flathub org.kde.Sdk//6.11 org.kde.Platform//6.11

Verifica che siano disponibili flatpak, flatpak-builder, Python 3 e git. I nomi dei pacchetti possono variare tra distribuzioni.

## 3. Generare i sorgenti delle dipendenze Python

Il manifest richiede packaging/flatpak/python3-flatpak-requirements.json. Generarlo da requirements.txt prima della prima build.

Lo strumento `flatpak-pip-generator` richiede il pacchetto Python `requirements-parser`. Sono supportate due modalità alternative.

### Modalità A: installazione nel Python utente

Usa questa modalità se la distribuzione consente l'installazione di pacchetti Python nell'area utente:

    git clone https://github.com/flatpak/flatpak-builder-tools .flatpak-builder-tools
    python3 -m pip install --user --upgrade pip requirements-parser
    FLATPAK_PYTHON=python3 sh packaging/flatpak/generate-python-sources.sh

Se Python è gestito dalla distribuzione e blocca l'installazione, usa la modalità virtual environment descritta sotto. Non è necessario eseguire `deactivate` in questa modalità.

### Modalità B: virtual environment isolato (consigliata)

    git clone https://github.com/flatpak/flatpak-builder-tools .flatpak-builder-tools
    python3 -m venv .flatpak-tools-venv
    . .flatpak-tools-venv/bin/activate
    python -m pip install --upgrade pip requirements-parser
    FLATPAK_PYTHON=.flatpak-tools-venv/bin/python sh packaging/flatpak/generate-python-sources.sh
    deactivate

`requirements-parser` serve solo allo strumento di build e non viene incluso nella sandbox runtime. Il JSON generato contiene le sorgenti offline delle dipendenze.

Le voci esplicite `pybind11`, `scikit-build-core` e `nanobind` in packaging/flatpak/requirements.txt sono intenzionali: Pillow e zxing-cpp vengono compilati da sorgente nella sandbox Flatpak e richiedono queste dipendenze di build.

## 4. Build e installazione locale

Dalla radice del repository:

    flatpak-builder --user --install --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml

Avvio della GUI, che è il comando predefinito:

    flatpak run org.keysng.KeysNG

Avvio esplicito delle tre interfacce:

    flatpak run --command=keys-ng-gui org.keysng.KeysNG
    flatpak run --command=keys-ng-tui org.keysng.KeysNG
    flatpak run --command=keys-ng org.keysng.KeysNG --help

La TUI e la CLI vanno avviate da un terminale. Gli argomenti della CLI si aggiungono dopo l'ID dell'applicazione, per esempio:

    flatpak run --command=keys-ng org.keysng.KeysNG vault-list

## 5. Creare un bundle redistribuibile

Genera prima un repository OSTree locale:

    rm -rf repo-flatpak build-flatpak
    flatpak-builder --repo=repo-flatpak --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml

Crea quindi il file singolo `.flatpak`:

    flatpak build-bundle repo-flatpak Keys-NG-0.1.24.flatpak org.keysng.KeysNG --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo

Il file può essere installato su un altro sistema con:

    flatpak install --user Keys-NG-0.1.24.flatpak

L'opzione `--runtime-repo` indica a Flatpak dove recuperare il runtime KDE e il BaseApp, che non vengono incorporati integralmente nel bundle.

Per pubblicare anche un checksum:

    sha256sum Keys-NG-0.1.24.flatpak > SHA256SUMS

Per Flathub o un altro repository pubblico è preferibile pubblicare un repository OSTree aggiornabile invece di soltanto un bundle locale.

## 6. Checklist di verifica

Verifica almeno:

- apertura e sblocco di un vault nella home selezionata;
- elenco chiavi GnuPG e cifratura/decifratura tramite l'host;
- launcher SSH e RDP, se configurati;
- importazione KeePassXC KDBX e XML;
- clipboard e TOTP;
- avvio di GUI, TUI e CLI;
- voce nel menu applicazioni e versione GUI mostrata sotto Aiuto.

Comandi utili:

    flatpak info org.keysng.KeysNG
    flatpak run org.keysng.KeysNG

## 7. Permessi e sicurezza

Il manifest richiede attualmente accesso al filesystem home, socket Wayland e X11 fallback, accesso DRI e accesso D-Bus a org.freedesktop.Flatpak.

Questi permessi sono intenzionali ma ampi. Il pacchetto non è completamente isolato dal vault dell'utente o dagli strumenti di credenziali dell'host: riusa keyring e agent GnuPG dell'host e avvia helper SSH/RDP sull'host. Verificare i permessi prima della distribuzione.

## 8. Aggiornare il pacchetto

Quando cambiano le dipendenze Python, aggiorna packaging/flatpak/requirements.txt e rigenera il modulo JSON dei sorgenti. Esegui nuovamente build e test, poi aggiorna la versione dell'applicazione e org.keysng.KeysNG.metainfo.xml per la release.

La wheel resta il formato consigliato per CLI/TUI e per gli ambienti in cui non si desidera la delega degli strumenti all'host.
