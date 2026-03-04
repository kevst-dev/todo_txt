"""Lógica del subcomando 'add' de la CLI."""

from __future__ import annotations

import argparse
from datetime import date

from rich.console import Console

from todo_txt.model.task import TodoTask
from todo_txt.repository import TodoRepository


def handle_add(args: argparse.Namespace) -> None:
    """Procesa el subcomando 'add'."""
    repo = TodoRepository(args.todo_file, args.done_file)
    todo_list = repo.load_todo()

    # 1. Preparar el texto de la tarea
    raw_text = args.text.strip()

    # Añadir fecha de creación automáticamente si no existe (estilo todo.txt)
    # El parser de TodoTask maneja el prefijo de fecha, pero aquí nos aseguramos
    # de que si el usuario no la pone, se añada la de hoy.
    current_date = date.today().isoformat()
    if not any(raw_text.startswith(f"{y}") for y in range(2000, 2900)):
        raw_text = f"{current_date} {raw_text}"

    # 2. Crear y añadir la tarea
    new_task = TodoTask.parse(raw_text)
    task_id = todo_list.add_task(new_task)

    # 3. Guardar cambios
    repo.save_todo(todo_list)

    # 4. Feedback visual
    console = Console()
    msg = " ".join(
        [
            "\n[bold green]✓[/bold green]",
            "Tarea añadida exitosamente con ID:",
            f"[bold cyan]{task_id}[/bold cyan]",
        ]
    )
    console.print(msg)
    console.print(f"[dim]Contenido: {new_task}[/dim]\n")
