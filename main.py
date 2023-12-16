from rich.console import Console
from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich.table import Table
from user import User
import os
import time
import finance
from transaction import Transaction

console = Console()
# Comprobar si se debe iniciar la configuracion inicial

data_path = os.path.join(os.path.expanduser("~"), ".pyfinance")


def initial_config():
    # Configuracion inicial cuando se abre el programa por primera vez
    console.rule("[bold cyan] Configuración Inicial")
    name = Prompt.ask("[bold yellow]Ingrese su primer nombre")
    surname = Prompt.ask("[bold yellow]Ingrese su apellido: ")

    new_user = User(1, name, surname, [])
    # Guardar nueva informacion dentro de la carpeta de datos

    with console.status("[bold cyan]Guardando información...", spinner="arc"):
        time.sleep(1.5)
        finance.write_user_data(new_user)

    console.print("[bold green]Información guardada con éxito!")


if not os.path.exists(data_path):
    with console.status(
        "[bold red]No se pudo encontrar la carpeta de datos. Creando...",
        spinner="arc",
    ):
        time.sleep(1.5)

        console.print("[bold green]Carpeta creada con éxito!")
        console.input("Presione enter para continuar...")
        console.clear()


if not "finances.bin" in os.listdir(data_path):
    initial_config()

running: bool = True

user = None
try:
    user = finance.load_user_data()
except:
    console.print(
        "[bold red]HA OCURRIDO UN ERROR LEYENDO LOS DATOS GUARDADOS.\nSe ejecutará la configuración inicial de nuevo"
    )
    console.input("[bold cyan]Presione enter para continuar.")
    initial_config()
    user = finance.load_user_data()

while running:
    accounts_table = Table("Nombre", "Saldo", "Moneda", title="Cuentas")
    accounts_table.expand = True

    for account in user.accounts:
        accounts_table.add_row(account.name, account.balance, "HNL")

    console.rule("[bold cyan] Menú Principal")
    console.print(
        f"[bold cyan]Bienvenido, [bold yellow]{user.name} {user.surname}[/bold yellow]!\n"
    )
    console.print(accounts_table)
    console.print(
        """\n
1. Agregar Gasto
2. Agregar Ingreso
3. Administrar Cuentas
"""
    )
    op = int(
        Prompt.ask(
            "[bold yellow]Ingrese la opción que desea realizar ",
            choices=["1", "2", "3"],
        )
    )
    console.log(op)
    console.log(type(op))

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
