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

"""GUI wrapping functionality for generating Gellermann series."""


from qtpy import QtCore, QtGui, QtWidgets

from . import __version__, gellermann

import numpy as np
import qdarktheme  # type: ignore

import sys


class ShorterLineEdit(QtWidgets.QLineEdit):
    def sizeHint(self):
        return QtCore.QSize(20, super().sizeHint().height())


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self._series = []
        self._was_saved = False

        self.setWindowTitle(f"PyGellermann {__version__}")
        self.setMinimumWidth(500)

        self._sequence_length_spinbox = QtWidgets.QSpinBox()
        self._sequence_length_spinbox.setRange(2, 100)
        self._sequence_length_spinbox.setSingleStep(2)
        self._sequence_length_spinbox.setValue(10)
        self._number_of_sequences_spinbox = QtWidgets.QSpinBox()
        self._number_of_sequences_spinbox.setRange(1, 1000)
        self._number_of_sequences_spinbox.setValue(5)
        self._alternation_tolerance_spinbox = QtWidgets.QDoubleSpinBox()
        self._alternation_tolerance_spinbox.setRange(0.0, 0.5)
        self._alternation_tolerance_spinbox.setSingleStep(0.01)
        self._alternation_tolerance_spinbox.setValue(0.1)

        self._option1_lineedit = ShorterLineEdit()
        self._option1_lineedit.setText("A")
        self._option2_lineedit = ShorterLineEdit()
        self._option2_lineedit.setText("B")

        random_seed_validator = QtGui.QIntValidator()
        random_seed_validator.setBottom(0)
        self._random_seed_lineedit = ShorterLineEdit()
        self._random_seed_lineedit.setValidator(random_seed_validator)
        self._random_seed_lineedit.setPlaceholderText("None")

        generate_button = QtWidgets.QPushButton("Generate")
        generate_button.clicked.connect(self._generate)

        self._results_table = QtWidgets.QTableWidget()
        self._results_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self._results_table.horizontalHeader().setVisible(False)
        self._results_table.setMinimumHeight(200)

        self._results_widget = QtWidgets.QWidget()
        self._results_widget.setVisible(False)

        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.clicked.connect(self._clear)
        copy_button = QtWidgets.QPushButton("&Copy")
        copy_button.clicked.connect(self._copy)
        copy_button.setShortcut(QtGui.QKeySequence.StandardKey.Copy)
        save_button = QtWidgets.QPushButton("&Save...")
        save_button.clicked.connect(self._save)
        save_button.setShortcut(QtGui.QKeySequence.StandardKey.Save)
        self._selected_format = ""

        input_layout = QtWidgets.QFormLayout()
        input_layout.addRow("Sequence &length:", self._sequence_length_spinbox)
        input_layout.addRow("&Number of sequences:", self._number_of_sequences_spinbox)
        input_layout.addRow("&Alternation tolerance:", self._alternation_tolerance_spinbox)
        input_layout.addRow("Choices:", self._option1_lineedit)
        input_layout.addRow("", self._option2_lineedit)
        input_layout.addRow("Random seed:", self._random_seed_lineedit)
        input_layout.addRow(generate_button)

        centered_input_layout = QtWidgets.QHBoxLayout()
        centered_input_layout.addStretch()
        centered_input_layout.addLayout(input_layout)
        centered_input_layout.addStretch()

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(clear_button)
        button_layout.addWidget(copy_button)
        button_layout.addWidget(save_button)

        results_layout = QtWidgets.QVBoxLayout()
        results_layout.addWidget(self._results_table)
        results_layout.addLayout(button_layout)
        results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_widget.setLayout(results_layout)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(centered_input_layout)
        main_layout.addWidget(self._results_widget)

        self.setLayout(main_layout)

        self._collapse_results()

    def closeEvent(self, event):
        if not self._check_unsaved_changes():
            event.ignore()

    def _check_unsaved_changes(self):
        if not self._series or self._was_saved:
            return True

        StandardButton = QtWidgets.QMessageBox.StandardButton
        message = "These generated Gellermann series have not been saved yet. Do you want to save them?"
        reply = QtWidgets.QMessageBox.question(self, "Unsaved changes", message, StandardButton.Yes | StandardButton.No | StandardButton.Cancel)
        if reply == StandardButton.Yes:
            return self._save()
        elif reply == StandardButton.No:
            return True
        else:
            return False

    def _generate(self):
        if not self._check_unsaved_changes():
            return

        n = self._sequence_length_spinbox.value()
        m = self._number_of_sequences_spinbox.value()
        alternation_tolerance = self._alternation_tolerance_spinbox.value()
        choices = (self._option1_lineedit.text(), self._option2_lineedit.text())

        if n % 2:
            QtWidgets.QMessageBox.critical(self, "Error", "PyGellermann cannot yet generate odd length Gellermann series.")
            return

        try:
            random_seed_text = self._random_seed_lineedit.text()
            random_seed = int(random_seed_text) if random_seed_text else None
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid random seed.")
            return
        rng = np.random.default_rng(random_seed)

        progress_dialog = QtWidgets.QProgressDialog("Generating series...", "Cancel", 0, m, self)
        progress_dialog.setWindowTitle("PyGellermann")
        progress_dialog.setMinimumDuration(500)
        progress_dialog.setModal(True)

        self._results_table.clearContents()
        self._results_table.setRowCount(0)

        self._series = []
        try:
            while len(self._series) < m:
                s = next(gellermann.generate_gellermann_series(n, 1, alternation_tolerance=alternation_tolerance,
                                                               choices=choices, rng=rng, max_iterations=1000), None)

                if progress_dialog.wasCanceled():
                    break

                if s is not None:
                    self._series.append(s)

                progress_dialog.setValue(len(self._series))
                QtWidgets.QApplication.processEvents()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            progress_dialog.cancel()
            progress_dialog.close()

        if progress_dialog.wasCanceled():
            self._series = []
            self._collapse_results()
            return

        self._results_table.setRowCount(len(self._series))
        self._results_table.setColumnCount(len(self._series[0]))
        for i, row in enumerate(self._series):
            for j, element in enumerate(row):
                item = QtWidgets.QTableWidgetItem(element)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # type: ignore
                self._results_table.setItem(i, j, item)
        self._results_table.setHorizontalHeaderLabels([""] * self._results_table.columnCount())
        min_width = (max(self._results_table.sizeHintForColumn(i) for i in range(self._results_table.columnCount())))
        self._results_table.horizontalHeader().setMinimumSectionSize(min_width)
        self._results_table.resizeColumnsToContents()
        self._results_table.resizeRowsToContents()
        self._expand_results()

        self._was_saved = False

    def _copy(self):
        row_strings = []
        for row in range(self._results_table.rowCount()):
            row_strings.append("\t".join(self._results_table.item(row, column).text() for column in range(self._results_table.columnCount())))
        QtWidgets.QApplication.clipboard().setText("\n".join(row_strings))

    def _clear(self):
        if not self._check_unsaved_changes():
            return

        self._series = []
        self._results_table.clearContents()
        self._results_table.setRowCount(0)
        self._collapse_results()

    def _collapse_results(self):
        self.installEventFilter(self)
        self._results_widget.setVisible(False)
        self.setMinimumHeight(self.sizeHint().height())
        QtCore.QTimer.singleShot(20, self.adjustSize)

    def _expand_results(self):
        self._results_widget.setVisible(True)
        self.setMinimumHeight(self.sizeHint().height())

    def _save(self):
        formats = [
            "Comma-separated file, wide-format (*.csv)",
            "Comma-separated file, long-format (*.csv)"
        ]
        name, selected = QtWidgets.QFileDialog.getSaveFileName(self, "Save generated series to file", "", ";;".join(formats), self._selected_format)

        if not name:
            return False
        self._selected_format = selected

        if selected == formats[0]:
            df = gellermann._series_to_wide_format_df(self._series)
        else:
            df = gellermann._series_to_long_format_df(self._series)

        try:
            df.to_csv(name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not save series to file:\n\n{e}")
            return False

        self._was_saved = True

        return True


def main():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    qdarktheme.enable_hi_dpi()

    app = QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme('auto')
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())  # type: ignore


if __name__ == '__main__':
    main()
