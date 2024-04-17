"""Module that defines the FileSelectorModal"""

import logging

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

    def compose(self) -> ComposeResult:
        logging.info("Composing FileSelectorModa")
        with Center(id="center"):
            yield Label(self.msg, id="msg")
            yield DirectoryTree(path=self.path, id="tree")

            with Horizontal(id="btns"):
                yield Button(_("Accept"), id="accept-btn", variant="primary")
                yield Button.error(_("Cancel"), id="cancel-btn")
