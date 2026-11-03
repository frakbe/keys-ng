# Keys NG — Creazione dei pacchetti nativi macOS con Briefcase

Questa guida descrive come creare, provare, firmare e distribuire i pacchetti nativi macOS di Keys NG. La build deve essere eseguita su macOS. Il successo della build non basta per la distribuzione: l'app o l'installer deve essere provato anche su un account o una VM macOS pulita.

## 1. Host di build e runtime

| Componente | Host di build | Runtime utente | Scopo |
|---|---:|---:|---|
| macOS su hardware Apple supportato | necessario | necessario | Briefcase, firma e notarizzazione Apple |
| Python 3.11+ | necessario | incluso da Briefcase | strumenti di build/runtime |
| Xcode Command Line Tools | necessario | no | compilatore, codesign e strumenti di packaging |
| Git | necessario | no | sorgenti e operazioni Briefcase |
| Briefcase | necessario | no | create, build, run e package |
| GnuPG e pinentry | consigliati per i test | necessari per Keys NG | OpenPGP, gpg-agent e passphrase |
| PySide6/Textual/dipendenze | risolte da Briefcase | incluse | runtime applicativo |

Keys NG non include né sostituisce GnuPG su macOS. L'applicazione pacchettizzata richiede comunque un'installazione funzionante di GnuPG e una configurazione pinentry sul Mac destinazione.

## 2. Prerequisiti

Installare gli Xcode Command Line Tools se non sono già presenti:

    xcode-select --install

Verificare l'host:

    sw_vers
    uname -m
    python3 --version
    git --version
    xcode-select -p
    xcrun --find clang
    codesign --version
    hdiutil -help | head

Per i test runtime installare GnuPG. Homebrew è una possibilità:

    brew install gnupg pinentry-mac
    gpg --version
    gpgconf --version

Creare o importare soltanto chiavi di test temporanee. Non usare chiavi private di produzione durante i test di packaging.

## 3. Ambiente isolato

Dalla root del progetto:

    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install briefcase

Verificare:

    python --version
    python -m briefcase --version

Usare la stessa architettura Python prevista per il target. Su Apple Silicon verificare se la build è arm64 o universal prima di pubblicare l'artefatto: una build arm64 non va considerata automaticamente compatibile con Mac Intel.

## 4. Metadata di packaging

Le applicazioni native sono configurate in pyproject.toml:

    keys_ng      -> src/keys_ng       -> GUI
    keys_ng_cli  -> src/keys_ng_cli   -> wrapper CLI
    keys_ng_tui  -> src/keys_ng_tui   -> wrapper TUI

La GUI usa l'icona macOS configurata da Briefcase. Devono esistere la risorsa .icns corrispondente e il file LICENSE nella root. Mantenere allineati metadata PEP 639, versione Briefcase e keys_ng.__version__.

La dipendenza runtime da GnuPG è intenzionale: va documentata agli utenti e verificata sul Mac destinazione, senza sostituirla silenziosamente con una gestione interna delle chiavi private.

## 5. Build e avvio della GUI

Creare il progetto nativo macOS:

    python -m briefcase create macOS -a keys_ng

Costruirlo:

    python -m briefcase build macOS -a keys_ng

Avviarlo prima del packaging:

    python -m briefcase run macOS -a keys_ng

Creare il DMG di sviluppo:

    python -m briefcase package macOS -a keys_ng -p dmg

L'output viene scritto sotto dist/. Un DMG creato senza identità Developer ID serve solo per test locali.

## 6. CLI e TUI

Per un'applicazione console, la distribuzione macOS deve usare un PKG invece di un DMG:

    python -m briefcase create macOS -a keys_ng_cli
    python -m briefcase build macOS -a keys_ng_cli
    python -m briefcase run macOS -a keys_ng_cli -- version
    python -m briefcase package macOS -a keys_ng_cli -p pkg

Per la TUI:

    python -m briefcase create macOS -a keys_ng_tui
    python -m briefcase build macOS -a keys_ng_tui
    python -m briefcase run macOS -a keys_ng_tui -- --version
    python -m briefcase package macOS -a keys_ng_tui -p pkg

Il separatore -- passa gli argomenti successivi all'applicazione. Provare i pacchetti console su un account pulito prima di distribuirli.

Per test controllati è possibile creare anche uno ZIP dell'app:

    python -m briefcase package macOS -a keys_ng -p zip

## 7. Pulizia e ricostruzione

Dopo modifiche a pyproject.toml, nomi applicazione, sources, dipendenze, icona, licenza o launcher, eliminare lo scaffold Briefcase precedente e ricrearlo:

    rm -rf build macOS
    python -m briefcase create macOS -a keys_ng
    python -m briefcase build macOS -a keys_ng

Non eliminare una directory contenente artefatti prima di avere copiato altrove i relativi checksum. Eseguire la pulizia dalla root del progetto e dopo aver verificato i percorsi.

## 8. Firma di sviluppo e verifica

Per i test locali può bastare una firma ad-hoc. Non è una firma di distribuzione e non identifica lo sviluppatore. Elencare le identità disponibili:

    security find-identity -v -p codesigning

Verificare un'app:

    codesign --verify --deep --strict --verbose=2 "dist/Keys NG.app"
    spctl --assess --type execute --verbose=4 "dist/Keys NG.app"

Il percorso esatto può cambiare in base alla versione Briefcase. Usare find dist -maxdepth 3 -name '*.app' per individuarlo.

Per la distribuzione usare un'identità Developer ID Application dell'Apple Developer account. Per un PKG firmato serve anche un'identità Developer ID Installer della stessa organizzazione. Non salvare certificati, chiavi private o credenziali di notarizzazione nel repository.

## 9. Firma, notarizzazione e stapling

Il flusso di release deve usare le opzioni di firma e notarizzazione supportate dalla versione Briefcase installata. Controllare prima l'help:

    python -m briefcase package macOS --help

Per un DMG GUI firmato fornire l'identità Developer ID Application secondo la versione Briefcase installata e consentire la notarizzazione. Per un PKG fornire anche l'identità installer. Per gli artefatti di solo sviluppo è possibile disabilitare esplicitamente la notarizzazione, ma non presentarli come release di produzione.

Dopo la notarizzazione verificare e, se non già eseguito dal packaging, applicare il ticket:

    xcrun stapler validate "dist/Keys NG.app"
    spctl --assess --type execute --verbose=4 "dist/Keys NG.app"

Se una submission viene interrotta, usare l'identificativo stampato da Briefcase con l'opzione resume supportata invece di avviare una seconda submission scollegata. Registrare ID e stato finale nelle evidenze.

Prima della release verificare che l'artefatto non contenga path di sviluppo, chiavi di test, credenziali private o configurazioni debug.

## 10. Checklist smoke test

    [ ] il DMG si apre sul Mac di build
    [ ] l'app può essere copiata in Applications
    [ ] l'app parte da Finder e da terminale
    [ ] identità e icona sono corrette
    [ ] keys-ng doctor risolve gpg e gpgconf
    [ ] keys-ng keys elenca le chiavi di test
    [ ] compare pinentry quando serve la chiave privata
    [ ] apertura di un vault di test
    [ ] wizard Nuovo Vault crea e apre un vault
    [ ] creazione/modifica/salvataggio voce
    [ ] timeout clipboard
    [ ] generazione TOTP
    [ ] lock e hard-lock globale
    [ ] lista dei vault recenti apre un vault di test
    [ ] avvio del pacchetto CLI da terminale
    [ ] avvio del pacchetto TUI e apertura di un vault
    [ ] pacchetto funzionante su account o VM macOS pulita
    [ ] artefatto firmato verificato con codesign
    [ ] artefatto notarizzato verificato con spctl
    [ ] checksum DMG o PKG registrato

## 11. Troubleshooting

### Briefcase non crea il progetto macOS

Verificare Python, Git, Xcode Command Line Tools e versione Briefcase. Eliminare lo scaffold build/macOS e ricrearlo dopo modifiche strutturali.

### L'app parte ma non apre il vault

Installare GnuPG e pinentry sul sistema destinazione. Eseguire keys-ng doctor e configurare eventualmente i percorsi gpg e gpgconf nelle Preferenze o in config.toml.

### codesign o notarizzazione falliscono

Verificare che il certificato Developer ID sia nel login keychain, che l'identità corrisponda all'Apple Developer Team e che il bundle identifier sia stabile. Conservare l'output completo Briefcase e non distribuire artefatti con firma fallita o saltata.

### spctl rifiuta l'app

Controllare firma, entitlements, stato quarantine e risultato della notarizzazione. Ripetere codesign, interrogare lo stato della submission con gli strumenti Apple disponibili e correggere il primo errore segnalato.

### Icona mancante

Verificare la presenza della risorsa .icns configurata e ricreare lo scaffold dopo ogni modifica a icona o metadata.

### Dipendenza mancante nel pacchetto

Controllare output Briefcase e requisiti delle app in pyproject.toml. Ricreare lo scaffold dopo aver modificato i requisiti e avviare l'app prima del packaging.

## 12. Evidenze di release

Conservare:

- commit Git e tag esatti;
- versioni Briefcase e Python;
- versione macOS e architettura;
- checksum SHA256 di DMG, PKG o ZIP;
- output di verifica codesign;
- submission/status notarizzazione e verifica stapler;
- risultati smoke test sul Mac di build e su un host pulito.

Il solo successo del comando package non costituisce validazione della release.
