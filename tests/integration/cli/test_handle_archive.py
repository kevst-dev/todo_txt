"""Tests de integración para el comando 'archive' de la CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from todo_txt.cli.main import main


def test_handle_archive_tasks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifica que el comando archive mueve tareas completadas a done.txt."""
    # 1. Preparar archivos
    todo_path = tmp_path / "todo.txt"
    done_path = tmp_path / "done.txt"

    # Tareas: una pendiente, una completada
    todo_content = (
        "2026-03-04 Tarea pendiente\nx 2026-03-04 2026-03-04 Tarea terminada\n"
    )
    todo_path.write_text(todo_content)
    done_path.touch()

    # 2. Ejecutar archive
    args = [
        "--todo-file",
        str(todo_path),
        "--done-file",
        str(done_path),
        "archive",
    ]
    main(args)

    # 3. Verificaciones
    captured = capsys.readouterr()
    assert "Se han archivado 1 tareas" in captured.out

    # a. todo.txt solo debe tener la pendiente
    todo_lines = todo_path.read_text().strip().split("\n")
    assert len(todo_lines) == 1
    assert "Tarea pendiente" in todo_lines[0]
    assert "x " not in todo_lines[0]

    # b. done.txt debe tener la terminada
    done_lines = done_path.read_text().strip().split("\n")
    assert len(done_lines) == 1
    assert "Tarea terminada" in done_lines[0]


def test_handle_archive_empty(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifica que no ocurra nada si no hay tareas completadas."""
    todo_path = tmp_path / "todo.txt"
    done_path = tmp_path / "done.txt"

    todo_path.write_text("Tarea pendiente solamente\n")
    done_path.touch()

    main(["--todo-file", str(todo_path), "--done-file", str(done_path), "archive"])

    captured = capsys.readouterr()
    assert "No hay tareas completadas para archivar" in captured.out

    # Archivos deben estar igual
    assert len(todo_path.read_text().strip().split("\n")) == 1
    assert done_path.read_text() == ""
