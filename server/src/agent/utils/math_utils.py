"""Utilidades para operaciones matemáticas seguras."""

import ast
import operator
import re
from typing import Optional

# Operadores matemáticos seguros
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_eval_math(expression: str) -> float:
    """Evalúa expresiones matemáticas de forma segura usando AST.
    
    Args:
        expression: Expresión matemática como string (ej: "2 + 3 * 4")
        
    Returns:
        Resultado de la evaluación
        
    Raises:
        ValueError: Si la expresión contiene operaciones no soportadas
    """
    try:
        node = ast.parse(expression, mode='eval').body
        return _eval_node(node)
    except Exception as e:
        raise ValueError(f"Error evaluando expresión: {e}")


def _eval_node(node):
    """Evalúa recursivamente nodos del AST.
    
    Args:
        node: Nodo del AST a evaluar
        
    Returns:
        Resultado de la evaluación del nodo
        
    Raises:
        ValueError: Si el nodo contiene operaciones no soportadas
    """
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return SAFE_OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        return SAFE_OPERATORS[type(node.op)](operand)
    else:
        raise ValueError(f"Operación no soportada: {type(node).__name__}")


def extract_math_expression(text: str) -> Optional[str]:
    """Extrae una expresión matemática de un texto.
    
    Args:
        text: Texto que contiene la expresión matemática
        
    Returns:
        Expresión matemática extraída o None si no se encuentra
    """
    # Buscar números y operadores matemáticos
    math_expr = re.findall(r'[\d+\-*/().\s]+', text)
    
    if math_expr:
        expression = ''.join(math_expr).strip()
        # Validar que la expresión no esté vacía
        if expression and any(c.isdigit() for c in expression):
            return expression
    
    return None
