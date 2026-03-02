"""Gestión de colecciones de tareas todo.txt."""

from __future__ import annotations

from collections.abc import Iterable

from todo_txt.model.task import TodoTask


class TodoList:
    """Representa una lista de tareas cargada en memoria."""

    def __init__(self, tasks: list[TodoTask | None] | None = None) -> None:
        """Inicializa la lista con tareas opcionales."""
        # La lista mantiene el orden físico (las líneas del archivo)
        self._tasks: list[TodoTask | None] = tasks or []

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> TodoList:
        """Crea una TodoList preservando la posición original de cada línea."""
        tasks: list[TodoTask | None] = []
        for line in lines:
            line_str = line.strip()
            if line_str:
                tasks.append(TodoTask.parse(line_str))
            else:
                # Guardamos None para preservar el número de línea como ID
                tasks.append(None)
        return cls(tasks)

    def get_task(self, task_id: int) -> TodoTask:
        """Obtiene una tarea por su ID (1-based index)."""
        idx = task_id - 1
        if 0 <= idx < len(self._tasks):
            task = self._tasks[idx]
            if task is not None:
                return task
        msg = f"No existe la tarea con ID {task_id}"
        raise IndexError(msg)

    def add_task(self, task: TodoTask) -> int:
        """Añade una tarea al final y devuelve su ID."""
        self._tasks.append(task)
        return len(self._tasks)

    def remove_task(self, task_id: int) -> TodoTask:
        """Elimina físicamente una tarea (o línea vacía) por su ID y la devuelve."""
        idx = task_id - 1
        if 0 <= idx < len(self._tasks):
            task = self._tasks.pop(idx)
            if task is not None:
                return task
            # Si era una línea vacía (None), lanzamos error
            msg = f"La línea {task_id} estaba vacía"
            raise ValueError(msg)
        msg = f"No se puede eliminar: ID {task_id} no encontrado"
        raise IndexError(msg)

    def compact(self) -> None:
        """Elimina todos los huecos (None) de la lista, reasignando IDs."""
        self._tasks = [t for t in self._tasks if t is not None]

    def update_task(self, task_id: int, new_task: TodoTask) -> None:
        """Reemplaza la tarea en la posición indicada."""
        idx = task_id - 1
        if 0 <= idx < len(self._tasks):
            self._tasks[idx] = new_task
        else:
            msg = f"No se puede actualizar: ID {task_id} no encontrado"
            raise IndexError(msg)

    def list_all(self) -> list[tuple[int, TodoTask]]:
        """Devuelve todas las tareas válidas con su ID de línea original."""
        return [(i + 1, task) for i, task in enumerate(self._tasks) if task is not None]

    def filter(self, *, is_completed: bool | None = None) -> list[tuple[int, TodoTask]]:
        """
        Filtra las tareas por su estado de completitud.

        Args:
            is_completed: Si es True, solo terminadas. Si es False, solo pendientes.
                         Si es None (por defecto), devuelve todas.

        """
        all_tasks = self.list_all()
        if is_completed is None:
            return all_tasks
        return [(tid, t) for tid, t in all_tasks if t.is_completed == is_completed]

    def __len__(self) -> int:
        """Devuelve el número total de líneas (incluyendo vacías)."""
        return len(self._tasks)

    def __iter__(self) -> Iterable[TodoTask]:
        """Itera solo sobre las tareas válidas."""
        return (task for task in self._tasks if task is not None)
