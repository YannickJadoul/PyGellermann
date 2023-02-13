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


import numpy as np
import pandas as pd

import itertools


# TODO: uneven length sequences
# TODO: optimize multiple calculations
# TODO: C backend?

DEFAULT_ALTERNATION_TOLERANCE = 0.1


def balanced_elements(s):
    n = len(s)
    return n % 2 == 0 and np.sum(s) == n // 2


def more_than_three_successive(s):
    successive = s[:-1] == s[1:]
    return np.any(successive[:-2] & successive[1:-1] & successive[2:])


def at_least_twenty_percent_per_half(s):
    n = len(s)
    p = n // 5
    return np.sum(s[:n//2]) >= p and np.sum(~s[:n//2]) >= p and np.sum(s[n//2:]) >= p and np.sum(~s[n//2:]) >= p


def less_than_half_reversals(s):
    return np.sum(s[:-1] != s[1:]) <= len(s) // 2


def close_to_fifty_percent_alternation(s, tolerance):
    assert 0 <= tolerance <= 0.5

    n = len(s)

    def close_to_fifty_percent_for(alternation):
        return 0.5 - tolerance <= np.sum(alternation == s) / n <= 0.5 + tolerance

    return (close_to_fifty_percent_for(np.tile([True, False], (n + 1) // 2)[:n]) and
            close_to_fifty_percent_for(np.tile([True, True, False, False], (n + 3) // 4)[:n]) and
            close_to_fifty_percent_for(np.tile([True, False, False, True], (n + 3) // 4)[:n]))


def is_boolean_gellermann_series(s, alternation_tolerance=0.1):
    return (balanced_elements(s) and
            not more_than_three_successive(s) and
            at_least_twenty_percent_per_half(s) and
            less_than_half_reversals(s) and
            close_to_fifty_percent_alternation(s, alternation_tolerance))


def is_gellermann_series(s, alternation_tolerance=0.1):
    assert len(set(s)) % 2 == 0
    first = s[0]
    return is_boolean_gellermann_series(np.array([x == s[0] for x in s]), alternation_tolerance=alternation_tolerance)


def generate_boolean_gellermann_series(n, m, rng=None, **kwargs):
    assert n % 2 == 0
    if rng is None:
        rng = np.random.default_rng()
    s = np.repeat([True, False], n // 2)
    while m > 0:
        rng.shuffle(s)
        if is_boolean_gellermann_series(s, **kwargs):
            yield s.copy()
            m -= 1


def generate_gellermann_series(n, m, symbols=('A', 'B'), rng=None, **kwargs):
    for s in generate_boolean_gellermann_series(n, m, rng=rng, **kwargs):
        yield [symbols[x] for x in s]


def generate_all_boolean_gellermann_series(n, **kwargs):
    assert n % 2 == 0
    for s in itertools.product([False, True], repeat=n):
        if is_boolean_gellermann_series(np.array(s), **kwargs):
            yield s


def generate_all_gellermann_series(n, symbols=('A', 'B'), **kwargs):
    for s in generate_all_boolean_gellermann_series(n, **kwargs):
        yield [symbols[x] for x in s]


def _series_to_wide_format_df(series_list):
    series_dicts = [{'series_idx': i, **{f'element_{j}': x for j, x in enumerate(s)}} for i, s in enumerate(series_list)]
    return pd.DataFrame(series_dicts).set_index('series_idx')


def _series_to_long_format_df(series_list):
    series_dicts = [{'series_idx': i, 'element_idx': j, 'element': e} for i, s in enumerate(series_list) for j, e in enumerate(s)]
    return pd.DataFrame(series_dicts).set_index(['series_idx', 'element_idx'])


def generate_gellermann_series_table(n, m, symbols=('A', 'B'), long_format=False, **kwargs):
    generated_series = list(generate_gellermann_series(n, m, symbols=symbols, **kwargs))
    if long_format:
        return _series_to_long_format_df(generated_series)
    else:
        return _series_to_wide_format_df(generated_series)
