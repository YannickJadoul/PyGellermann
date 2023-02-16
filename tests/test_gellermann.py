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


def test_generate_gellermann_series():
    pygellermann.generate_gellermann_series(10, 1, rng=np.random.default_rng(42))


def test_generate_all_gellermann_series():
    all_series = list(pygellermann.generate_all_gellermann_series(10))
    assert len(all_series) == 8
    

