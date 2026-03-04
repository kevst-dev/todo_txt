"""Módulo para el parseo de expresiones de filtrado avanzadas mediante Lark."""

from __future__ import annotations

from typing import Any

from lark import Lark, Transformer

from todo_txt.model.filters import (
    AndFilter,
    CompletedFilter,
    ContextFilter,
    NotFilter,
    OrFilter,
    PriorityFilter,
    ProjectFilter,
    TagFilter,
    TaskFilter,
)

# Gramática de Lark para el DSL de filtros
GRAMMAR = r"""
?start: expr

?expr: or_test
?or_test: and_test (_OR and_test)*
?and_test: not_test (_AND not_test)*
?not_test: _NOT not_test -> is_not
         | comparison
         | "(" expr ")"

comparison: (ATTR | TAG_ATTR) OP VALUE

# Palabras clave y símbolos
_OR: "OR" | "or" | "||"
_AND: "AND" | "and" | "&&"
_NOT: "NOT" | "not" | "!"

ATTR: "project" | "priority" | "context" | "done"
TAG_ATTR: "tag." /[a-zA-Z_]\w*/
OP: "==" | "!=" | ">=" | "<=" | ">" | "<"
VALUE: /'[^']*'/ | /"[^"]*"/ | /\w+/

%import common.WS
%ignore WS
"""


class FilterTransformer(Transformer):  # type: ignore[misc]
    """Convierte el árbol de sintaxis de Lark en objetos TaskFilter."""

    def comparison(self, args: list[Any]) -> TaskFilter:
        """Traduce una comparación simple (attr op value) a un filtro."""
        attr, op, val = args
        attr_name = str(attr)
        operator = str(op)
        value = str(val).strip("'\"")

        if attr_name.startswith("tag."):
            tag_key = attr_name[4:]
            return TagFilter(tag_key, value, operator=operator)

        if attr_name == "project":
            return ProjectFilter(value, operator=operator)
        if attr_name == "priority":
            return PriorityFilter(value, operator=operator)
        if attr_name == "context":
            return ContextFilter(value, operator=operator)
        if attr_name == "done":
            bool_val = value.lower() == "true"
            return CompletedFilter(bool_val, operator=operator)

        msg = f"Atributo no soportado: {attr_name}"
        raise ValueError(msg)

    def is_not(self, args: list[Any]) -> TaskFilter:
        """Traduce el operador NOT."""
        return NotFilter(args[0])

    def and_test(self, args: list[Any]) -> TaskFilter:
        """Traduce el operador AND (soporta múltiples filtros encadenados)."""
        return AndFilter(*args) if len(args) > 1 else args[0]

    def or_test(self, args: list[Any]) -> TaskFilter:
        """Traduce el operador OR (soporta múltiples filtros encadenados)."""
        return OrFilter(*args) if len(args) > 1 else args[0]


# Inicialización del parser
parser = Lark(GRAMMAR, parser="lalr", transformer=FilterTransformer())


def parse_filter(expression: str) -> TaskFilter:
    """
    Convierte una cadena de texto en un filtro de tareas ejecutable.

    Args:
        expression: La cadena con el filtro (ej: "project == 'uniandes'").

    Returns:
        Un objeto TaskFilter listo para ser usado con TodoList.find().

    """
    return parser.parse(expression)  # type: ignore[no-any-return]
