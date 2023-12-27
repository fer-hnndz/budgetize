import time

from rich.console import Console
from rich.prompt import FloatPrompt, IntPrompt, Prompt
from rich.table import Table

from core.accounts.account import Account
from core.cli.utils import load_user_data, save_user_data, should_run_initial_config
from core.Transaction import Transaction
from core.users.user import User
from core.CurrencyManager import CurrencyManager
import core.consts as consts

console = Console()

# * Global vars
running: bool = True
user: User = None


# Initial config
def initial_config():
    # Retrieve exchange rates

    console.rule("[bold cyan]Initial Configuration")
    name = Prompt.ask("[bold yellow]Enter your name")
    base_currency = Prompt.ask(
        "[bold yellow]Enter the symbol of you base currency",
        choices=consts.CURRENCY_SYMBOLS,
        default="USD",
    )

    new_user = User(name=name, base_currency=base_currency, accounts=[])

    # Save user
    with console.status("[bold cyan]Saving info...", spinner="arc"):
        save_user_data(new_user)

    console.print("[bold green]User saved successfully!")
    time.sleep(0.7)


if should_run_initial_config():
    initial_config()

try:
    user = load_user_data()
except:
    console.print(
        "[bold red]THERE WAS AN ERROR TRYING TO RETRIEVE THE USER DATA. RE-RUNNING INITIAL CONFIG..."
    )
    console.input("[bold cyan]Press enter to continue...")
    initial_config()
    user = load_user_data()

while running:
    # Setup accounts table

    exchanges = None
    with console.status(
        "[bold cyan]Retrieving latest exchange rates...", spinner="arc"
    ):
        currencies = CurrencyManager(user.base_currency)
        exchanges = currencies.get_all_exchanges()

    accounts_table = Table("Account Name", "Balance", title="Accounts")
    accounts_table.expand = True

    for account in user.accounts:
        accounts_table.add_row(account.name, "$" + str(account.balance))

    console.rule("[bold cyan] Main Menu")
    console.print(f"[bold cyan]Welcome, [bold yellow]{user.name}[/bold yellow]!\n")
    console.print(accounts_table)
    console.print(
        """\n
1. Add Expense
2. Add Income
3. Create Account
4. Delete Account
"""
    )
    op = int(
        Prompt.ask(
            "[bold yellow]Enter the number of the option you want to select:",
            choices=["1", "2", "3"],
        )
    )
    # console.log(op)
    # console.log(type(op))

    if op == 1:
        if len(user.accounts) == 0:  # Si no hay cuentas, no se puede agregar un gasto
            console.print(
                "[bold red]No se puede agregar un gasto porque no hay cuentas creadas."
            )
            console.input("[bold cyan]Presione enter para continuar.")
            continue

        console.rule("[bold cyan] Agregar Gasto")

        acc_index = -1

        console.clear()
        while acc_index < 0 or acc_index > len(user.accounts):
            for i, acc in enumerate(user.accounts):
                console.print(f"{i+1}. {acc.name} - {acc.balance} HNL")

                acc_index = IntPrompt.ask(
                    "[bold yellow]ngrese el número de la cuenta donde desea agregar el gasto",
                )

                if acc_index < 0 or acc_index > len(user.accounts):
                    console.print(
                        "[bold red]El número de cuenta ingresado no es válido"
                    )

        # Pedir datos
        cuenta_seleccionada = user.accounts[acc_index - 1]

        console.clear()
        console.rule(f"[bold cyan] Agregar Gasto ({cuenta_seleccionada.name})")

        gasto = FloatPrompt.ask(
            "[bold yellow]Ingrese el monto del gasto: ", min_value=0
        )
        descripcion = Prompt.ask("[bold yellow]Ingrese una descripción: ")
        # categoria

        t = Transaction()
    elif op == 3:
        console.rule("[bold cyan]Add Accounts")

        account_name = ""
        while account_name.strip() == "":
            account_name = Prompt.ask(
                "[bold yellow]Enter the name of the account: "
            ).strip()

            if account_name == "":
                console.print("[bold red]The account name cannot be empty.")

        balance: int = -1
        while balance < 0:
            balance = IntPrompt.ask("[bold yellow]Enter the initial balance: ")

            if balance <= 0:
                console.print("[bold red]The initial balance must be atleast 0.")

        # Create account
        new_account = Account(account_name, balance)
        user.accounts.append(new_account)

        with console.status("[bold cyan]Saving info...", spinner="arc"):
            save_user_data(user)

        console.print("[bold green]Account saved successfully!")
        time.sleep(0.7)
