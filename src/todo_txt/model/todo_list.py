"""Gestión de colecciones de tareas todo.txt."""

from __future__ import annotations

from collections.abc import Iterable

from todo_txt.model.task import TodoTask


class TodoList:
    """Representa una lista de tareas cargada en memoria."""

    def __init__(self, tasks: list[TodoTask] | None = None) -> None:
        """Inicializa la lista con tareas opcionales."""
        # La lista mantiene el orden físico (las líneas del archivo)
        self._tasks: list[TodoTask] = tasks or []

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> TodoList:
        """Crea una TodoList a partir de un iterable de strings."""
        tasks = []
        for line in lines:
            line_str = line.strip()
            if line_str:
                tasks.append(TodoTask.parse(line_str))
            else:
                # Opcional: Podríamos manejar líneas vacías si queremos
                # mantener estrictamente el número de línea.
                # Por ahora, las saltamos pero esto cambiaría el ID.
                # Si queremos ID = línea real, deberíamos guardar un Placeholder.
                continue
        return cls(tasks)

    def get_task(self, task_id: int) -> TodoTask:
        """Obtiene una tarea por su ID (1-based index)."""
        idx = task_id - 1
        if 0 <= idx < len(self._tasks):
            return self._tasks[idx]
        msg = f"No existe la tarea con ID {task_id}"
        raise IndexError(msg)

    def add_task(self, task: TodoTask) -> int:
        """Añade una tarea al final y devuelve su ID."""
        self._tasks.append(task)
        return len(self._tasks)

    def remove_task(self, task_id: int) -> TodoTask:
        """Elimina una tarea por su ID y la devuelve."""
        idx = task_id - 1
        if 0 <= idx < len(self._tasks):
            return self._tasks.pop(idx)
        msg = f"No se puede eliminar: ID {task_id} no encontrado"
        raise IndexError(msg)

    def update_task(self, task_id: int, new_task: TodoTask) -> None:
        """Reemplaza la tarea en la posición indicada."""
        idx = task_id - 1
        if 0 <= idx < len(self._tasks):
            self._tasks[idx] = new_task
        else:
            msg = f"No se puede actualizar: ID {task_id} no encontrado"
            raise IndexError(msg)

    def list_all(self) -> list[tuple[int, TodoTask]]:
        """Devuelve todas las tareas con su ID actual."""
        return [(i + 1, task) for i, task in enumerate(self._tasks)]

    def __len__(self) -> int:
        """Devuelve el número de tareas en la lista."""
        return len(self._tasks)

    def __iter__(self) -> Iterable[TodoTask]:
        """Itera sobre las tareas en la lista."""
        return iter(self._tasks)
