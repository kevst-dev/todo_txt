"""Tests de integración para el comando 'add' de la CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from todo_txt.cli.main import main


def test_handle_add_task(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verifica que el comando add añade una tarea y guarda el archivo."""
    # 1. Rutas temporales
    todo_path = tmp_path / "todo.txt"
    done_path = tmp_path / "done.txt"
    todo_path.touch()

    # 2. Argumentos para añadir una tarea
    task_text = "(A) Comprar café @mercado +compras"
    args = [
        "--todo-file",
        str(todo_path),
        "--done-file",
        str(done_path),
        "add",
        task_text,
    ]

    # 3. Ejecutamos
    main(args)

    # 4. Verificaciones
    captured = capsys.readouterr()
    assert "Tarea añadida exitosamente" in captured.out
    assert "ID: 1" in captured.out

    content = todo_path.read_text().strip()
    # El parser normaliza el orden (proyectos antes de contextos)
    assert "2026-03-04" in content
    assert "(A) Comprar café" in content
    assert "+compras" in content
    assert "@mercado" in content


def test_handle_add_preserves_provided_date(tmp_path: Path) -> None:
    """Verifica que no se duplique la fecha si el usuario ya provee una."""
    todo_path = tmp_path / "todo.txt"
    todo_path.touch()

    task_text = "2026-01-01 Tarea vieja"
    args = ["--todo-file", str(todo_path), "add", task_text]

    main(args)

    content = todo_path.read_text().strip()
    assert content == task_text


def test_handle_add_multiple_tasks_and_ids(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifica que los IDs se incrementen correctamente al añadir varias tareas."""
    todo_path = tmp_path / "todo.txt"
    todo_path.touch()

    # Añadir primera tarea
    main(["--todo-file", str(todo_path), "add", "Tarea 1"])
    # Añadir segunda tarea
    main(["--todo-file", str(todo_path), "add", "Tarea 2"])

    captured = capsys.readouterr()
    assert "ID: 1" in captured.out
    assert "ID: 2" in captured.out

    lines = todo_path.read_text().strip().split("\n")
    assert len(lines) == 2
    assert "Tarea 1" in lines[0]
    assert "Tarea 2" in lines[1]
