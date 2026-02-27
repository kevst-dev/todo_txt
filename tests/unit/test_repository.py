"""Tests para el repositorio de archivos todo.txt y done.txt."""

from __future__ import annotations

from pathlib import Path

from todo_txt.model.task import TodoTask
from todo_txt.model.todo_list import TodoList
from todo_txt.repository import TodoRepository


def test_repository_load_missing_files(tmp_path: Path) -> None:
    """Verifica que si los archivos no existen, se devuelve una lista vacía."""
    repo = TodoRepository(tmp_path / "todo.txt", tmp_path / "done.txt")
    todo_list = repo.load()

    assert len(todo_list) == 0


def test_repository_load_from_both_files(tmp_path: Path) -> None:
    """Verifica la carga combinada de todo.txt y done.txt."""
    todo_file = tmp_path / "todo.txt"
    done_file = tmp_path / "done.txt"

    todo_file.write_text("Tarea pendiente 1\nTarea pendiente 2\n", encoding="utf-8")
    done_file.write_text("x 2026-02-27 Tarea completada\n", encoding="utf-8")

    repo = TodoRepository(todo_file, done_file)
    todo_list = repo.load()

    assert len(todo_list) == 3
    # Verificamos que se cargaron ambos estados
    pendings = [t for t in todo_list if not t.is_completed]
    completed = [t for t in todo_list if t.is_completed]

    assert len(pendings) == 2
    assert len(completed) == 1


def test_repository_save_distributes_tasks(tmp_path: Path) -> None:
    """Verifica que las tareas se repartan correctamente entre archivos al guardar."""
    todo_file = tmp_path / "todo.txt"
    done_file = tmp_path / "done.txt"
    repo = TodoRepository(todo_file, done_file)

    # Creamos una lista con tareas mixtas
    tasks = [
        TodoTask.parse("Pendiente A"),
        TodoTask.parse("x 2026-02-27 Completada B"),
        TodoTask.parse("Pendiente C"),
    ]
    todo_list = TodoList(tasks)

    # Guardamos
    repo.save(todo_list)

    # Verificamos el contenido de los archivos
    todo_content = todo_file.read_text(encoding="utf-8")
    done_content = done_file.read_text(encoding="utf-8")

    assert "Pendiente A" in todo_content
    assert "Pendiente C" in todo_content
    assert "Completada B" in done_content
    # Verificamos que no se cruzaron
    assert "Completada B" not in todo_content
    assert "Pendiente A" not in done_content


def test_repository_save_overwrites_content(tmp_path: Path) -> None:
    """Verifica que el guardado sobrescribe el contenido previo."""
    todo_file = tmp_path / "todo.txt"
    done_file = tmp_path / "done.txt"

    # Archivo con basura previa
    todo_file.write_text("CONTENIDO VIEJO\n", encoding="utf-8")

    repo = TodoRepository(todo_file, done_file)
    todo_list = TodoList.from_lines(["NUEVO CONTENIDO"])

    repo.save(todo_list)

    todo_content = todo_file.read_text(encoding="utf-8")
    assert "CONTENIDO VIEJO" not in todo_content
    assert "NUEVO CONTENIDO" in todo_content
