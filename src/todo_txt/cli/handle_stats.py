"""Lógica del subcomando 'stats' de la CLI."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from todo_txt.model.todo_list import TodoList
from todo_txt.repository import TodoRepository


def handle_stats(args: argparse.Namespace) -> None:
    """Procesa el subcomando 'stats'."""
    repo = TodoRepository(args.todo_file, args.done_file)
    todo_list = repo.load_todo()

    # Si no hay subcomando o es 'summary', mostramos el resumen
    match args.subcommand:
        case "summary" | None:
            _show_summary(todo_list)
        case _:
            # Por si añadimos otros subcomandos después
            Console().print(
                f"[red]Error: Subcomando '{args.subcommand}' no reconocido.[/]"
            )


def _show_summary(todo_list: TodoList) -> None:
    """Muestra un resumen analítico con Rich."""
    all_entries = todo_list.list_all()
    total_tasks = len(all_entries)

    # Agregación
    completed_count = sum(1 for e in all_entries if e.task.is_completed)
    pending_count = total_tasks - completed_count

    project_context_map: dict[str, Counter[str]] = defaultdict(Counter)
    project_total_tasks: Counter[str] = Counter()

    for entry in all_entries:
        task = entry.task
        projects = task.projects or ["(sin proyecto)"]
        contexts = task.contexts or ["(sin contexto)"]

        for p in projects:
            project_total_tasks[p] += 1
            for c in contexts:
                project_context_map[p][c] += 1

    console = Console()

    # --- 1. Dashboard Global (Panel más compacto) ---
    summary_table = Table.grid(padding=(0, 2))
    summary_table.add_column(style="bold white")
    summary_table.add_column(style="bold cyan", justify="right")

    summary_table.add_row("Total Tareas:", str(total_tasks))
    summary_table.add_row("[green]Completadas:[/]", str(completed_count))
    summary_table.add_row("[yellow]Pendientes:[/]", str(pending_count))

    console.print(
        Panel(
            summary_table,
            title="[bold magenta]📊 ESTADÍSTICAS[/]",
            border_style="magenta",
            expand=False,  # No se expande a todo el ancho
        )
    )

    # --- 2. Árbol de Proyectos (Más limpio) ---
    tree = Tree("[bold underline white]ESTRUCTURA DE TRABAJO[/]")

    # Ordenar por importancia (cantidad de tareas)
    for project, total in project_total_tasks.most_common():
        p_node = tree.add(f"[bold cyan]+{project}[/] [dim]({total} tareas)[/]")

        for context, count in project_context_map[project].most_common():
            # Usamos una representación más minimalista
            p_node.add(f"[yellow]@{context}[/] [dim]·[/] [white]{count}[/]")

    console.print(tree)
    console.print("\n")
