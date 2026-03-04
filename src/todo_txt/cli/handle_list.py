"""Lógica de los comandos de la CLI."""

from __future__ import annotations

import argparse

from todo_txt.model.filters import CompletedFilter
from todo_txt.parser.filter_parser import parse_filter
from todo_txt.repository import TodoRepository
from todo_txt.view import print_tasks


def handle_list(args: argparse.Namespace) -> None:
    """Procesa el subcomando 'list'."""
    repo = TodoRepository(args.todo_file, args.done_file)
    todo_list = repo.load_todo()

    # 1. Aplicar filtro de Lark si existe
    if args.filter:
        task_filter = parse_filter(args.filter)
        entries = todo_list.find(task_filter)
    else:
        entries = todo_list.list_all()

    # 2. Filtrar por estado si no se pidió '--all'
    if not args.all:
        pending_filter = CompletedFilter(is_completed=False)
        entries = [e for e in entries if pending_filter.matches(e.task)]

    # 3. Imprimir resultados
    print_tasks(tasks_with_id=entries, columns=args.columns)
