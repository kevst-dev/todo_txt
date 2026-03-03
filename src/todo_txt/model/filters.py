"""Módulo para el filtrado avanzado de tareas mediante el patrón Specification."""

from __future__ import annotations

from abc import ABC, abstractmethod

from todo_txt.model.task import TodoTask


class TaskFilter(ABC):
    """
    Interfaz base para todos los filtros de tareas.

    Permite la composición de filtros complejos utilizando operadores lógicos:
    - '&' para AND
    - '|' para OR
    - '~' para NOT
    """

    @abstractmethod
    def matches(self, task: TodoTask) -> bool:
        """Determina si una tarea cumple con el criterio del filtro."""

    def __and__(self, other: TaskFilter) -> AndFilter:
        """Combina este filtro con otro usando AND."""
        return AndFilter(self, other)

    def __or__(self, other: TaskFilter) -> OrFilter:
        """Combina este filtro con otro usando OR."""
        return OrFilter(self, other)

    def __invert__(self) -> NotFilter:
        """Invierte el resultado de este filtro (NOT)."""
        return NotFilter(self)


# --- Filtros Atómicos (Básicos) ---


class ProjectFilter(TaskFilter):
    """Filtra tareas que pertenecen a un proyecto específico (+proyecto)."""

    def __init__(self, project: str) -> None:
        """Inicializa el filtro con el nombre del proyecto."""
        self.project = project

    def matches(self, task: TodoTask) -> bool:
        """Verifica si la tarea contiene el proyecto."""
        return self.project in task.projects


class ContextFilter(TaskFilter):
    """Filtra tareas que pertenecen a un contexto específico (@contexto)."""

    def __init__(self, context: str) -> None:
        """Inicializa el filtro con el nombre del contexto."""
        self.context = context

    def matches(self, task: TodoTask) -> bool:
        """Verifica si la tarea contiene el contexto."""
        return self.context in task.contexts


class PriorityFilter(TaskFilter):
    """Filtra tareas por su nivel de prioridad (A-Z)."""

    def __init__(self, priority: str) -> None:
        """Inicializa el filtro con la letra de prioridad."""
        self.priority = priority

    def matches(self, task: TodoTask) -> bool:
        """Verifica si la tarea tiene la prioridad exacta."""
        return task.priority == self.priority


class CompletedFilter(TaskFilter):
    """Filtra tareas según su estado de completitud (x)."""

    def __init__(self, is_completed: bool = True) -> None:
        """Inicializa el filtro con el estado deseado (True para hechas)."""
        self.is_completed = is_completed

    def matches(self, task: TodoTask) -> bool:
        """Verifica si el estado de la tarea coincide."""
        return task.is_completed == self.is_completed


# --- Filtros de Composición (Lógicos) ---


class AndFilter(TaskFilter):
    """Combina múltiples filtros: todos deben cumplirse (operación AND)."""

    def __init__(self, *filters: TaskFilter) -> None:
        """Inicializa con una lista de filtros a combinar."""
        self.filters = filters

    def matches(self, task: TodoTask) -> bool:
        """Verifica que todos los filtros internos coincidan."""
        return all(f.matches(task) for f in self.filters)


class OrFilter(TaskFilter):
    """Combina múltiples filtros: al menos uno debe cumplirse (operación OR)."""

    def __init__(self, *filters: TaskFilter) -> None:
        """Inicializa con una lista de filtros a combinar."""
        self.filters = filters

    def matches(self, task: TodoTask) -> bool:
        """Verifica que al menos uno de los filtros internos coincida."""
        return any(f.matches(task) for f in self.filters)


class NotFilter(TaskFilter):
    """Invierte el resultado de un filtro (operación NOT)."""

    def __init__(self, task_filter: TaskFilter) -> None:
        """Inicializa con el filtro que se desea invertir."""
        self.filter = task_filter

    def matches(self, task: TodoTask) -> bool:
        """Verifica que el filtro interno NO coincida."""
        return not self.filter.matches(task)
