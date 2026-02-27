from __future__ import annotations

from datetime import date

from todo_txt.model.task import TodoTask


def test_standard_task() -> None:
    line = (
        "(D) 2025-04-07 ",
        "Definir calendario de ejecuciones general para el área ",
        "+uniandes @proyectos_de_análisis",
    )

    task = TodoTask.parse("".join(line))
    except_task = TodoTask(
        is_completed=False,
        priority="D",
        completion_date=None,
        creation_date=date(year=2025, month=4, day=7),
        description="Definir calendario de ejecuciones general para el área",
        projects=["uniandes"],
        contexts=["proyectos_de_análisis"],
        special_tags={},
    )

    assert task == except_task


def test_minimum_task_only_description() -> None:
    line = "Comprar leche"

    task = TodoTask.parse(line)
    expected_task = TodoTask(description="Comprar leche")

    assert task == expected_task


def test_task_complete_with_all_metadata() -> None:
    line = [
        "x (A) 2026-02-27 2026-02-20 ",
        "Terminar el parser ",
        "+python +dev @home ",
        "due:2026-03-01 ",
        "status:wip ",
        "note:../todo/notes/dashboard_asientos_contables_2026-01-22.md ",
        'msg:"Esto es un mensaje de prueba"',
    ]
    task = TodoTask.parse("".join(line))

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
            "note": "../todo/notes/dashboard_asientos_contables_2026-01-22.md",
            "msg": "Esto es un mensaje de prueba",
        },
    )
    assert task == expected_task


def test_tags_interspersed_in_the_description() -> None:
    # Las etiquetas no siempre están al final, el parser debe poder
    # sacarlas del medio del texto
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
    # Si no, son simplemente parte de la descripción.
    line = "x(A) 2026-02-27 Esto no tiene formato real"

    task = TodoTask.parse(line)
    expected_task = TodoTask(description="x(A) 2026-02-27 Esto no tiene formato real")

    assert task == expected_task


def test_priority_without_dates() -> None:
    line = "(B) Revisar correos"
    task = TodoTask.parse(line)

    expected_task = TodoTask(priority="B", description="Revisar correos")
    assert task == expected_task
