"""Modelo de datos para las tareas de todo.txt."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class TodoTask:
    """Representa una tarea individual siguiendo el formato estándar de todo.txt."""

    # El texto de la tarea, excluyendo las marcas de completado, prioridad y etiquetas.
    description: str

    # Indica si la tarea está completada.
    is_completed: bool = False

    # Letra mayúscula (A-Z) que indica la prioridad.
    priority: str | None = None

    # Fecha de finalización (YYYY-MM-DD).
    completion_date: date | None = None

    # Fecha de creación (YYYY-MM-DD).
    creation_date: date | None = None

    # Lista de proyectos asociados (palabras con '+').
    projects: list[str] = field(default_factory=list)

    # Lista de contextos asociados (palabras con '@').
    contexts: list[str] = field(default_factory=list)

    # Pares clave:valor para metadata adicional.
    special_tags: dict[str, str] = field(default_factory=dict)

    @classmethod
    def parse(cls, line: str) -> TodoTask:
        """Toma una línea de texto en formato todo.txt y devuelve un TodoTask."""
        line = line.strip()
        if not line:
            msg = "La línea de tarea no puede estar vacía."
            raise ValueError(msg)

        # 1. Metadatos de prefijo (Completado, Prioridad, Fechas)
        is_completed, line = cls._extract_completion(line)
        priority, line = cls._extract_priority(line)
        comp_date, creat_date, line = cls._extract_dates(line)

        # 2. Cuerpo de la tarea (Descripción y etiquetas)
        desc, projects, contexts, tags = cls._extract_body(line)

        return cls(
            description=desc,
            is_completed=is_completed,
            priority=priority,
            completion_date=comp_date,
            creation_date=creat_date,
            projects=projects,
            contexts=contexts,
            special_tags=tags,
        )

    @staticmethod
    def _extract_completion(line: str) -> tuple[bool, str]:
        """Extrae la marca de completado 'x '."""
        if line.startswith("x "):
            return True, line[2:].lstrip()
        return False, line

    @staticmethod
    def _extract_priority(line: str) -> tuple[str | None, str]:
        """Extrae la prioridad '(A) '."""
        match = re.match(r"^\(([A-Z])\)\s+", line)
        if match:
            return match.group(1), line[match.end() :].lstrip()
        return None, line

    @staticmethod
    def _extract_dates(line: str) -> tuple[date | None, date | None, str]:
        """Extrae hasta dos fechas al inicio de la línea."""
        dates = []
        while True:
            # Buscamos fecha YYYY-MM-DD seguida de espacio o fin de línea
            match = re.match(r"^(\d{4}-\d{2}-\d{2})(?:\s+|$)", line)
            if match:
                dates.append(date.fromisoformat(match.group(1)))
                line = line[match.end() :].lstrip()
            else:
                break

        if len(dates) == 2:
            return dates[0], dates[1], line
        if len(dates) == 1:
            return None, dates[0], line
        return None, None, line

    @staticmethod
    def _extract_body(line: str) -> tuple[str, list[str], list[str], dict[str, str]]:
        """Extrae descripción y etiquetas del resto de la línea de forma robusta."""
        projects = []
        contexts = []
        tags = {}

        # 1. Extraer Tags key:value (soporta comillas para valores con espacios)
        # Patrón: busca llave:valor, donde el valor puede ser un "texto con espacios"
        # o texto_simple.
        tag_pattern = re.compile(r"(?:\s|^)([\w.-]+):(?:\"([^\"]*)\"|(\S+))")

        def _extract_tag(match: re.Match[str]) -> str:
            key = match.group(1)
            # El grupo 2 es el valor con comillas, el grupo 3 es sin comillas
            value = match.group(2) if match.group(2) is not None else match.group(3)
            tags[key] = value
            return " "

        line = tag_pattern.sub(_extract_tag, line)

        # 2. Extraer Proyectos (+proyecto)
        project_pattern = re.compile(r"(?:\s|^)\+(\S+)")

        def _extract_project(match: re.Match[str]) -> str:
            projects.append(match.group(1))
            return " "

        line = project_pattern.sub(_extract_project, line)

        # 3. Extraer Contextos (@contexto)
        context_pattern = re.compile(r"(?:\s|^)@(\S+)")

        def _extract_context(match: re.Match[str]) -> str:
            contexts.append(match.group(1))
            return " "

        line = context_pattern.sub(_extract_context, line)

        # 4. Lo que queda es la descripción
        description = " ".join(line.split())

        return description, projects, contexts, tags

    def __str__(self) -> str:
        """Devuelve la representación en formato todo.txt."""
        parts = []
        if self.is_completed:
            parts.append("x")
        if self.priority:
            parts.append(f"({self.priority})")
        if self.completion_date:
            parts.append(self.completion_date.isoformat())
        if self.creation_date:
            parts.append(self.creation_date.isoformat())

        parts.append(self.description)

        # Proyectos y contextos
        parts.extend([f"+{p}" for p in self.projects])
        parts.extend([f"@{c}" for c in self.contexts])

        # Tags especiales (añade comillas si el valor tiene espacios)
        for k, v in self.special_tags.items():
            if " " in v:
                parts.append(f'{k}:"{v}"')
            else:
                parts.append(f"{k}:{v}")

        return " ".join(parts)
