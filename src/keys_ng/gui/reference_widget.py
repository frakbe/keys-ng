"""Readable reference origins shared by the entry editor and detail pane."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from keys_ng.i18n import _
from keys_ng.services.reference_info import inspect_reference


class ReferenceWidget(QWidget):
    open_origin = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.info = None
        self.label = QLabel()
        self.label.setTextFormat(Qt.TextFormat.PlainText)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.open_button = QPushButton(_("Open source entry"))
        self.open_button.clicked.connect(self.open_source)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        row = QHBoxLayout()
        row.addWidget(self.label, 1)
        row.addWidget(self.open_button)
        layout.addLayout(row)
        self.clear()

    def clear(self):
        self.info = None
        self.label.clear()
        self.setToolTip("")
        self.hide()

    def update_reference(self, vault, value, *, source=None):
        self.clear()
        if not value or not value.strip().startswith("{REF:"):
            return
        self.info = inspect_reference(vault, value, source=source)
        lines = []
        for hop in self.info.hops:
            field = _("Username") if hop.field == "U" else _("Password")
            lines.append(_("Linked to: {title} — {path} ({field})").format(
                title=hop.title, path=hop.path or _("Root"), field=field))
        errors = {
            "locked": _("Vault locked."),
            "invalid": _("Invalid or unsupported reference."),
            "cycle": _("Circular reference."),
            "depth": _("Reference chain is too deep."),
            "missing": _("Source entry not found."),
            "unavailable": _("Source entry cannot be read or verified."),
            "empty": _("Source field is empty."),
        }
        if self.info.error:
            lines.append(errors[self.info.error])
        self.label.setText("\n→ ".join(lines))
        # Only canonical reference identifiers, never the resolved password.
        self.setToolTip("\n".join(f"{{REF:{h.field}@I:{h.entry_id}}}" for h in self.info.hops))
        self.open_button.setEnabled(bool(self.info.hops))
        self.show()

    def open_source(self):
        if self.info and self.info.hops:
            self.open_origin.emit(self.info.hops[0].entry_id)
