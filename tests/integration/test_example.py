from __future__ import annotations

from pathlib import Path

from todo_txt.model.filters import ProjectFilter
from todo_txt.repository import TodoRepository
from todo_txt.view import AVAILABLE_COLUMNS, print_tasks


def test_integration_example() -> None:
    """Test de integración para visualizar el flujo completo con rich."""
    # Usamos rutas relativas (se asume que existen archivos en data/)
    todo_path = Path("tests/integration/data/todo.txt")
    done_path = Path("tests/integration/data/done.txt")

    # 1. Cargamos el repositorio
    repository = TodoRepository(todo_path, done_path)
    todo_list = repository.load_todo()

    # 2. Visualizamos SOLO las pendientes (usando el método filter antiguo)
    pending_tasks = todo_list.filter(is_completed=False)

    print("\nTareas Pendientes:")
    print_tasks(
        tasks_with_id=pending_tasks,
        columns=AVAILABLE_COLUMNS,
    )

    # 3. Prueba del nuevo sistema de filtros avanzado CONSERVANDO IDs
    print("\nFiltro por proyecto 'uniandes' (CONSERVANDO IDs):")
    task_filter = ProjectFilter("uniandes")

    # Filtramos sobre list_all() para obtener TaskEntries (ID + Task)
    filtered_entries = [
        entry for entry in todo_list.list_all() if task_filter.matches(entry.task)
    ]

    print_tasks(filtered_entries)
