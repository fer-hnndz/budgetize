"""Defines the modal to edit user categories"""

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, SelectionList

from budgetize import SettingsManager
from budgetize.db import Database


class CategoriesModal(ModalScreen):

    DB: Database = None  # type: ignore

    def __init__(self) -> None:
        """Creates a new CategoriesModal instance."""

        self.settings = SettingsManager()
        CategoriesModal.DB = Database(self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        """Composes the CategoriesModal screen."""

        with ScrollableContainer(id="scrollable"):

            selection_list: SelectionList[str] = SelectionList(
                *self._get_categories_tuple(), id="categories-list"
            )
            yield selection_list

        with Horizontal(id="horizontal"):
            yield Button("Add Category", id="add-category-btn", variant="primary")
            yield Button.error(
                "Delete Selected Categories", id="delete-btn", disabled=True
            )

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        """Triggers when a selection is changed in the selection list"""

        selected_items = event.selection_list.selected

        horizontal_container = self.app.get_child_by_id(
            "horizontal", expect_type=Horizontal
        )
        delete_button = horizontal_container.get_child_by_id(
            "delete-btn", expect_type=Button
        )

        delete_button.disabled = True if not selected_items else False

    def _get_categories_tuple(self) -> list[tuple[str, str]]:
        """Returns a list of tuples with the category name in both values"""

        categories = self.settings.get_categories()
        return [(category, category) for category in categories]
