"""Tests de integración para el motor de búsqueda (Lark + TodoList + Repository)."""

from __future__ import annotations

from pathlib import Path

from todo_txt.parser.filter_parser import parse_filter
from todo_txt.repository import TodoRepository
from todo_txt.view import print_tasks


def test_integration_full_search_flow() -> None:
    """Prueba el flujo completo: query string -> filtros -> TodoList -> tabla."""
    # 1. Cargar datos de prueba reales (desde tests/integration/data/)
    todo_path = Path("tests/integration/data/todo.txt")
    done_path = Path("tests/integration/data/done.txt")
    repository = TodoRepository(todo_path, done_path)
    todo_list = repository.load_todo()

    # 2. Definir una búsqueda compleja con Lark
    # Queremos: (Proyectos uniandes O personal) Y NO completadas
    # query = "(project == 'uniandes' OR project == 'personal') AND NOT done == True"
    # query = "(project == 'uniandes') AND NOT done == True"
    query = "\n".join(
        [
            # "project == 'uniandes' AND",
            # "context != 'proyecto_notas' AND",
            # "priority != 'D' AND",
            # "priority >= E AND",
            # "priority != '' AND",
            # "tag.wait != '' AND",
            "tag.due != '' AND",
            "NOT done == True",
        ]
    )

    # 3. Parsear la expresión a objetos TaskFilter
    task_filter = parse_filter(query)

    # 4. Validar que el parser generó la estructura correcta
    # assert isinstance(task_filter, AndFilter)
    # assert isinstance(task_filter.filters[0], OrFilter)
    # assert isinstance(task_filter.filters[1], NotFilter)

    # 5. Ejecutar la búsqueda en la TodoList
    # TODO: Implementar find() en TodoList para simplificar esto
    results = [
        entry for entry in todo_list.list_all() if task_filter.matches(entry.task)
    ]

    # 6. Validaciones de resultados
    # Sabemos que hay muchas tareas de uniandes y personal pendientes en el archivo.
    # assert len(results) > 0

    # Todas las encontradas deben cumplir el criterio
    """
    for entry in results:
        assert not entry.task.is_completed
        assert "uniandes" in entry.task.projects or "personal" in entry.task.projects
    """
    # 7. Visualizar para confirmar visualmente
    print(f"\nResultados para el query: {query}")
    print_tasks(results)
