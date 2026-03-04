"""Punto de entrada de la interfaz de línea de comandos."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .handle_add import handle_add
from .handle_do import handle_do
from .handle_list import handle_list


def main(argv: list[str] | None = None) -> None:
    """Función principal de la CLI."""
    if not argv:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Gestor de tareas todo.txt avanzado")

    # Flags Globales
    parser.add_argument(
        "--todo-file",
        type=Path,
        default=Path("todo.txt"),
        help="Ruta al archivo todo.txt",
    )
    parser.add_argument(
        "--done-file",
        type=Path,
        default=Path("done.txt"),
        help="Ruta al archivo done.txt",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcomandos")

    # Subcomando 'list'
    list_parser = subparsers.add_parser("list", aliases=["ls"], help="Listar tareas")
    list_parser.add_argument(
        "--filter", type=str, help="Query de búsqueda avanzada (Lark)"
    )
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Mostrar todas las tareas (incluye completadas)",
    )
    list_parser.add_argument("--columns", nargs="+", help="Lista de columnas a mostrar")

    # Subcomando 'add'
    add_parser = subparsers.add_parser("add", help="Añadir una nueva tarea")
    add_parser.add_argument(
        "text", type=str, help="Texto de la tarea (ej: '(A) Mi tarea @casa +familia')"
    )

    # Subcomando 'do'
    do_parser = subparsers.add_parser("do", help="Marcar una tarea como completada")
    do_parser.add_argument("id", type=int, help="ID de la tarea")

    args = parser.parse_args(argv)

    # Pattern Matching para el manejo de comandos
    match args.command:
        case "list" | "ls":
            handle_list(args)
        case "add":
            handle_add(args)
        case "do":
            handle_do(args)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
