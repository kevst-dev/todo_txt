"""Lógica del subcomando 'do' de la CLI."""

from __future__ import annotations

import argparse

from rich.console import Console

from todo_txt.repository import TodoRepository


def handle_do(args: argparse.Namespace) -> None:
    """Procesa el subcomando 'do'."""
    repo = TodoRepository(args.todo_file, args.done_file)
    todo_list = repo.load_todo()

    try:
        # 1. Recuperar la tarea
        task = todo_list.get_task(args.id)

        if task.is_completed:
            msg = " ".join(
                [
                    "[yellow]⚠[/yellow]",
                    f"La tarea con ID [bold]{args.id}[/bold]",
                    "ya estaba completada.",
                ]
            )
            Console().print(msg)
            return

        # 2. Marcar como completada
        completed_task = task.complete()
        todo_list.update_task(args.id, completed_task)

        # 3. Guardar cambios
        repo.save_todo(todo_list)

        # 4. Feedback visual
        console = Console()
        msg = " ".join(
            [
                "\n[bold green]✓[/bold green]",
                "Tarea",
                f"[bold cyan]{args.id}[/bold cyan]",
                "marcada como completada.",
            ]
        )
        console.print(msg)
        console.print(f"[dim]Contenido: {completed_task}[/dim]\n")

    except IndexError:
        Console().print(
            f"\n[bold red]Error:[/] No existe la tarea con ID [bold]{args.id}[/bold]\n"
        )
