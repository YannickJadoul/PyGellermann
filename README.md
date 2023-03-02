[![PyPI version](https://img.shields.io/pypi/v/pygellermann.svg)](https://pypi.python.org/pypi/pygellermann)
[![PyPI Python versions](https://img.shields.io/pypi/pyversions/pygellermann.svg)](https://pypi.python.org/pypi/pygellermann)
[![GitHub Actions status](https://github.com/YannickJadoul/PyGellermann/actions/workflows/ci.yml/badge.svg)](https://github.com/YannickJadoul/PyGellermann/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/YannickJadoul/PyGellermann/main.svg)](https://results.pre-commit.ci/latest/github/YannickJadoul/PyGellermann/main)

# PyGellerman: A Python Gellermann series generator

This is a Python implementation of a random genenerator for Gellermann series, pseudorandom binary sequences for human and non-human animal behavioural experiments[^Gellermann1933]. It includes both a graphical user interface (GUI) as well as a simple Python API.

Gellermann series aim to avoid inflating a partipant's experimental performance by excluding random sequences that would match simple psychological or behavioural patterns. More specifically, a Gellermann series is a random sequence which satisfies five criteria; each series of length $n$:
- must contain an equal number (= $n/2$) of As and Bs;
- must contain at most 3 As or Bs in a row;
- must contain at least 20% (= $n/5$) As and Bs within both the first and last
half;
- must contain at most $n/2$ reversals (A-B or B-A transitions);
- must provide a correct response rate close to 50% chance when responses are provided as simple alternation (ABAB...) or double alternation (AABBAA... and ABBAAB...).

## Installation
PyGellermann is available on PyPI and can be installed using pip:

    pip install pygellermann

For details on how to use `pip`, see the [Python Packaging User Guide](https://packaging.python.org/tutorials/installing-packages/) or [pip's User Guide](https://pip.pypa.io/en/stable/user_guide/).

Alternatively, you can download the GUI as a standalone executable for Linux, macOS, and Windows from the [releases page](https://github.com/YannickJadoul/PyGellermann/releases).

**Note**: On macOS, opening the PyGellermann app bundle might at first be blocked because it is not signed or distributed through the App Store. To override this and open the app, right-click on the app bundle and select *Open* from the context menu. This will open a dialog asking you to confirm that you want to open the app. After that, you can open the app by double-clicking on it. For more details, see [the macOS User Guide](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac).

## Usage
### Graphical User Interface
After installation, you can run the GUI by typing `pygellermann-gui` in your terminal or by running the standalone executable (`PyGellermann`, `PyGellermann.app`, or `PyGellermann.exe`). The following window should appear:

![PyGellermann GUI](https://raw.githubusercontent.com/YannickJadoul/PyGellermann/main/docs/gui.png)

Four parameters can be set to customize the generated Gellermann series:
- *Sequence length*: The length of each generated sequence.
- *Number of sequences*: The number of sequences to generate.
- *Alternation tolerance*: How close to 50% chance level a sequence needs to be when compared to single or double alternation.
- *Choices*: The two possible choices for each stimulus in the sequences.
- *Random seed*: The seed for the random number generator, allowing to deterministically generate the same sequences.

The *Generate* button will then generate the requested number of sequences, and display them in the table underneath.

Finally, the generated Gellermann series can be copied to the clipboard (*Copy*) or saved to a CSV file (*Save...*).

### Python API
The Python API consists of 4 simple functions:

- `is_gellermann_series(s, alternation_tolerance=DEFAULT_ALTERNATION_TOLERANCE)`

  Check if a binary sequence is a Gellermann series.

  #### Parameters
  - `s` : `Sequence[Any]`

    A binary series (i.e., containing two different elements) of even length.

  - `alternation_tolerance` : `float`, optional

    The tolerance around 50% chance level compared to single or double alternation, a value between 0 and 0.5 (default: 0.1).

  #### Returns
  - `bool`

    True if the given sequence is a Gellermann series, False otherwise.

  #### Raises
  - `ValueError`

    If the sequence length is not even, or if the sequence contains more than two different elements, or if the alternation tolerance is not between 0 and 0.5.

  #### Examples
  ```pycon
  >>> is_gellermann_series(['B', 'B', 'A', 'B', 'A', 'B', 'B', 'A', 'A', 'A'])
  True
  >>> is_gellermann_series('1112212122122211', alternation_tolerance=0.2)
  True
  >>> is_gellermann_series('1112212122122211', alternation_tolerance=0.0)
  False
  ```

- `generate_gellermann_series(n, m, choices=('A', 'B'), rng=None, **kwargs)`

  Generate m random Gellermann series of length n.

  #### Parameters
  - `n` : `int`

    The length of the series.

  - `m` : `int`

    The number of series to generate.

  - `choices` : `Tuple[Any, Any]`, optional

    The two elements of the series (default: ('A', 'B')).

  - `rng` : `np.random.Generator`, optional

    A NumPy random number generator (default: `None`, which uses the default NumPy random number generator).

  - `max_iterations` : `int`, optional

    The maximum number of iterations to try to generate all Gellermann series (default: `None`, which tries indefinitely).

  - `kwargs`

    Additional keyword arguments passed to `is_gellermann_series`.

  #### Yields
  - `Iterator[Sequence[Any]]`

    A generator object with m Gellermann series of length n.


- `generate_all_gellermann_series(n, choices, **kwargs)`
  Generate all Gellermann series of length n in lexicographic order.

  #### Parameters
  - `n` : `int`

    The length of the series.

  - `choices` : `Tuple[Any, Any]`, optional

      The two elements of the series (default: ('A', 'B')).

  - `kwargs`

      Additional keyword arguments passed to `is_gellermann_series`.

  #### Yields
  - `Iterator[Sequence[Any]]`

    A generator object with all Gellermann series of length n.


- `generate_gellermann_series_table(n, m, long_format: bool = False, **kwargs)`

  Generate a Pandas DataFrame of m random Gellermann series of length n.

  In the wide format, the DataFrame has columns 'series_i', 'element_0', 'element_1', ..., 'element_{n-1}', and each row contains a full series. In the long format, the DataFrame has columns 'series_i', 'element_i', 'element', and each row contains a single element of a series.

  #### Parameters
  - `n` : `int`

    The length of the series.

  - `m` : `int`

    The number of series to generate.

  - `long_format` : `bool`, optional

    If True, the DataFrame is in long format (default: False).

  - `kwargs`

    Additional keyword arguments passed to `generate_gellermann_series`.

  #### Returns
  - `pd.DataFrame`

    A Pandas DataFrame of m random Gellermann series of length n.


## License

PyGellermann is released under the GNU General Public License v3 or later. See the LICENSE file for details.

PyGellermann was developed at the [Comparative Bioacoustics Group](https://www.mpi.nl/department/comparative-bioacoustics/20) of the [Max Planck Institute for Psycholinguistics](https://www.mpi.nl/), Nijmegen, the Netherlands.

## References

[^Gellermann1933]: Gellermann, L. W. (1933). Chance orders of alternating stimuli in visual discrimination experiments. *The Journal of Genetic Psychology, 42*, 206-208.
