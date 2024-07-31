"""Module that contains the Screen for creating budgets."""

from typing import Optional

from babel.numbers import format_currency
from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Select

from budgetize.budget import Budget
from budgetize.settings_manager import SettingsManager
from budgetize.utils import _


class CreateBudget(Screen):
    """Screen that allows the user to create/edit a budget.

    Arguments
    ----------
    budget: `Optional[budgetize.Budget]`
        The budget to edit. If `None`, a new budget will be created/overwritten.
    """

    CSS_PATH = "css/create_budget.tcss"

    def __init__(self, budget: Optional[Budget] = None):
        self.app.sub_title = _("Create Budget")
        super().__init__()

        self.mgr = SettingsManager()
        self.expected_income = budget.get_income() if budget else 0.0
        self.categories_limit: dict[str, float] = (
            budget.to_dict()["categories"] if budget else {}
        )
        self.limits_total = 0.0
        self.budget_balanced = True if budget else False

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header()

        with Center():
            yield Label(_("Expected Monthly Income"), id="expected-income-label")

            #! =========================================
            #! Widget.tooltip is an attribute. Hence that's why mypy doesn't like passing it as a paremeter.
            #! Perhaps this is an issue.
            #! =========================================

            expected_income = Input(
                id="expected-income-input",
                type="number",
                value=str(self.expected_income),
                placeholder=format_currency(
                    number=1200,
                    currency=self.mgr.get_base_currency(),
                    locale=self.mgr.get_locale(),
                ),
            )
            expected_income.tooltip = _(
                "The amount of money you expect to earn each month."
            )
            yield expected_income
            yield Label(_("Categories Expense Limit"), id="expense-limit-label")
            yield Label("", id="limits-label")
            with Horizontal(id="categories-horizontal"):
                category_select = Select(
                    id="category-select",
                    options=[
                        (category, category)
                        for category in SettingsManager().get_categories()
                    ],
                    allow_blank=False,
                )
                category_select.tooltip = _("The name of the category.")
                yield category_select

                category_limit_input = Input(
                    id="category-limit-input",
                    type="number",
                    placeholder=format_currency(
                        number=100,
                        currency=self.mgr.get_base_currency(),
                        locale=self.mgr.get_locale(),
                    ),
                )
                category_limit_input.tooltip = _("The expense limit of the category.")
                yield category_limit_input

            with Horizontal(id="limits-btns"):
                yield Button(_("Add Limit"), id="add-limit-btn")
                yield Button(_("Delete Limit"), id="delete-limit-btn", variant="error")
            yield Button(
                _("Save Budget"), id="save-budget-btn", variant="success", disabled=True
            )

    def after_layout(self) -> None:
        """Called after the layout is done."""
        self._update_limits_label()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handler for all button presses."""
        category_select = self.query_one("#category-select", expect_type=Select)
        limit_input = self.query_one("#category-limit-input", expect_type=Input)
        delete_button = self.query_one("#delete-limit-btn", expect_type=Button)

        if event.button.id == "add-limit-btn":
            limit_val = float(limit_input.value)

            if limit_val <= 0:
                self.app.notify(
                    title=_("Could not add Limit"),
                    message=_("The limit must be greater than 0."),
                    severity="error",
                )
                return

            self.categories_limit[str(category_select.value)] = float(limit_input.value)
            delete_button.disabled = False
            limit_input.clear()

        if event.button.id == "delete-limit-btn":
            self.categories_limit.pop(str(category_select.value))
            delete_button.disabled = True
            limit_input.clear()

        if event.button.id == "save-budget-btn":
            new_budget = Budget(
                income=self.expected_income, categories=self.categories_limit
            )

            self.mgr.save_budget(new_budget)
            self.app.notify(
                title=_("Budget Saved"),
                message=_("Your budget has been saved."),
                severity="information",
            )
            self.app.pop_screen()
            return

        self._update_limits_label()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handler for all select changes."""
        if event.select.id == "category-select":
            category_select = self.query_one("#category-select", expect_type=Select)
            limit_input = self.query_one("#category-limit-input", expect_type=Input)

            if category_select.value in self.categories_limit:

                # Update the limit input with the saved limit
                limit_input.value = str(
                    self.categories_limit[str(category_select.value)]
                )

                # Enable the delete button
                delete_button = self.query_one("#delete-limit-btn", expect_type=Button)
                delete_button.disabled = False

            else:
                # Disable the delete button
                delete_button = self.query_one("#delete-limit-btn", expect_type=Button)
                delete_button.disabled = True
                limit_input.clear()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "expected-income-input":
            return

        expected_income_input = self.query_one(
            "#expected-income-input", expect_type=Input
        )

        if expected_income_input.value.strip() == "":
            self.expected_income = 0.0
            return

        converted_value = float(expected_income_input.value)
        self.expected_income = converted_value if converted_value > 0 else 0.0
        self._update_limits_label()

    def _update_limits_label(self) -> None:
        """Updates the label that shows the limit for each category"""
        msg = self._get_limits_msg()
        self.query_one("#limits-label", expect_type=Label).update(msg)

        save_button = self.query_one("#save-budget-btn", expect_type=Button)
        save_button.disabled = not self.budget_balanced

    def _get_limits_msg(self) -> str:
        """Returns the message that shows the limit for each catergory."""

        self.budget_balanced = False
        msg = ""
        self.limits_total = 0.0
        for category, limit in self.categories_limit.items():

            category_limit = format_currency(
                number=limit,
                currency=self.mgr.get_base_currency(),
                locale=self.mgr.get_locale(),
            )

            # Calculate ratio (percentage) of the limit to the expected income
            ratio_msg = self._get_category_ratio_msg(limit)

            msg += f"{category}: {category_limit} ({ratio_msg})\n"
            self.limits_total += limit

        # Add total message
        msg += _(
            "\n[yellow2]Total Limits: {total_limits}\n".format(
                total_limits=format_currency(
                    number=self.limits_total,
                    currency=self.mgr.get_base_currency(),
                    locale=self.mgr.get_locale(),
                )
            )
        )

        difference = format_currency(
            number=self.expected_income - self.limits_total,
            currency=self.mgr.get_base_currency(),
            locale=self.mgr.get_locale(),
        )

        # Add message to guide user to adjust limits
        if self.limits_total > self.expected_income:
            msg += _(
                "[red]WARNING: Your total limits exceed your expected income ({difference}). Considering lowering the limits"
            ).format(difference=difference)
        elif self.limits_total == self.expected_income:
            msg += _("[green]You have perfectly balanced your budget. Good job!")
            self.budget_balanced = True
        else:
            msg += _(
                "[blue]You still have money on your expected income to spend (+ {difference}). Perhaps you can increase some limits.".format(
                    difference=difference
                )
            )

        return msg

    def _get_category_ratio_msg(self, limit: float) -> str:
        """Returns the ratio of the limit to the expected income."""

        ratio = limit / self.expected_income
        ratio_msg = f"{round(ratio * 100, 2)}%" if ratio >= 0 else "N/A"
        return ratio_msg
