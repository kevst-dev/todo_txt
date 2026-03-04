"""Tests de integración para el motor de búsqueda (Lark + TodoList + Repository)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from todo_txt.parser.filter_parser import parse_filter
from todo_txt.repository import TodoRepository
from todo_txt.view import print_tasks


def test_integration_full_search_flow() -> None:
    """Prueba el flujo completo: query string -> filtros -> TodoList -> tabla."""
    # 1. Cargar datos de prueba reales
    todo_path = Path("tests/integration/data/todo.txt")
    done_path = Path("tests/integration/data/done.txt")
    repository = TodoRepository(todo_path, done_path)
    todo_list = repository.load_todo()

    # 2. Búsqueda compleja: Proyecto uniandes Y Prioridad D o mejor Y NO completadas
    query = "project == 'uniandes' AND priority >= 'D' AND NOT done == True"

    print(f"\n--- Ejecutando búsqueda: {query} ---")

    task_filter = parse_filter(query)
    results = todo_list.find(task_filter)

    assert len(results) > 0
    print_tasks(results)


def test_integration_empty_fields() -> None:
    """Prueba la búsqueda de valores vacíos (nulls) usando el string vacío ''."""
    todo_path = Path("tests/integration/data/todo.txt")
    repository = TodoRepository(todo_path, Path("tests/integration/data/done.txt"))
    todo_list = repository.load_todo()

    # Queremos: Proyecto uniandes Y que NO tengan prioridad Y NO completadas
    query = "project == 'uniandes' AND priority == '' AND NOT done == True"

    print(f"\n--- Ejecutando búsqueda de vacíos: {query} ---")

    task_filter = parse_filter(query)
    results = todo_list.find(task_filter)

    # Verificamos que las encontradas realmente no tienen prioridad
    for entry in results:
        assert entry.task.priority is None

    print_tasks(results)


def test_integration_date_filters() -> None:
    """Prueba el filtrado por fechas (created, completed)."""
    todo_path = Path("tests/integration/data/todo.txt")
    repository = TodoRepository(todo_path, Path("tests/integration/data/done.txt"))
    todo_list = repository.load_todo()

    # Queremos: Tareas creadas a partir del 1 de enero de 2026
    target_date_str = "2026-01-02"
    query = f"created >= '{target_date_str}' AND NOT done == True"

    print(f"\n--- Ejecutando búsqueda por fecha: {query} ---")

    task_filter = parse_filter(query)
    results = todo_list.find(task_filter)

    target_date = date.fromisoformat(target_date_str)
    for entry in results:
        assert entry.task.creation_date is not None
        assert entry.task.creation_date >= target_date

    print_tasks(results)


def test_integration_tag_inference() -> None:
    """Prueba la inferencia de tipos en TagFilter (fechas, números)."""
    todo_path = Path("tests/integration/data/todo.txt")
    repository = TodoRepository(todo_path, Path("tests/integration/data/done.txt"))
    todo_list = repository.load_todo()

    # 1. Probar rango de fechas en un tag personalizado (due)
    # Buscamos tareas que venzan ANTES de finales de 2026
    query = "tag.due < '2026-12-31' AND tag.due != '' AND NOT done == True"

    print(f"\n--- Ejecutando búsqueda por rango en TAG (Fecha): {query} ---")

    task_filter = parse_filter(query)
    results = todo_list.find(task_filter)

    assert len(results) > 0
    limit_date = date(2026, 12, 31)
    for entry in results:
        due_val = entry.task.special_tags.get("due")
        assert due_val is not None
        assert date.fromisoformat(due_val) < limit_date

    print_tasks(results)
