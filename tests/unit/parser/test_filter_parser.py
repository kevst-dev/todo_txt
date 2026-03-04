"""Tests para el motor de parseo de filtros avanzados."""

from __future__ import annotations

from todo_txt.model.filters import (
    AndFilter,
    CompletedFilter,
    ContextFilter,
    NotFilter,
    OrFilter,
    PriorityFilter,
    ProjectFilter,
)
from todo_txt.parser.filter_parser import parse_filter


def test_parse_simple_project_filter() -> None:
    """Verifica el parseo de un filtro de proyecto simple."""
    f = parse_filter("project == 'uniandes'")
    assert isinstance(f, ProjectFilter)
    assert f.project == "uniandes"


def test_parse_simple_priority_filter() -> None:
    """Verifica el parseo de un filtro de prioridad simple."""
    f = parse_filter("priority == 'A'")
    assert isinstance(f, PriorityFilter)
    assert f.priority == "A"


def test_parse_simple_context_filter() -> None:
    """Verifica el parseo de un filtro de contexto simple."""
    f = parse_filter("context == 'home'")
    assert isinstance(f, ContextFilter)
    assert f.context == "home"


def test_parse_simple_done_filter() -> None:
    """Verifica el parseo de un filtro de completitud simple."""
    f = parse_filter("done == True")
    assert isinstance(f, CompletedFilter)
    assert f.is_completed is True


def test_parse_and_combination() -> None:
    """Verifica que AND se parsea como un AndFilter con dos hijos."""
    f = parse_filter("project == 'A' AND priority == 'B'")
    assert isinstance(f, AndFilter)
    assert len(f.filters) == 2
    assert isinstance(f.filters[0], ProjectFilter)
    assert isinstance(f.filters[1], PriorityFilter)


def test_parse_or_combination() -> None:
    """Verifica que OR se parsea como un OrFilter con dos hijos."""
    f = parse_filter("project == 'A' OR project == 'B'")
    assert isinstance(f, OrFilter)
    assert len(f.filters) == 2


def test_parse_not_combination() -> None:
    """Verifica que NOT se parsea como un NotFilter envolviendo a otro."""
    f = parse_filter("NOT done == True")
    assert isinstance(f, NotFilter)
    assert isinstance(f.filter, CompletedFilter)


def test_parse_precedence_and_parentheses() -> None:
    """Verifica que los paréntesis alteran la estructura del árbol como se espera."""
    # Query: (A OR B) AND C
    # El AND debe ser la raíz, con un OR como primer hijo.
    query = "(project == 'A' OR project == 'B') AND priority == 'C'"
    f = parse_filter(query)

    assert isinstance(f, AndFilter)
    assert isinstance(f.filters[0], OrFilter)
    assert isinstance(f.filters[1], PriorityFilter)

    # Query: A OR (B AND C)
    # El OR debe ser la raíz, con un AND como segundo hijo.
    query_alt = "project == 'A' OR (project == 'B' AND priority == 'C')"
    f_alt = parse_filter(query_alt)

    assert isinstance(f_alt, OrFilter)
    assert isinstance(f_alt.filters[0], ProjectFilter)
    assert isinstance(f_alt.filters[1], AndFilter)
