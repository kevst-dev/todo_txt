"""Tests de integración para el comando 'list' de la CLI."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from todo_txt.cli.main import main


def extract_ids_from_output(output: str) -> list[str]:
    """Extrae únicamente los identificadores numéricos de las tareas.

    Busca el patrón del ID en la primera columna de la tabla de rich.
    Mantiene la unicidad para evitar duplicados por el wrap de líneas.

    Returns:
        list[str]: Una lista que contiene solo los IDs (números) de las tareas
                  encontradas, preservando el orden de aparición.
    """
    # Buscamos el patrón SOLO al inicio de cada línea física
    raw_ids = re.findall(r"^\s*│\s+(\d+)\s+│", output, re.MULTILINE)
    return list(dict.fromkeys(raw_ids))


def test_handle_list_count(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifica que el comando list muestra la cantidad correcta de tareas."""
    # 1. Rutas de datos de prueba
    todo_path = Path("tests/integration/data/todo.txt")
    done_path = Path("tests/integration/data/done.txt")

    # 2. Argumentos para listar pendientes (por defecto)
    args = [
        "--todo-file",
        str(todo_path),
        "--done-file",
        str(done_path),
        "list",
    ]

    # 3. Ejecutamos main
    main(args)

    # 4. Capturamos salida
    captured = capsys.readouterr()
    found_ids = extract_ids_from_output(captured.out)

    print(found_ids)

    # En el archivo de prueba hay 37 tareas pendientes
    assert len(found_ids) == 37
    assert "1" in found_ids
    assert "37" in found_ids


def test_handle_list_complex_filter(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifica el comando list con un filtro denso y complejo."""
    todo_path = Path("tests/integration/data/todo.txt")
    done_path = Path("tests/integration/data/done.txt")

    # Filtro denso: uniandes con prioridad >= D OR personal con vencimiento
    query = (
        "( (project == 'uniandes' AND priority >= 'D') OR "
        "(project == 'personal' AND tag.due != '') ) "
        "AND NOT done == True"
    )

    args = [
        "--todo-file",
        str(todo_path),
        "--done-file",
        str(done_path),
        "list",
        "--filter",
        query,
    ]

    main(args)

    captured = capsys.readouterr()
    found_ids = extract_ids_from_output(captured.out)

    # Basado en tus datos de prueba:
    # - Uniandes con prioridad A-D: IDs 1, 2, 3, 4, 6 (D) y 17 (D) -> 6 tareas
    # - Personal con due: IDs 20, 22, 24, 25, 27, 29, 31, 32 -> 8 tareas
    # Total esperado: 14 tareas
    assert len(found_ids) == 14
    assert "1" in found_ids  # uniandes D
    assert "20" in found_ids  # personal con due
    assert "5" not in found_ids  # uniandes E (fuera de rango >= D)
    assert "11" not in found_ids  # uniandes sin prioridad
