"""Tests de integración para el comando 'edit' de la CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from todo_txt.cli.main import main


def test_handle_edit_task(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verifica que el comando edit actualiza el texto de una tarea."""
    # 1. Preparar archivo con tareas
    todo_path = tmp_path / "todo.txt"
    todo_path.write_text("Tarea 1\nTarea 2\nTarea 3\n")

    # 2. Editar la tarea 2 (ID 2)
    new_text = "(A) Tarea 2 Actualizada @edit +test"
    args = ["--todo-file", str(todo_path), "edit", "2", new_text]
    main(args)

    # 3. Verificaciones
    captured = capsys.readouterr()
    assert "actualizada exitosamente" in captured.out
    assert "Tarea 2 Actualizada" in captured.out

    # El archivo debe tener el texto actualizado en la línea correcta
    lines = todo_path.read_text().strip().split("\n")
    assert len(lines) == 3
    assert lines[0] == "Tarea 1"
    assert "Tarea 2 Actualizada" in lines[1]
    assert lines[2] == "Tarea 3"


def test_handle_edit_non_existent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifica error al editar tarea inexistente."""
    todo_path = tmp_path / "todo.txt"
    todo_path.touch()

    args = ["--todo-file", str(todo_path), "edit", "5", "Nueva"]
    main(args)

    captured = capsys.readouterr()
    assert "Error" in captured.out
    assert "No existe la tarea con ID 5" in captured.out
