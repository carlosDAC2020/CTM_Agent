"""Routers de la API"""

from .assistants import router as assistants_router
from .threads import router as threads_router
from .runs import router as runs_router
from .system import router as system_router

__all__ = [
    "assistants_router",
    "threads_router",
    "runs_router",
    "system_router",
]
