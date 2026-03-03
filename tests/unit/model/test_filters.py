"""Tests para el sistema de filtrado de tareas."""

from __future__ import annotations

import pytest

from todo_txt.model.filters import (
    CompletedFilter,
    ContextFilter,
    PriorityFilter,
    ProjectFilter,
)
from todo_txt.model.task import TodoTask


@pytest.fixture
def sample_task() -> TodoTask:
    """Tarea de prueba con varios metadatos."""
    return TodoTask.parse("(A) Tarea importante +uniandes @oficina")


def test_project_filter(sample_task: TodoTask) -> None:
    """Verifica el filtrado por proyecto (+)."""
    f = ProjectFilter("uniandes")
    assert f.matches(sample_task) is True

    f_other = ProjectFilter("personal")
    assert f_other.matches(sample_task) is False


def test_context_filter(sample_task: TodoTask) -> None:
    """Verifica el filtrado por contexto (@)."""
    f = ContextFilter("oficina")
    assert f.matches(sample_task) is True

    f_other = ContextFilter("hogar")
    assert f_other.matches(sample_task) is False


def test_priority_filter(sample_task: TodoTask) -> None:
    """Verifica el filtrado por prioridad ((A))."""
    f = PriorityFilter("A")
    assert f.matches(sample_task) is True

    f_other = PriorityFilter("B")
    assert f_other.matches(sample_task) is False


def test_completed_filter() -> None:
    """Verifica el filtrado por estado de completitud (x)."""
    task_done = TodoTask.parse("x Tarea hecha")
    task_pending = TodoTask.parse("Tarea pendiente")

    f = CompletedFilter(True)
    assert f.matches(task_done) is True
    assert f.matches(task_pending) is False

    f_pending = CompletedFilter(False)
    assert f_pending.matches(task_done) is False
    assert f_pending.matches(task_pending) is True


def test_and_filter_operator(sample_task: TodoTask) -> None:
    """Verifica la combinación AND mediante el operador '&'."""
    # (Project uniandes) AND (Priority A)
    f = ProjectFilter("uniandes") & PriorityFilter("A")
    assert f.matches(sample_task) is True

    # (Project uniandes) AND (Priority B) -> False
    f_fail = ProjectFilter("uniandes") & PriorityFilter("B")
    assert f_fail.matches(sample_task) is False


def test_or_filter_operator(sample_task: TodoTask) -> None:
    """Verifica la combinación OR mediante el operador '|'."""
    # (Project personal) OR (Priority A) -> True (porque A coincide)
    f = ProjectFilter("personal") | PriorityFilter("A")
    assert f.matches(sample_task) is True

    # (Project personal) OR (Priority B) -> False
    f_fail = ProjectFilter("personal") | PriorityFilter("B")
    assert f_fail.matches(sample_task) is False


def test_not_filter_operator(sample_task: TodoTask) -> None:
    """Verifica la inversión NOT mediante el operador '~'."""
    # NOT (Project personal) -> True (porque no es personal)
    f = ~ProjectFilter("personal")
    assert f.matches(sample_task) is True

    # NOT (Project uniandes) -> False
    f_fail = ~ProjectFilter("uniandes")
    assert f_fail.matches(sample_task) is False


def test_complex_combination(sample_task: TodoTask) -> None:
    """Verifica una combinación lógica anidada compleja."""
    # (Project uniandes OR Project personal) AND (Priority A AND NOT Completed)
    f = (ProjectFilter("uniandes") | ProjectFilter("personal")) & (
        PriorityFilter("A") & ~CompletedFilter()
    )

    assert f.matches(sample_task) is True

    # Modificamos para que falle: Prioridad B
    f_fail = (ProjectFilter("uniandes") | ProjectFilter("personal")) & (
        PriorityFilter("B") & ~CompletedFilter()
    )
    assert f_fail.matches(sample_task) is False
