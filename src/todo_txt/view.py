"""Módulo para la visualización de tareas en consola usando rich."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.text import Text

from todo_txt.model.task import TodoTask

# Definición de columnas disponibles
AVAILABLE_COLUMNS = [
    "id",
    "done",
    "priority",
    "completion_date",
    "creation_date",
    "description",
    "projects",
    "contexts",
    "tags",
]

# Configuración de estilos para prioridades
PRIORITY_STYLES = {
    "A": "bold red",
    "B": "bold yellow",
    "C": "bold cyan",
    "D": "bold green",
}


def print_tasks(
    tasks_with_id: list[tuple[int, TodoTask]],
    columns: list[str] | None = None,
) -> None:
    """
    Imprime una tabla bonita con las tareas proporcionadas.

    Args:
        tasks_with_id: Lista de tuplas (id, tarea).
        columns: Lista de nombres de columnas a mostrar. Si es None, muestra todas.

    """
    if not tasks_with_id:
        Console().print("[yellow]No hay tareas para mostrar.[/yellow]")
        return

    columns_to_show = columns or AVAILABLE_COLUMNS
    table = Table(show_header=True, header_style="bold magenta")

    # 1. Configurar las cabeceras de la tabla
    if "id" in columns_to_show:
        table.add_column("ID", justify="right", style="dim")
    if "done" in columns_to_show:
        table.add_column("Done", justify="center")
    if "priority" in columns_to_show:
        table.add_column("Prio", justify="center")
    if "completion_date" in columns_to_show:
        table.add_column("Done Date", justify="center")
    if "creation_date" in columns_to_show:
        table.add_column("Created", justify="center")
    if "description" in columns_to_show:
        table.add_column("Description", overflow="fold")
    if "projects" in columns_to_show:
        table.add_column("Projects", style="blue")
    if "contexts" in columns_to_show:
        table.add_column("Contexts", style="green")
    if "tags" in columns_to_show:
        table.add_column("Tags", style="dim italic")

    # 2. Rellenar las filas
    for task_id, task in tasks_with_id:
        row_data = []
        style = "dim" if task.is_completed else ""

        if "id" in columns_to_show:
            row_data.append(str(task_id))

        if "done" in columns_to_show:
            row_data.append("[green]x[/green]" if task.is_completed else "[red]o[/red]")

        if "priority" in columns_to_show:
            prio = task.priority or "-"
            prio_style = PRIORITY_STYLES.get(prio, "")
            row_data.append(Text(prio, style=prio_style))

        if "completion_date" in columns_to_show:
            row_data.append(
                task.completion_date.isoformat() if task.completion_date else "-"
            )

        if "creation_date" in columns_to_show:
            row_data.append(
                task.creation_date.isoformat() if task.creation_date else "-"
            )

        if "description" in columns_to_show:
            desc_text = Text(task.description, style=style)
            row_data.append(desc_text)

        if "projects" in columns_to_show:
            row_data.append(" ".join(task.projects))

        if "contexts" in columns_to_show:
            row_data.append(" ".join(task.contexts))

        if "tags" in columns_to_show:
            tags_str = " ".join([f"{k}:{v}" for k, v in task.special_tags.items()])
            row_data.append(tags_str)

        table.add_row(*row_data)

    Console().print(table)
