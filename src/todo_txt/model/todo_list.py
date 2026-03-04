"""Gestión de colecciones de tareas todo.txt."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, NamedTuple

from todo_txt.model.task import TodoTask

# Usamos TYPE_CHECKING para importar TaskFilter solo durante el análisis de tipos.
# Esto evita una importación circular, ya que 'filters.py' a su vez podría
# necesitar tipos definidos en este módulo en el futuro.
if TYPE_CHECKING:
    from todo_txt.model.filters import TaskFilter


class TaskEntry(NamedTuple):
    """
    Representa una tarea vinculada a su posición física en el archivo.

    Esta clase es un contenedor inmutable (basado en tupla) que asocia
    una instancia de TodoTask con su identificador de línea (ID). Se utiliza
    principalmente para transportar información entre la lógica de negocio
    (TodoList) y las capas de presentación (View) o persistencia (Repository).

    Atributos:
        id: El número de línea de la tarea en el archivo todo.txt (1-based).
            Este ID es dinámico y corresponde a la posición actual en la lista.
        task: La instancia de TodoTask que contiene los datos parseados
            (descripción, prioridad, fechas, etc.).
    """

    id: int
    task: TodoTask


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

    def list_all(self) -> list[TaskEntry]:
        """Devuelve todas las tareas válidas vinculadas a su ID de línea actual."""
        return [
            TaskEntry(id=i + 1, task=task)
            for i, task in enumerate(self._tasks)
            if task is not None
        ]

    def filter(self, *, is_completed: bool | None = None) -> list[TaskEntry]:
        """
        Filtra las tareas por su estado de completitud.

        Args:
            is_completed: Si es True, solo terminadas. Si es False, solo pendientes.
                          Si es None (por defecto), devuelve todas.

        Returns:
            Una lista de TaskEntry que cumplen con el criterio de filtrado.

        """
        all_entries = self.list_all()
        if is_completed is None:
            return all_entries
        return [e for e in all_entries if e.task.is_completed == is_completed]

    def find(self, task_filter: TaskFilter) -> list[TaskEntry]:
        """
        Busca tareas que coincidan con un filtro complejo.

        Este método centraliza la lógica de búsqueda, permitiendo desacoplar
        la estructura interna de la lista de los criterios de filtrado
        (objetos TaskFilter). Conserva siempre los IDs originales.

        Args:
            task_filter: Objeto que encapsula la lógica de comparación.

        Returns:
            Lista de TaskEntry que satisfacen el filtro.

        """
        return [entry for entry in self.list_all() if task_filter.matches(entry.task)]

    def __len__(self) -> int:
        """Devuelve el número total de líneas (incluyendo vacías)."""
        return len(self._tasks)

    def __iter__(self) -> Iterable[TodoTask]:
        """Itera solo sobre las tareas válidas."""
        return (task for task in self._tasks if task is not None)
