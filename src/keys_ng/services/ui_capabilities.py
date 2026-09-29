from __future__ import annotations

# Interactive capabilities that ordinary users should be able to reach from both
# graphical and terminal frontends. Administrative/diagnostic CLI-only commands
# (doctor, reindex, catalog-health, desktop integration, legacy migration) are
# intentionally outside this parity contract.
INTERACTIVE_CAPABILITIES = frozenset({
    "vault.create", "vault.open", "vault.close", "vault.recent",
    "entry.create", "entry.edit", "entry.delete", "entry.move",
    "entry.copy_url", "entry.copy_username", "entry.copy_password",
    "entry.copy_totp", "entry.copy_uuid", "entry.copy_notes",
    "entry.export_keepassxc_xml", "vault.export_keepassxc_xml",
    "vault.import_keepassxc", "password.generate",
    "folder.create", "folder.rename", "folder.move", "folder.delete",
    "inbox.review", "trusted_signers.manage", "preferences.edit",
    "help.read", "vault.lock", "vault.unlock",
})

GUI_CAPABILITIES = INTERACTIVE_CAPABILITIES
TUI_CAPABILITIES = INTERACTIVE_CAPABILITIES

def missing_interactive_capabilities(frontend: str) -> frozenset[str]:
    implemented = GUI_CAPABILITIES if frontend == "gui" else TUI_CAPABILITIES if frontend == "tui" else frozenset()
    return INTERACTIVE_CAPABILITIES - implemented
