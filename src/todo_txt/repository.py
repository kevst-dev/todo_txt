"""Módulo para la persistencia de tareas en archivos todo.txt y done.txt."""

from __future__ import annotations

from pathlib import Path

from todo_txt.model.task import TodoTask
from todo_txt.model.todo_list import TodoList


class TodoRepository:
    """Gestiona la lectura y escritura de tareas en el sistema de archivos."""

    def __init__(self, todo_path: Path, done_path: Path) -> None:
        """Inicializa el repositorio con las rutas de los archivos."""
        self.todo_path = todo_path
        self.done_path = done_path

    def load(self) -> TodoList:
        """
        Carga todas las tareas de ambos archivos en una sola lista.

        Si los archivos no existen, devuelve una lista vacía.
        """
        all_lines: list[str] = []
        for path in [self.todo_path, self.done_path]:
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    all_lines.extend(f.readlines())

        return TodoList.from_lines(all_lines)

    def save(self, todo_list: TodoList) -> None:
        """
        Separa las tareas y las guarda en sus archivos correspondientes.

        Sobrescribe los archivos existentes para reflejar el estado actual
        de la lista de tareas.
        """
        pending_tasks: list[TodoTask] = []
        completed_tasks: list[TodoTask] = []

        for task in todo_list:
            if task.is_completed:
                completed_tasks.append(task)
            else:
                pending_tasks.append(task)

        self._write_to_file(self.todo_path, pending_tasks)
        self._write_to_file(self.done_path, completed_tasks)

    def _write_to_file(self, path: Path, tasks: list[TodoTask]) -> None:
        """Escribe una lista de tareas en un archivo (sobrescribe)."""
        # Aseguramos que el directorio exista
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            for task in tasks:
                f.write(f"{task}\n")
