"""Módulo para la persistencia de tareas en archivos todo.txt y done.txt."""

from __future__ import annotations

from pathlib import Path

from todo_txt.model.todo_list import TodoList


class TodoRepository:
    """Gestiona la lectura y escritura de tareas en el sistema de archivos."""

    def __init__(self, todo_path: Path, done_path: Path) -> None:
        """Inicializa el repositorio con las rutas de los archivos."""
        self.todo_path = todo_path
        self.done_path = done_path

    def load_todo(self) -> TodoList:
        """Carga las tareas únicamente del archivo todo.txt."""
        lines: list[str] = []
        if self.todo_path.exists():
            with self.todo_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
        return TodoList.from_lines(lines)

    def save_todo(self, todo_list: TodoList) -> None:
        """Guarda el estado actual de la lista en todo.txt (preservando orden e IDs)."""
        if not self.todo_path.parent.exists():
            self.todo_path.parent.mkdir(parents=True, exist_ok=True)

        with self.todo_path.open("w", encoding="utf-8") as f:
            # Usamos el acceso interno para no saltar los huecos (None)
            # y mantener la estructura exacta del archivo.
            for task_or_none in todo_list._tasks:
                if task_or_none is None:
                    f.write("\n")
                else:
                    f.write(f"{task_or_none}\n")

    def archive_completed(self, todo_list: TodoList) -> int:
        """
        Mueve las tareas completadas de todo_list al archivo done.txt.

        Devuelve el número de tareas archivadas.
        """
        completed_tasks = todo_list.filter(is_completed=True)
        if not completed_tasks:
            return 0

        # 1. Añadir al final de done.txt (append mode)
        if not self.done_path.parent.exists():
            self.done_path.parent.mkdir(parents=True, exist_ok=True)

        with self.done_path.open("a", encoding="utf-8") as f:
            for entry in completed_tasks:
                f.write(f"{entry.task}\n")

        # 2. Eliminar de todo_list (físicamente, de abajo a arriba)
        for entry in sorted(completed_tasks, key=lambda e: e.id, reverse=True):
            todo_list.remove_task(entry.id)

        # 3. Persistir el cambio en todo.txt
        self.save_todo(todo_list)

        return len(completed_tasks)
