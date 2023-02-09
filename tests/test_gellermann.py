import gellermann

import numpy as np


def test_is_gellermann_series():
    assert gellermann.is_gellermann_series("R R R L L R L R L L".split())
    assert gellermann.is_gellermann_series("L L L R R L R L R R".split())
    assert gellermann.is_gellermann_series("R R L R L R R L L L".split())
    assert gellermann.is_gellermann_series("L L R L R L L R R R".split())
    assert gellermann.is_gellermann_series("R R L L R L R R L L".split())
    assert gellermann.is_gellermann_series("L L R R L R L L R R".split())

    assert gellermann.is_gellermann_series("LLRRLRLLRR")
    assert gellermann.is_gellermann_series("LLRRLRLLRR".replace("L", "A").replace("R", "B"))


def test_generate_gellermann_series():
    gellermann.generate_gellermann_series(10, 1, rng=np.random.default_rng(42))


def test_generate_all_gellermann_series():
    all_series = list(gellermann.generate_all_gellermann_series(10))
    assert len(all_series) == 8
    

