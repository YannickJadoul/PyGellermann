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


import pytest

import pygellermann

import numpy as np


def test_is_gellermann_series():
    assert pygellermann.is_gellermann_series("R R R L L R L R L L".split())
    assert pygellermann.is_gellermann_series("L L L R R L R L R R".split())
    assert pygellermann.is_gellermann_series("R R L R L R R L L L".split())
    assert pygellermann.is_gellermann_series("L L R L R L L R R R".split())
    assert pygellermann.is_gellermann_series("R R L L R L R R L L".split())
    assert pygellermann.is_gellermann_series("L L R R L R L L R R".split())

    assert pygellermann.is_gellermann_series("LLRRLRLLRR")
    assert pygellermann.is_gellermann_series("LLRRLRLLRR".replace("L", "A").replace("R", "B"))


@pytest.mark.parametrize('m', [1, 5, 20])
@pytest.mark.parametrize('n', [10, 20, 40])
def test_generate_gellermann_series(n, m):
    all_series = list(pygellermann.generate_gellermann_series(n, m))
    assert len(all_series) == m
    assert all(len(s) == n for s in all_series)
    assert all(pygellermann.is_gellermann_series(s) for s in all_series)
    assert set.union(*map(set, all_series)) == {'A', 'B'}


def test_generate_gellermann_series_rng():
    series = list(pygellermann.generate_gellermann_series(10, 5, rng=np.random.default_rng(42)))
    assert series == [
        ['A', 'A', 'A', 'B', 'B', 'A', 'B', 'A', 'B', 'B'],
        ['B', 'B', 'A', 'A', 'B', 'A', 'B', 'B', 'A', 'A'],
        ['A', 'A', 'A', 'B', 'B', 'A', 'B', 'A', 'B', 'B'],
        ['B', 'B', 'A', 'A', 'B', 'A', 'B', 'B', 'A', 'A'],
        ['B', 'B', 'A', 'A', 'B', 'A', 'B', 'B', 'A', 'A']
    ]


def test_generate_gellermann_series_max_iterations():
    series = list(pygellermann.generate_gellermann_series(8, 5, max_iterations=1000))
    assert len(series) == 0


@pytest.mark.parametrize('n, m_expected', [(10, 8), (16, 80), (20, 4726)])
def test_generate_all_gellermann_series(n, m_expected):
    all_series = list(pygellermann.generate_all_gellermann_series(n))
    assert len(all_series) == m_expected
    assert all(len(s) == n for s in all_series)
    assert set.union(*map(set, all_series)) == {'A', 'B'}

    for s in pygellermann.generate_gellermann_series(n, 100):
        assert pygellermann.is_gellermann_series(s) == (s in all_series)


@pytest.mark.parametrize('tolerance, m_expected', [(0.1, 8), (0.2, 32), (0.3, 72), (0.4, 84), (0.5, 86)])
def test_generate_all_gellermann_series_tolerance(tolerance, m_expected):
    all_series = list(pygellermann.generate_all_gellermann_series(10, alternation_tolerance=tolerance))
    assert len(all_series) == m_expected
    assert all(len(s) == 10 for s in all_series)
    assert set.union(*map(set, all_series)) == {'A', 'B'}


@pytest.mark.parametrize('choices', [('L', 'R'), ('R', 'L'), (1, 2), ('ABC', (42,))])
@pytest.mark.parametrize('n', [10, 20, 40])
def test_generate_gellermann_series_choices(n, choices):
    series = next(pygellermann.generate_gellermann_series(n, 1, choices=choices))
    assert pygellermann.is_gellermann_series(series)
    assert len(series) == n
    assert set(series) == set(choices)


@pytest.mark.parametrize('m', [1, 5, 20])
@pytest.mark.parametrize('n', [10, 20, 40])
def test_generate_gellermann_series_table_wide(n, m):
    df = pygellermann.generate_gellermann_series_table(n, m, long_format=False)

    assert len(df) == m
    assert len(df.columns) == n
    assert list(df.columns) == [f'element_{i}' for i in range(n)]
    assert df.index.nlevels == 1
    assert df.index.names == ['series_i']
    assert all(pygellermann.is_gellermann_series(r) for _, r in df.iterrows())


@pytest.mark.parametrize('m', [1, 5, 20])
@pytest.mark.parametrize('n', [10, 20, 40])
def test_generate_gellermann_series_table_long(n, m):
    df = pygellermann.generate_gellermann_series_table(n, m, long_format=True)

    assert len(df) == m * n
    assert len(df.columns) == 1
    assert list(df.columns) == ['element']
    assert df.index.nlevels == 2
    assert df.index.names == ['series_i', 'element_i']
    assert all(pygellermann.is_gellermann_series(g['element']) for _, g in df.groupby('series_i'))
