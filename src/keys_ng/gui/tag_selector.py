"""Editable menu with independently checkable tags, without secret record caching."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QToolButton, QMenu

from keys_ng.i18n import _


class TagSelector(QWidget):
    def __init__(self, available, selected, parent=None):
        super().__init__(parent)
        self.available = set(available) | set(selected)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.edit = QLineEdit(", ".join(selected), self)
        self.edit.setPlaceholderText(_("Add tags, separated by commas"))
        self.button = QToolButton(self)
        self.button.setText(_("Select tags"))
        self.button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.menu = QMenu(self.button)
        self.menu.aboutToShow.connect(self.refresh_menu)
        self.button.setMenu(self.menu)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)

    def selected_tags(self):
        return list(dict.fromkeys(t.strip() for t in self.edit.text().split(",") if t.strip()))

    def text(self):
        return ", ".join(self.selected_tags())

    def refresh_menu(self):
        self.menu.clear()
        selected = self.selected_tags()
        self.available.update(selected)
        for tag in sorted(self.available, key=str.casefold):
            action = self.menu.addAction(tag)
            action.setCheckable(True)
            action.setChecked(tag in selected)
            action.toggled.connect(lambda checked, value=tag: self.toggle_tag(value, checked))

    def toggle_tag(self, tag, checked):
        selected = self.selected_tags()
        if checked and tag not in selected:
            selected.append(tag)
        elif not checked:
            selected = [t for t in selected if t != tag]
        self.edit.setText(", ".join(selected))

    def clear(self):
        self.edit.clear()
        self.available.clear()
        self.menu.clear()
