"""Módulo para la visualización de tareas en consola usando rich."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.text import Text

from todo_txt.model.todo_list import TaskEntry

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


def _get_priority_sort_key(entry: TaskEntry) -> tuple[int, int]:
    """Ordena por prioridad (A=1 más alto) y luego por ID."""
    prio = entry.task.priority
    if prio is None:
        return (27, entry.id)
    return (ord(prio) - ord("A") + 1, entry.id)


def print_tasks(
    tasks_with_id: list[TaskEntry],
    columns: list[str] | None = None,
) -> None:
    """
    Imprime una tabla bonita con las tareas proporcionadas.

    Args:
        tasks_with_id: Lista de objetos TaskEntry (id + tarea).
        columns: Lista de nombres de columnas a mostrar. Si es None, muestra todas.

    """
    if not tasks_with_id:
        Console().print("[yellow]No hay tareas para mostrar.[/yellow]")
        return

    console = Console()
    console.print("\n[bold cyan]📋 LISTA DE TAREAS[/bold cyan]")

    # Normalizar columnas (manejar si vienen como una sola cadena con espacios)
    if columns:
        columns_to_show = []
        for col in columns:
            columns_to_show.extend(col.lower().split())
    else:
        columns_to_show = AVAILABLE_COLUMNS

    table = Table(show_header=True, header_style="bold magenta")

    # 1. Configurar las cabeceras de la tabla (en el orden solicitado)
    # Usamos un mapa para mantener la coherencia
    column_map = {
        "id": ("ID", {"justify": "right", "style": "dim"}),
        "done": ("Done", {"justify": "center"}),
        "priority": ("Prio", {"justify": "center"}),
        "completion_date": ("Done Date", {"justify": "center"}),
        "creation_date": ("Created", {"justify": "center"}),
        "description": ("Description", {"overflow": "fold"}),
        "projects": ("Projects", {"style": "blue"}),
        "contexts": ("Contexts", {"style": "green"}),
        "tags": ("Tags", {"style": "dim italic"}),
    }

    actual_columns = []
    for col_name in columns_to_show:
        if col_name in column_map:
            label, kwargs = column_map[col_name]
            table.add_column(label, **kwargs)
            actual_columns.append(col_name)

    # 2. Rellenar las filas
    tasks_with_id = sorted(tasks_with_id, key=_get_priority_sort_key)
    for entry in tasks_with_id:
        task_id = entry.id
        task = entry.task
        row_data = []
        style = "dim" if task.is_completed else ""

        for col_name in actual_columns:
            match col_name:
                case "id":
                    row_data.append(str(task_id))
                case "done":
                    val = "[green]x[/green]" if task.is_completed else "[red]o[/red]"
                    row_data.append(val)
                case "priority":
                    prio = task.priority or "-"
                    prio_style = PRIORITY_STYLES.get(prio, "")
                    row_data.append(Text(prio, style=prio_style))
                case "completion_date":
                    val = (
                        task.completion_date.isoformat()
                        if task.completion_date
                        else "-"
                    )
                    row_data.append(val)
                case "creation_date":
                    val = task.creation_date.isoformat() if task.creation_date else "-"
                    row_data.append(val)
                case "description":
                    row_data.append(Text(task.description, style=style))
                case "projects":
                    row_data.append(" ".join(task.projects))
                case "contexts":
                    row_data.append(" ".join(task.contexts))
                case "tags":
                    tags_str = " ".join(
                        [f"{k}:{v}" for k, v in task.special_tags.items()]
                    )
                    row_data.append(tags_str)

        table.add_row(*row_data)

    console.print(table)

    console.print(
        f"[dim]Total de tareas: [bold white]{len(tasks_with_id)}[/bold white][/dim]\n"
    )
