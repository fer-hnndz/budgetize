"""Module that defines the FileSelectorModal"""

import logging
from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Label

from budgetize.consts import APP_FOLDER_PATH, BACKUPS_FOLDER
from budgetize.utils import _


class FileSelectorModal(ModalScreen):
    """A modal that allows a user to select a file/folder"""

    CSS_PATH = "css/file_selector_modal.tcss"

    def __init__(self, path: str, message: str = _("Select a File")) -> None:
        """Creates a new instance of a FileSelector Modal

        Args:
            path (str): The path thethe File selector
            message (str): A message that is shown above the file selector.

        """
        super().__init__()
        self.msg = message
        self.path = path

        self.selected_path: Optional[Path] = None

    def compose(self) -> ComposeResult:
        logging.info("Composing FileSelectorModa")
        with Center(id="center"):
            yield Label(self.msg, id="msg")
            yield DirectoryTree(path=self.path, id="tree")

            with Horizontal(id="btns"):
                yield Button(_("Accept"), id="accept-btn", variant="primary")
                yield Button.error(_("Cancel"), id="cancel-btn")

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Triggered when selected file is changed"""

        self.selected_path = event.path
        print(f"Selected Path: {self.selected_path}")
        logging.debug(
            f"Selected Path: {self.selected_path}",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Button press handler"""

        print(self.selected_path)
        if event.button.id == "accept-btn":
            if self.selected_path is None:
                self.notify(
                    title=_("Recover From Backup"),
                    message=_("Please select a backup file to recover from."),
                    severity="error",
                )
                return

            if not self.selected_path.is_file():
                self.notify(
                    title=_("Recover From Backup"),
                    message=_("Please select a valid backup file to recover from."),
                    severity="error",
                )
                return

            self.dismiss(self.selected_path)
        elif event.button.id == "cancel-btn":
            self.dismiss(None)
