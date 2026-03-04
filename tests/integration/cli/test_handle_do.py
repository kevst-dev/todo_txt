"""Tests de integración para el comando 'do' de la CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from todo_txt.cli.main import main


def test_handle_do_task(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verifica que el comando do marca una tarea como completada."""
    # 1. Preparar archivo con una tarea pendiente
    todo_path = tmp_path / "todo.txt"
    todo_path.write_text("2026-03-04 Comprar pan\n")

    # 2. Ejecutar comando do 1
    args = ["--todo-file", str(todo_path), "do", "1"]
    main(args)

    # 3. Verificaciones
    captured = capsys.readouterr()
    assert "marcada como completada" in captured.out
    assert "1" in captured.out

    # El archivo debe tener la 'x' al inicio
    content = todo_path.read_text().strip()
    assert content.startswith("x ")
    assert "Comprar pan" in content


def test_handle_do_non_existent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifica el error al intentar completar una tarea inexistente."""
    todo_path = tmp_path / "todo.txt"
    todo_path.touch()

    args = ["--todo-file", str(todo_path), "do", "99"]
    main(args)

    captured = capsys.readouterr()
    assert "Error" in captured.out
    assert "No existe la tarea con ID 99" in captured.out


def test_handle_do_middle_task(tmp_path: Path) -> None:
    """Verifica que se puede completar una tarea en medio de una lista de varias."""
    todo_path = tmp_path / "todo.txt"
    tasks = [
        "Tarea 1",
        "Tarea 2",
        "Tarea 3",
        "Tarea 4",
    ]
    todo_path.write_text("\n".join(tasks) + "\n")

    # Completar la tarea 3 (ID 3)
    main(["--todo-file", str(todo_path), "do", "3"])

    content_lines = todo_path.read_text().strip().split("\n")

    # Verificaciones:
    assert len(content_lines) == 4
    assert not content_lines[0].startswith("x ")  # Tarea 1 intacta
    assert not content_lines[1].startswith("x ")  # Tarea 2 intacta
    assert content_lines[2].startswith("x ")  # Tarea 3 COMPLETADA
    assert "Tarea 3" in content_lines[2]
    assert not content_lines[3].startswith("x ")  # Tarea 4 intacta
