from rich.console import Console
from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich.table import Table
from core.transaction import Transaction
import time
from core.cli.utils import should_run_initial_config, save_user_data, load_user_data
from core.users.user import User

console = Console()

# * Global vars
running: bool = True
user: User = None


# Initial config
def initial_config():
    console.rule("[bold cyan] Initial Config")
    name = Prompt.ask("[bold yellow]What's your first name?")
    surname = Prompt.ask("[bold yellow]What's your surname?")

    new_user = User(name, surname, [])

    # Save user
    with console.status("[bold cyan]Saving info...", spinner="arc"):
        save_user_data(new_user)

    console.print("[bold green]Información guardada con éxito!")
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
    accounts_table = Table("Account Name", "Balance", "Currency", title="Accounts")
    accounts_table.expand = True

    for account in user.accounts:
        accounts_table.add_row(account.name, account.balance, "HNL")

    console.rule("[bold cyan] Main Menu")
    console.print(
        f"[bold cyan]Welcome, [bold yellow]{user.name} {user.surname}[/bold yellow]!\n"
    )
    console.print(accounts_table)
    console.print(
        """\n
1. Add Expense
2. Add Income
3. Manage Accounts
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
