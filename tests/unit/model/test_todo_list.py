"""Tests para la gestión de TodoList."""

from __future__ import annotations

import pytest

from todo_txt.model.task import TodoTask
from todo_txt.model.todo_list import TodoList


def test_todo_list_from_lines() -> None:
    lines = [
        "(A) Tarea 1",
        "x 2026-02-27 Tarea 2",
        "Tarea 3 @home",
    ]
    todo_list = TodoList.from_lines(lines)

    assert len(todo_list) == 3
    assert todo_list.get_task(1).priority == "A"
    assert todo_list.get_task(2).is_completed is True
    assert "@home" in str(todo_list.get_task(3))


def test_add_and_get_by_id() -> None:
    todo_list = TodoList()
    task = TodoTask.parse("Nueva tarea")
    new_id = todo_list.add_task(task)

    assert new_id == 1
    assert todo_list.get_task(1).description == "Nueva tarea"


def test_remove_by_id() -> None:
    todo_list = TodoList.from_lines(["T1", "T2", "T3"])
    removed = todo_list.remove_task(2)  # Eliminamos T2

    assert removed.description == "T2"
    assert len(todo_list) == 2
    # El ID 2 ahora debería ser T3 (esto es comportamiento estándar CLI)
    assert todo_list.get_task(2).description == "T3"


def test_update_by_id() -> None:
    todo_list = TodoList.from_lines(["Tarea vieja"])
    new_task = TodoTask.parse("Tarea actualizada")
    todo_list.update_task(1, new_task)

    assert todo_list.get_task(1).description == "Tarea actualizada"


def test_invalid_id_raises_error() -> None:
    todo_list = TodoList.from_lines(["T1"])
    with pytest.raises(IndexError, match="No existe la tarea con ID 99"):
        todo_list.get_task(99)


def test_list_all_with_ids() -> None:
    todo_list = TodoList.from_lines(["T1", "T2"])
    all_tasks = todo_list.list_all()

    assert all_tasks == [(1, todo_list.get_task(1)), (2, todo_list.get_task(2))]
