"""Lógica del subcomando 'edit' de la CLI."""

from __future__ import annotations

import argparse

from rich.console import Console

from todo_txt.model.task import TodoTask
from todo_txt.repository import TodoRepository


def handle_edit(args: argparse.Namespace) -> None:
    """Procesa el subcomando 'edit'."""
    repo = TodoRepository(args.todo_file, args.done_file)
    todo_list = repo.load_todo()

    try:
        # 1. Validar existencia
        old_task = todo_list.get_task(args.id)

        # 2. Parsear nuevo texto como una TodoTask
        new_task = TodoTask.parse(args.text)

        # 3. Actualizar y guardar en memoria
        todo_list.update_task(args.id, new_task)

        # 4. Persistir cambios en disco
        repo.save_todo(todo_list)

        # 5. Feedback visual
        console = Console()
        msg = " ".join(
            [
                "\n[bold green]✓[/bold green]",
                "Tarea",
                f"[bold cyan]{args.id}[/bold cyan]",
                "actualizada exitosamente.\n",
            ]
        )
        console.print(msg)
        console.print(f"[dim]Anterior:  {old_task}[/dim]")
        console.print(f"[bold white]Nueva:     {new_task}[/bold white]\n")

    except IndexError:
        Console().print(
            f"\n[bold red]Error:[/] No existe la tarea con ID [bold]{args.id}[/bold]\n"
        )
    except ValueError as e:
        Console().print(f"\n[bold red]Error al parsear la tarea:[/] {e}\n")
