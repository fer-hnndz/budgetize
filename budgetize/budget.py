"""Module that defines the Budget class."""


class Budget:
    """Represents a budget a user can create.

    A budget should have an expected monthly income, and the expend limit for each selected category.
    """

    def __init__(self, income: float, categories: dict[int, float]):
        """Initializes a new budget.

        Arguments
        ---------
            income: `float`
                The expected monthly income.
            categories `dict`:
                A dictionary with the categories and their respective expend limits.
                Each key is an account ID, and the value is the expend limit for that account.
        """
        self._income = income
        self._categories = categories

    def get_income(self) -> float:
        """Returns the monthly income of the budget.

        Returns:
            The monthly income.
        """
        return self._income

    def get_expend_limit(self, id: int) -> float:
        """Returns the expend limit for a given category.

        Arguments
        ---------
            id: `int`
                The category ID.

        Returns:
            The expend limit for the given category.
        """

        return self._categories[id]

    def to_dict(self) -> dict:
        """Returns the budget as a dictionary.

        Returns:
            A dictionary with the budget data.
        """
        return {"income": self._income, "categories": self._categories}
