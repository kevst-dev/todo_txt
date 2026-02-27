"""Tests para el modelo TodoTask."""

from __future__ import annotations

from datetime import date

from todo_txt.model.task import TodoTask


def test_standard_task() -> None:
    line = (
        "(D) 2025-04-07 "
        "Definir calendario de ejecuciones general para el área "
        "+uniandes @proyectos_de_análisis"
    )

    task = TodoTask.parse(line)
    expected_task = TodoTask(
        is_completed=False,
        priority="D",
        completion_date=None,
        creation_date=date(year=2025, month=4, day=7),
        description="Definir calendario de ejecuciones general para el área",
        projects=["uniandes"],
        contexts=["proyectos_de_análisis"],
        special_tags={},
    )

    assert task == expected_task


def test_minimum_task_only_description() -> None:
    line = "Comprar leche"

    task = TodoTask.parse(line)
    expected_task = TodoTask(description="Comprar leche")

    assert task == expected_task


def test_task_complete_with_all_metadata() -> None:
    # Probamos una tarea compleja con todos los campos y valores con espacios
    line = (
        "x (A) 2026-02-27 2026-02-20 "
        "Terminar el parser "
        "+python +dev @home "
        'due:2026-03-01 status:wip msg:"Esto es un mensaje"'
    )
    task = TodoTask.parse(line)

    expected_task = TodoTask(
        is_completed=True,
        priority="A",
        completion_date=date(2026, 2, 27),
        creation_date=date(2026, 2, 20),
        description="Terminar el parser",
        projects=["python", "dev"],
        contexts=["home"],
        special_tags={
            "due": "2026-03-01",
            "status": "wip",
            "msg": "Esto es un mensaje",
        },
    )
    assert task == expected_task


def test_tags_interspersed_in_the_description() -> None:
    # Las etiquetas pueden estar en cualquier lugar. El parser las extrae
    # y limpia la descripción de espacios extra.
    line = "Llamar a @juan sobre el +proyecto_secreto mañana due:hoy temprano"

    task = TodoTask.parse(line)
    expected_task = TodoTask(
        description="Llamar a sobre el mañana temprano",
        projects=["proyecto_secreto"],
        contexts=["juan"],
        special_tags={"due": "hoy"},
    )

    assert task == expected_task


def test_false_positives_due_to_lack_of_spaces() -> None:
    # Según todo.txt, la 'x' y la prioridad '(A)' DEBEN ir seguidas de un espacio.
    line = "x(A) 2026-02-27 Esto no tiene formato real"

    task = TodoTask.parse(line)
    # Aquí 'x(A)' es parte de la descripción porque no hay espacio tras la x
    # '2026-02-27' no se reconoce como fecha al inicio porque está precedida por x(A)
    expected_task = TodoTask(
        description="x(A) 2026-02-27 Esto no tiene formato real",
    )

    assert task == expected_task


def test_priority_without_dates() -> None:
    line = "(B) Revisar correos"
    task = TodoTask.parse(line)

    expected_task = TodoTask(priority="B", description="Revisar correos")
    assert task == expected_task


def test_serialization_to_string() -> None:
    """Verifica que el objeto se convierta correctamente a string (formato todo.txt)."""
    task = TodoTask(
        description="Comprar pan",
        is_completed=True,
        priority="A",
        completion_date=date(2026, 2, 27),
        creation_date=date(2026, 2, 20),
        projects=["hogar"],
        contexts=["supermercado"],
        special_tags={"due": "hoy", "msg": "urgente"},
    )

    expected_line = "x (A) 2026-02-27 2026-02-20 Comprar pan +hogar @supermercado due:hoy msg:urgente"
    assert str(task) == expected_line


def test_serialization_with_quoted_tags() -> None:
    """Verifica que los valores con espacios se entrecomillen al serializar."""
    task = TodoTask(
        description="Tarea con espacios",
        special_tags={"nota": "esto tiene espacios"},
    )
    assert str(task) == 'Tarea con espacios nota:"esto tiene espacios"'


def test_parse_serialization_roundtrip() -> None:
    """Verifica que parsear un string y volverlo a convertir resulte en lo mismo."""
    line = 'x (A) 2026-02-27 2026-02-20 Tarea de prueba +proyecto @contexto tag:valor msg:"con espacios"'
    task = TodoTask.parse(line)
    # El roundtrip asegura que no perdemos información
    assert str(task) == line
