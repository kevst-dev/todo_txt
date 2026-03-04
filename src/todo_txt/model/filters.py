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

    def __init__(self, project: str, operator: str = "==") -> None:
        """
        Inicializa el filtro con el nombre del proyecto y operador.

        Si project es "", busca tareas sin proyectos asociados.
        """
        self.project = project
        self.operator = operator

    def matches(self, task: TodoTask) -> bool:
        """Verifica si la tarea cumple el criterio de proyecto."""
        if self.project == "":
            has_no_projects = len(task.projects) == 0
            return has_no_projects if self.operator == "==" else not has_no_projects

        is_present = self.project in task.projects
        if self.operator == "==":
            return is_present
        if self.operator == "!=":
            return not is_present
        return False


class ContextFilter(TaskFilter):
    """Filtra tareas que pertenecen a un contexto específico (@contexto)."""

    def __init__(self, context: str, operator: str = "==") -> None:
        """
        Inicializa el filtro con el nombre del contexto y operador.

        Si context es "", busca tareas sin contextos asociados.
        """
        self.context = context
        self.operator = operator

    def matches(self, task: TodoTask) -> bool:
        """Verifica si la tarea cumple el criterio de contexto."""
        if self.context == "":
            has_no_contexts = len(task.contexts) == 0
            return has_no_contexts if self.operator == "==" else not has_no_contexts

        is_present = self.context in task.contexts
        if self.operator == "==":
            return is_present
        if self.operator == "!=":
            return not is_present
        return False


class PriorityFilter(TaskFilter):
    """
    Filtra tareas por su nivel de prioridad (A-Z).

    IMPORTANTE: En todo.txt, la prioridad 'A' es MAYOR que 'B'.
    Por lo tanto, 'priority >= B' devolverá tareas con prioridad A y B.
    Si priority es "", busca tareas sin prioridad asignada.
    """

    def __init__(self, priority: str, operator: str = "==") -> None:
        """Inicializa el filtro con la letra de prioridad y operador."""
        self.priority = priority.upper() if priority else ""
        self.operator = operator

    def matches(self, task: TodoTask) -> bool:
        """Verifica si la tarea cumple el criterio de prioridad."""
        if self.priority == "":
            is_empty = task.priority is None
            return is_empty if self.operator == "==" else not is_empty

        if task.priority is None:
            # Una tarea sin prioridad es menor que cualquier prioridad A-Z
            return self.operator == "!="

        tp = task.priority.upper()
        sp = self.priority

        # Lógica de comparación (Invertida alfabéticamente: A > B)
        if self.operator == "==":
            return tp == sp
        if self.operator == "!=":
            return tp != sp
        if self.operator == ">":
            return tp < sp
        if self.operator == ">=":
            return tp <= sp
        if self.operator == "<":
            return tp > sp
        if self.operator == "<=":
            return tp >= sp

        return False


class CompletedFilter(TaskFilter):
    """Filtra tareas según su estado de completitud (x)."""

    def __init__(self, is_completed: bool, operator: str = "==") -> None:
        """Inicializa el filtro con el estado deseado y operador."""
        self.is_completed = is_completed
        self.operator = operator

    def matches(self, task: TodoTask) -> bool:
        """Verifica si el estado de la tarea coincide."""
        matches_state = task.is_completed == self.is_completed
        if self.operator == "==":
            return matches_state
        if self.operator == "!=":
            return not matches_state
        return False


class TagFilter(TaskFilter):
    """Filtra tareas por etiquetas genéricas (llave:valor)."""

    def __init__(self, key: str, value: str, operator: str = "==") -> None:
        """
        Inicializa el filtro con la clave del tag, el valor esperado y operador.

        Si value es "", busca tareas que no tengan definida esa etiqueta.
        """
        self.key = key
        self.value = value
        self.operator = operator

    def matches(self, task: TodoTask) -> bool:
        """Verifica si la tarea tiene el tag con el valor indicado."""
        # Obtenemos el valor del tag (None si no existe)
        actual_value = task.special_tags.get(self.key)

        if self.value == "":
            # Caso: Buscar tareas SIN este tag
            is_missing = actual_value is None
            return is_missing if self.operator == "==" else not is_missing

        if actual_value is None:
            # Si la tarea no tiene el tag, solo coincide si el operador es !=
            return self.operator == "!="

        if self.operator == "==":
            return actual_value == self.value
        if self.operator == "!=":
            return actual_value != self.value

        # Por ahora no soportamos rangos en tags genéricos (ej: wait > 'A')
        return False


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
