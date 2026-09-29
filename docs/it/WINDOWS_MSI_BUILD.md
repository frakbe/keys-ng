# Keys NG M1.19 — Creazione dei pacchetti MSI Windows con Briefcase

Questo documento raccoglie la procedura Windows verificata durante il lavoro di packaging M1.18.1/M1.19. È rivolto a manutentori e revisori della release. La build va eseguita su Windows; l'MSI risultante va poi provato, preferibilmente, su un account o una VM Windows pulita.

## 1. Ambiente di build e ambiente runtime

| Componente | Host di build | Runtime utente | Scopo |
|---|---:|---:|---|
| Python 3.11+ | necessario | incluso da Briefcase | strumenti di build/runtime applicativo |
| Git for Windows | necessario nel workflow verificato | no | operazioni Briefcase/template/sorgenti usate dalla build |
| Briefcase | necessario | no | create/build/package |
| WiX/toolchain usato da Briefcase | necessario durante il packaging | no | generazione MSI |
| Gpg4win / GnuPG | fortemente consigliato per gli smoke test | necessario | OpenPGP, gpg-agent, pinentry |
| PySide6/Textual/dipendenze applicative | risolte da Briefcase | incluse | runtime GUI/TUI |

Git **non è una dipendenza runtime di Keys NG**. Tuttavia, nel workflow Windows realmente verificato per questo progetto Briefcase non riusciva a completare la creazione dei binari quando Git non era installato. Installare quindi **Git for Windows** da `https://git-scm.com` prima di usare Briefcase.

## 2. Prerequisiti

Installare Python 64 bit supportato e Git for Windows. Per i test runtime installare anche Gpg4win e creare o importare almeno una coppia di chiavi di test.

Da PowerShell:

```powershell
py --version
git --version
Get-Command git
```

Per i test runtime GnuPG:

```powershell
gpg --version
gpgconf --version
```

M1.19 può individuare automaticamente le normali installazioni Gpg4win/GnuPG anche se `gpg.exe` non è nel `PATH`. Con versioni precedenti è stato utile, a fini diagnostici, il workaround temporaneo:

```powershell
$env:Path += ";C:\Program Files\GnuPG\bin"
```

Con M1.19 non dovrebbe essere normalmente necessario.

## 3. Preparazione di un ambiente di build isolato

Dalla root del progetto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install briefcase
```

Verifica:

```powershell
python --version
git --version
python -m briefcase --version
```

## 4. Metadata di packaging da mantenere validi

Il progetto usa metadata PEP 639:

```toml
[project]
license = "GPL-3.0-or-later"
license-files = ["LICENSE"]
```

Il file `LICENSE` deve esistere realmente nella root. Non tornare al formato deprecato `license = { file = ... }`.

I nomi applicazione Briefcase devono corrispondere a un package sorgente. M1.19 fornisce:

```text
keys_ng      -> src/keys_ng       -> GUI
keys_ng_cli  -> src/keys_ng_cli   -> wrapper CLI
keys_ng_tui  -> src/keys_ng_tui   -> wrapper TUI
```

Il launcher GUI è `src/keys_ng/__main__.py`; i wrapper console delegano rispettivamente a `keys_ng.cli.main` e `keys_ng.tui.main`.

## 5. Creazione dell'MSI GUI

```powershell
python -m briefcase create windows -a keys_ng
python -m briefcase build windows -a keys_ng
```

Prima del packaging eseguire sempre lo smoke test:

```powershell
python -m briefcase run windows -a keys_ng
```

Poi creare l'MSI:

```powershell
python -m briefcase package windows -a keys_ng -p msi
```

L'artefatto viene scritto sotto `dist\`.

## 6. CLI e TUI

CLI:

```powershell
python -m briefcase create windows -a keys_ng_cli
python -m briefcase build windows -a keys_ng_cli
python -m briefcase run windows -a keys_ng_cli -- version
python -m briefcase package windows -a keys_ng_cli -p msi
```

TUI:

```powershell
python -m briefcase create windows -a keys_ng_tui
python -m briefcase build windows -a keys_ng_tui
python -m briefcase run windows -a keys_ng_tui -- --version
python -m briefcase package windows -a keys_ng_tui -p msi
```

Il separatore `--` indica che gli argomenti successivi vanno passati all'applicazione console e non a Briefcase.

## 7. Pulizia dopo modifiche strutturali

Se cambiano `pyproject.toml`, nomi applicazione, `sources`, metadata licenza o launcher, eliminare lo scaffold precedente:

```powershell
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force windows -ErrorAction SilentlyContinue
```

Poi rieseguire `create` e `build`.

## 8. Checklist runtime dell'MSI

```text
[ ] installazione MSI riuscita
[ ] voce nel menu Start e icona corrette
[ ] avvio GUI
[ ] `keys-ng doctor` mostra i percorsi risolti di gpg.exe e gpgconf.exe
[ ] `keys-ng keys` elenca le chiavi di test
[ ] appare pinentry quando serve la chiave privata
[ ] apertura di un vault esistente
[ ] wizard Nuovo Vault crea e apre il vault
[ ] creazione/modifica/salvataggio voce
[ ] Mostra/Nascondi password
[ ] clipboard e cancellazione temporizzata
[ ] TOTP
[ ] lock e hard-lock
[ ] CLI funzionante dal terminale
[ ] TUI avviabile e capace di creare/aprire un vault
[ ] disinstallazione pulita
```

## 9. Troubleshooting emerso dai test reali

### `sources ... does not include a package named ...`

Il nome dell'app Briefcase e il package sorgente non coincidono. M1.19 usa `keys_ng` per la GUI perché il package reale è `src/keys_ng`.

### `does not define either sources or external_package_path`

Una sottosezione obsoleta come `[tool.briefcase.app.keys_ng_gui.windows]` può far interpretare `keys_ng_gui` come un'altra applicazione. Cercare l'intero file:

```powershell
Select-String -Path pyproject.toml -Pattern "keys_ng_gui"
```

### `Your project does not include any license files`

Verificare metadata PEP 639 e file fisico:

```powershell
Test-Path .\LICENSE
```

### Git non trovato / Briefcase non completa la creazione

Installare Git for Windows da `https://git-scm.com`, aprire una nuova PowerShell e verificare:

```powershell
git --version
Get-Command git
```

### `Unable to execute GnuPG: [WinError 2]`

M1.19 cerca `PATH`, informazioni di installazione Windows e percorsi standard Gpg4win/GnuPG. Eseguire:

```powershell
keys-ng doctor
```

Se necessario configurare percorsi espliciti nelle Preferenze oppure in `config.toml`:

```toml
[gnupg]
gpg = "C:\\Program Files\\GnuPG\\bin\\gpg.exe"
gpgconf = "C:\\Program Files\\GnuPG\\bin\\gpgconf.exe"
```

### Le modifiche alla configurazione Briefcase sembrano ignorate

Eliminare `build`/`windows` come nella sezione 7 e ricreare il progetto nativo.

## 10. Regola di release

Il solo successo di `package` non basta. Il manutentore deve completare `create`, `build`, `run` e `package`, quindi eseguire la checklist runtime su Windows con Gpg4win. Conservare gli hash degli MSI insieme agli altri artefatti della release.
