"""Main PyGellermann module, containing all public functions."""

from ._version import __version__
from .gellermann import (
    DEFAULT_ALTERNATION_TOLERANCE,
    generate_all_gellermann_series,
    generate_gellermann_series,
    generate_gellermann_series_table,
    is_gellermann_series
)

__all__ = [
    '__version__',
    'DEFAULT_ALTERNATION_TOLERANCE',
    'generate_all_gellermann_series',
    'generate_gellermann_series',
    'generate_gellermann_series_table',
    'is_gellermann_series'
]
