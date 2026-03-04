"""Punto de entrada de la interfaz de línea de comandos."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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

    subparser = parser.add_subparsers(dest="command", help="Subcomandos")

    # Subcomando 'list'
    list_parser = subparser.add_parser("list", help="Listar tareas")
    list_parser.add_argument(
        "--filter", type=str, help="Query de búsqueda avanzada (Lark)"
    )
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Mostrar todas las tareas (incluye completadas)",
    )
    list_parser.add_argument("--columns", nargs="+", help="Lista de columnas a mostrar")

    args = parser.parse_args(argv)

    if args.command in ["list", "ls"]:
        handle_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
