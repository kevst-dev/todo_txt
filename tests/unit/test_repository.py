"""Tests para el repositorio de archivos todo.txt y done.txt."""

from __future__ import annotations

from pathlib import Path

from todo_txt.model.todo_list import TodoList
from todo_txt.repository import TodoRepository


def test_repository_load_todo_missing_file(tmp_path: Path) -> None:
    """Verifica que si el archivo no existe, se devuelve una lista vacía."""
    repo = TodoRepository(tmp_path / "todo.txt", tmp_path / "done.txt")
    todo_list = repo.load_todo()

    assert len(todo_list) == 0


def test_repository_load_todo_only(tmp_path: Path) -> None:
    """Verifica que load_todo solo carga el archivo todo.txt."""
    todo_file = tmp_path / "todo.txt"
    done_file = tmp_path / "done.txt"

    todo_file.write_text("Tarea 1\n", encoding="utf-8")
    done_file.write_text("x Tarea terminada\n", encoding="utf-8")

    repo = TodoRepository(todo_file, done_file)
    todo_list = repo.load_todo()

    assert len(todo_list) == 1
    assert todo_list.get_task(1).description == "Tarea 1"


def test_repository_save_todo_preserves_blank_lines(tmp_path: Path) -> None:
    """Verifica que save_todo respeta las líneas vacías."""
    todo_file = tmp_path / "todo.txt"
    repo = TodoRepository(todo_file, tmp_path / "done.txt")

    lines = ["Tarea 1", "", "Tarea 3"]
    todo_list = TodoList.from_lines(lines)

    repo.save_todo(todo_list)

    content = todo_file.read_text(encoding="utf-8")
    assert content == "Tarea 1\n\nTarea 3\n"


def test_repository_archive_completed(tmp_path: Path) -> None:
    """Verifica que el archivado mueve tareas de un archivo a otro."""
    todo_file = tmp_path / "todo.txt"
    done_file = tmp_path / "done.txt"

    # Setup: 1 pendiente, 1 completada
    todo_file.write_text("Pendiente\nx Completada\n", encoding="utf-8")

    repo = TodoRepository(todo_file, done_file)
    todo_list = repo.load_todo()

    # Ejecutar archivado
    archived_count = repo.archive_completed(todo_list)

    assert archived_count == 1

    # Verificar todo.txt (solo queda la pendiente)
    todo_content = todo_file.read_text(encoding="utf-8")
    assert todo_content == "Pendiente\n"

    # Verificar done.txt (se añadió la completada)
    done_content = done_file.read_text(encoding="utf-8")
    assert "x Completada" in done_content
