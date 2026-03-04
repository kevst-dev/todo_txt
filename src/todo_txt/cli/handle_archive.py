"""Lógica del subcomando 'archive' de la CLI."""

from __future__ import annotations

import argparse

from rich.console import Console

from todo_txt.repository import TodoRepository


def handle_archive(args: argparse.Namespace) -> None:
    """Procesa el subcomando 'archive'."""
    repo = TodoRepository(args.todo_file, args.done_file)
    todo_list = repo.load_todo()

    # 1. Ejecutar el archivado
    archived_count = repo.archive_completed(todo_list)

    # 2. Feedback visual
    console = Console()
    if archived_count > 0:
        msg = " ".join(
            [
                "\n[bold green]✓[/bold green]",
                f"Se han archivado [bold cyan]{archived_count}[/bold cyan]",
                "tareas en",
                f"[dim]{args.done_file}[/dim]\n",
            ]
        )
        console.print(msg)
    else:
        console.print("\n[yellow]⚠[/yellow] No hay tareas completadas para archivar.\n")
