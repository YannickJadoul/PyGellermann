# Copyright (C) 2022-2023  Yannick Jadoul
#
# This file is part of PyGellermann.
#
# PyGellermann is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyGellermann is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyGellermann.  If not, see <https://www.gnu.org/licenses/>.

"""Functionality for checking and generating Gellermann series."""

import numpy as np
import pandas as pd

import itertools
import sys

import numpy.typing as npt
from typing import Any, Iterator, List, Optional, Sequence, Tuple

# TODO: uneven length sequences
# TODO: optimize multiple calculations
# TODO: C backend?

DEFAULT_ALTERNATION_TOLERANCE = 0.1


if sys.version_info >= (3, 9):
    BoolSequence = np.ndarray[int, np.dtype[np.bool_]]
else:
    BoolSequence = npt.NDArray[np.bool_]


def balanced_elements(s: BoolSequence) -> bool:
    """Check if a boolean sequence has equal number of True and False elements."""
    n = len(s)
    return n % 2 == 0 and np.sum(s) == n // 2


def more_than_three_successive(s: BoolSequence) -> bool:
    """Check if a boolean sequence has more than three True or False elements in a row."""
    successive = s[:-1] == s[1:]
    return bool(np.any(successive[:-2] & successive[1:-1] & successive[2:]))


def at_least_twenty_percent_per_half(s: BoolSequence) -> bool:
    """Check if a boolean sequence has at least 20% True or False elements in both halves."""
    n = len(s)
    p = n // 5
    return bool(np.sum(s[:n//2]) >= p and np.sum(~s[:n//2]) >= p and np.sum(s[n//2:]) >= p and np.sum(~s[n//2:]) >= p)


def less_than_half_reversals(s: BoolSequence) -> bool:
    """Check if a boolean sequence has less than half True-False or False-True reversals."""
    return int(np.sum(s[:-1] != s[1:])) <= len(s) // 2


def close_to_fifty_percent_alternation(s: BoolSequence, tolerance: float) -> bool:
    """Check if a boolean sequence matches the single or double alternation criterion.

    Checks if matches single or double alternating sequences sufficiently close to 50% chance
    level, +/- tolerance.
    """
    assert 0 <= tolerance <= 0.5

    n = len(s)

    def close_to_fifty_percent_for(alternation: BoolSequence) -> bool:
        return 0.5 - tolerance <= int(np.sum(alternation == s)) / n <= 0.5 + tolerance

    return (close_to_fifty_percent_for(np.tile([True, False], (n + 1) // 2)[:n]) and
            close_to_fifty_percent_for(np.tile([True, True, False, False], (n + 3) // 4)[:n]) and
            close_to_fifty_percent_for(np.tile([True, False, False, True], (n + 3) // 4)[:n]))


def is_boolean_gellermann_series(s: BoolSequence, alternation_tolerance: float = DEFAULT_ALTERNATION_TOLERANCE) -> bool:
    """Check if a boolean sequence is a Gellermann series."""
    assert len(s) % 2 == 0
    assert 0 <= alternation_tolerance <= 0.5

    return (balanced_elements(s) and
            not more_than_three_successive(s) and
            at_least_twenty_percent_per_half(s) and
            less_than_half_reversals(s) and
            close_to_fifty_percent_alternation(s, alternation_tolerance))


def is_gellermann_series(s: Sequence[Any], alternation_tolerance: float = DEFAULT_ALTERNATION_TOLERANCE) -> bool:
    """Check if a binary sequence is a Gellermann series.

    Parameters
    ----------
    s
        A binary series (i.e., containing two different elements) of even length.
    alternation_tolerance
        The tolerance around 50% chance level compared to single or double alternation, a value
        between 0 and 0.5 (default: 0.1).

    Returns
    -------
    bool
        True if the given sequence is a Gellermann series, False otherwise.

    Raises
    ------
    ValueError
        If the sequence length is not even, or if the sequence contains more than two different
        elements, or if the alternation tolerance is not between 0 and 0.5.

    Examples
    --------
    >>> is_gellermann_series(['B', 'B', 'A', 'B', 'A', 'B', 'B', 'A', 'A', 'A'])
    True
    >>> is_gellermann_series('1112212122122211', alternation_tolerance=0.2)
    True
    >>> is_gellermann_series('1112212122122211', alternation_tolerance=0.0)
    False
    """
    if len(s) % 2 != 0:
        raise ValueError(f"Sequence length {len(s)} is not even.")
    if len(set(s)) > 2:
        raise ValueError(f"Sequence {s} contains more than two different elements.")
    if not 0 <= alternation_tolerance <= 0.5:
        raise ValueError(f"Alternation tolerance {alternation_tolerance} is not between 0 and 0.5.")

    if len(s) == 0:
        return True

    s = list(s)
    return is_boolean_gellermann_series(np.array([x == s[0] for x in s]), alternation_tolerance=alternation_tolerance)


def generate_boolean_gellermann_series(n: int, m: int, rng: Optional[np.random.Generator] = None,
                                       max_iterations: Optional[int] = None, **kwargs: Any) -> Iterator[BoolSequence]:
    """Generate m random boolean Gellermann series of length n."""
    assert n % 2 == 0
    assert m > 0

    if rng is None:
        rng = np.random.default_rng()
    s = np.repeat([True, False], n // 2)

    for _ in itertools.islice(itertools.count(), max_iterations):
        rng.shuffle(s)
        if is_boolean_gellermann_series(s, **kwargs):
            yield s.copy()
            m -= 1

        if m == 0:
            break


def generate_gellermann_series(n: int, m: int, choices: Tuple[Any, Any] = ('A', 'B'), rng: Optional[np.random.Generator] = None,
                               max_iterations: Optional[int] = None, **kwargs: Any) -> Iterator[Sequence[Any]]:
    """Generate m random Gellermann series of length n.

    Parameters
    ----------
    n
        The length of the series.
    m
        The number of series to generate.
    choices
        The two elements of the series (default: ('A', 'B')).
    rng
        A NumPy random number generator (default: None, which uses the default NumPy random number
        generator).
    max_iterations
        The maximum number of iterations to try to generate all Gellermann series (default: None,
        which tries indefinitely).
    kwargs
        Additional keyword arguments passed to `is_gellermann_series`.

    Yields
    ------
    Iterator[Sequence[Any]]
        A generator object with m Gellermann series of length n.
    """
    for s in generate_boolean_gellermann_series(n, m, rng=rng, max_iterations=max_iterations, **kwargs):
        yield [choices[int(x)] for x in s]


def generate_all_boolean_gellermann_series(n: int, **kwargs: Any) -> Iterator[BoolSequence]:
    """Generate all boolean Gellermann series of length n."""
    assert n % 2 == 0

    for s in itertools.product([False, True], repeat=n):
        if is_boolean_gellermann_series(np.array(s), **kwargs):
            yield np.array(s)


def generate_all_gellermann_series(n: int, choices: Tuple[Any, Any] = ('A', 'B'), **kwargs: Any) -> Iterator[Sequence[Any]]:
    """Generate all Gellermann series of length n in lexicographic order.

    Parameters
    ----------
    n
        The length of the series.
    choices
        The two elements of the series (default: ('A', 'B')).
    kwargs
        Additional keyword arguments passed to `is_gellermann_series`.

    Yields
    ------
    Iterator[Sequence[Any]]
        A generator object with all Gellermann series of length n.
    """
    for s in generate_all_boolean_gellermann_series(n, **kwargs):
        yield [choices[int(x)] for x in s]


def _series_to_wide_format_df(series_list: List[Sequence[Any]]) -> pd.DataFrame:
    """Convert a list of series to a wide format DataFrame."""
    series_dicts = [{'series_i': i, **{f'element_{j}': x for j, x in enumerate(s)}} for i, s in enumerate(series_list)]
    return pd.DataFrame(series_dicts).set_index('series_i')


def _series_to_long_format_df(series_list: List[Sequence[Any]]) -> pd.DataFrame:
    """Convert a list of series to a long format DataFrame."""
    series_dicts = [{'series_i': i, 'element_i': j, 'element': e} for i, s in enumerate(series_list) for j, e in enumerate(s)]
    return pd.DataFrame(series_dicts).set_index(['series_i', 'element_i'])


def generate_gellermann_series_table(n: int, m: int, long_format: bool = False, **kwargs: Any) -> pd.DataFrame:
    """Generate a Pandas DataFrame of m random Gellermann series of length n.

    In the wide format, the DataFrame has columns  series_i', 'element_0', 'element_1', ...,
    'element_{n-1}', and each row contains a full series. In the long format, the DataFrame has
    columns 'series_i', 'element_i', 'element', and each row contains a single element of a series.

    Parameters
    ----------
    n
        The length of the series.
    m
        The number of series to generate.
    long_format
        If True, the DataFrame is in long format (default: False).
    kwargs
        Additional keyword arguments passed to `generate_gellermann_series`.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame of m random Gellermann series of length n.
    """
    assert n % 2 == 0
    assert m > 0

    generated_series = list(generate_gellermann_series(n, m, **kwargs))
    if long_format:
        return _series_to_long_format_df(generated_series)
    else:
        return _series_to_wide_format_df(generated_series)
