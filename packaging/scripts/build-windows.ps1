$ErrorActionPreference = "Stop"
python -m pip install --upgrade briefcase
briefcase create windows
briefcase build windows
briefcase package windows -p msi
