"""Lógica del subcomando 'note' de la CLI."""

from __future__ import annotations

import argparse
import os
import subprocess  # nosec B404
from pathlib import Path

from rich.console import Console

from todo_txt.repository import TodoRepository


def handle_note(args: argparse.Namespace) -> None:
    """Procesa el subcomando 'note'."""
    repo = TodoRepository(args.todo_file, args.done_file)
    todo_list = repo.load_todo()

    try:
        # 1. Recuperar la tarea
        task = todo_list.get_task(args.id)

        # 2. Verificar si tiene el tag 'note'
        note_val = task.special_tags.get("note")
        if not note_val:
            msg = " ".join(
                [
                    "\n[bold red]Error:[/] La tarea",
                    f"[bold cyan]{args.id}[/bold cyan]",
                    "no tiene una nota asociada (ej: [dim]note:archivo.md[/dim]).\n",
                ]
            )
            Console().print(msg)
            return

        # 3. Resolver la ruta de la nota
        todo_dir = Path(args.todo_file).parent

        # Comportamiento inteligente de pathlib:
        # Si 'note_val' es una ruta absoluta (empieza por / o C:\), el operador '/'
        # ignora automáticamente 'todo_dir' y devuelve la ruta absoluta tal cual.
        # Si es relativa, la une al directorio donde vive el archivo todo.txt.
        note_path = (todo_dir / note_val).resolve()

        # Asegurar que el directorio de la nota existe (por si se va a crear una nueva)
        note_path.parent.mkdir(parents=True, exist_ok=True)

        # 4. Obtener el editor del sistema ($EDITOR)
        editor = os.environ.get("EDITOR", "nvim")

        # 5. Lanzar el editor
        msg = " ".join(
            [
                "\n[bold green]Abriendo nota:[/]",
                f"[dim]{note_path}[/dim]",
                f"con [bold]{editor}[/bold]...",
            ]
        )
        Console().print(msg)

        # Lanzar el proceso del editor (bloqueante)
        # nosec B603: El comando y el archivo son controlados por el usuario
        subprocess.run([editor, str(note_path)], check=True)  # nosec B603
        Console().print("[bold green]✓[/bold green] Editor cerrado.\n")

    except IndexError:
        Console().print(
            f"\n[bold red]Error:[/] No existe la tarea con ID [bold]{args.id}[/bold]\n"
        )
    except subprocess.CalledProcessError as e:
        Console().print(f"\n[bold red]Error al abrir el editor:[/] {e}\n")
    except Exception as e:
        Console().print(f"\n[bold red]Error inesperado:[/] {e}\n")
