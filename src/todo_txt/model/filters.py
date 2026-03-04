"""Módulo para el filtrado avanzado de tareas mediante el patrón Specification."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Any, cast

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
    """Filtra tareas por etiquetas genéricas (llave:valor) con inferencia de tipos."""

    def __init__(self, key: str, value: str, operator: str = "==") -> None:
        """
        Inicializa el filtro con la clave del tag, el valor esperado y operador.

        Si value es "", busca tareas que no tengan definida esa etiqueta.
        """
        self.key = key
        self.value = value
        self.operator = operator

    def _coerce_value(self, val: str) -> Any:
        """Intenta inferir el tipo de dato del valor del tag."""
        # 1. Booleanos
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False

        # 2. Fechas (ISO YYYY-MM-DD)
        try:
            return date.fromisoformat(val)
        except ValueError:
            pass

        # 3. Números (float o int)
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            pass

        # 4. Rutas (Si contiene / o es una ruta válida existente)
        if "/" in val or "\\" in val or val.startswith("./"):
            return Path(val)

        # 5. Texto (fallback)
        return val

    def matches(self, task: TodoTask) -> bool:
        """Verifica si la tarea tiene el tag con el valor indicado usando tipos."""
        actual_raw = task.special_tags.get(self.key)

        if self.value == "":
            is_missing = actual_raw is None
            return is_missing if self.operator == "==" else not is_missing

        if actual_raw is None:
            return self.operator == "!="

        # Inferimos tipos para ambos valores
        v_actual = self._coerce_value(actual_raw)
        v_target = self._coerce_value(self.value)

        # Si los tipos no coinciden, comparamos como texto plano
        if type(v_actual) is not type(v_target):
            v_actual, v_target = str(v_actual), str(v_target)

        # Operaciones permitidas según el tipo
        is_range_op = self.operator in (">", ">=", "<", "<=")

        # Booleanos y Paths no soportan rangos (devuelven False)
        if isinstance(v_actual, (bool, Path)) and is_range_op:
            return False

        if self.operator == "==":
            return bool(v_actual == v_target)
        if self.operator == "!=":
            return bool(v_actual != v_target)
        if self.operator == ">":
            return bool(v_actual > v_target)
        if self.operator == ">=":
            return bool(v_actual >= v_target)
        if self.operator == "<":
            return bool(v_actual < v_target)
        if self.operator == "<=":
            return bool(v_actual <= v_target)

        return False


class DateFilter(TaskFilter):
    """Filtra tareas por atributos de fecha (creación, completado)."""

    def __init__(self, attr_name: str, value: str, operator: str = "==") -> None:
        """Inicializa el filtro de fecha."""
        self.attr_name = attr_name
        self.operator = operator
        self.target_date = date.fromisoformat(value) if value != "" else None

    def matches(self, task: TodoTask) -> bool:
        """Compara la fecha de la tarea con la fecha objetivo."""
        # Obtenemos el valor y aseguramos el tipo para Mypy
        actual_val = getattr(task, self.attr_name)
        actual_date = cast(date | None, actual_val)

        if self.target_date is None:
            is_none = actual_date is None
            return is_none if self.operator == "==" else not is_none

        if actual_date is None:
            return self.operator == "!="

        if self.operator == "==":
            return bool(actual_date == self.target_date)
        if self.operator == "!=":
            return bool(actual_date != self.target_date)
        if self.operator == ">":
            return bool(actual_date > self.target_date)
        if self.operator == ">=":
            return bool(actual_date >= self.target_date)
        if self.operator == "<":
            return bool(actual_date < self.target_date)
        if self.operator == "<=":
            return bool(actual_date <= self.target_date)

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
