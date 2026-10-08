# Generare il Flatpak di Keys NG su Linux

Questa guida descrive il flusso supportato per creare il Flatpak della GUI di Keys NG. Il manifest e lo script di supporto si trovano in packaging/flatpak/.

## 1. Struttura del pacchetto

Il Flatpak usa KDE Platform 6.11 e io.qt.PySide.BaseApp. Include la GUI; CLI e TUI restano disponibili tramite wheel Python o altri pacchetti nativi.

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

    git clone https://github.com/flatpak/flatpak-builder-tools .flatpak-builder-tools
    python3 -m venv .flatpak-tools-venv
    . .flatpak-tools-venv/bin/activate
    python -m pip install --upgrade pip requirements-parser
    FLATPAK_PYTHON=.flatpak-tools-venv/bin/python packaging/flatpak/generate-python-sources.sh
    deactivate

requirements-parser serve solo allo strumento di build e non va installato nel Python di sistema gestito dalla distribuzione. Il JSON generato contiene le sorgenti offline e non entra nella sandbox runtime.

## 4. Build e installazione locale

Dalla radice del repository:

    flatpak-builder --user --install --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml
    flatpak run org.keysng.KeysNG

## 5. Repository o bundle distribuibile

Per creare un repository OSTree locale:

    flatpak-builder --repo=repo-flatpak --force-clean build-flatpak packaging/flatpak/org.keysng.KeysNG.yml
    flatpak --user remote-add --if-not-exists keys-ng-local repo-flatpak
    flatpak --user install keys-ng-local org.keysng.KeysNG

Per creare un bundle singolo:

    flatpak build-bundle repo-flatpak Keys-NG.flatpak org.keysng.KeysNG

Per Flathub o un altro repository pubblico è preferibile pubblicare manifest e metadati dei sorgenti, non soltanto un bundle locale.

## 6. Checklist di verifica

Verifica almeno:

- apertura e sblocco di un vault nella home selezionata;
- elenco chiavi GnuPG e cifratura/decifratura tramite l'host;
- launcher SSH e RDP, se configurati;
- importazione KeePassXC KDBX e XML;
- clipboard e TOTP;
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