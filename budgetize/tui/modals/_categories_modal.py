"""Defines the modal to edit user categories"""

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, SelectionList

from budgetize import SettingsManager
from budgetize.db import Database
from budgetize.utils import _


class CategoriesModal(ModalScreen):

    DB: Database = None  # type: ignore

    def __init__(self) -> None:
        """Creates a new CategoriesModal instance."""

        self.settings = SettingsManager()
        self.current_categories = self.settings.get_categories()
        CategoriesModal.DB = Database(self.app)
        super().__init__()

    def compose(self) -> ComposeResult:
        """Composes the CategoriesModal screen."""

        with ScrollableContainer(id="scrollable"):

            self.selection_list: SelectionList[str] = SelectionList(
                *self._get_categories_tuple(), id="categories-list"
            )
            yield self.selection_list

        with Horizontal(id="horizontal"):
            yield Button(_("Add Category"), id="add-category-btn", variant="primary")
            yield Button.error(
                _("Delete Selected Categories"), id="delete-btn", disabled=True
            )
            yield Button(_("Close"), id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Triggers when a Button is pressed."""

        # TODO: Show confirmation msg
        if event.button.id == "delete-btn":
            selected_items = self.selection_list.selected

            for category in selected_items:
                self.current_categories.remove(category)

            self.settings.set_categories(self.current_categories)
            self.selection_list.clear_options()
            for category in self.current_categories:
                self.selection_list.add_option((category, category))

        if event.button.id == "close-btn":
            self.app.pop_screen()

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
        return [(category, category) for category in self.current_categories]
