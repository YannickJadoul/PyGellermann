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


from . import gellermann

import pandas as pd

from qtpy import QtCore, QtGui, QtWidgets

import sys


class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()

        self._series = []
        self._was_saved = False

        self.setWindowTitle("PyGellermann")
        self.setMinimumWidth(500)

        self._sequence_length_spinbox = QtWidgets.QSpinBox()
        self._sequence_length_spinbox.setRange(10, 100)
        self._sequence_length_spinbox.setValue(10)
        self._number_of_sequences_spinbox = QtWidgets.QSpinBox()
        self._number_of_sequences_spinbox.setRange(1, 1000)
        self._number_of_sequences_spinbox.setValue(5)
        self._alternation_tolerance_spinbox = QtWidgets.QDoubleSpinBox()
        self._alternation_tolerance_spinbox.setRange(0.0, 0.5)
        self._alternation_tolerance_spinbox.setSingleStep(0.01)
        self._alternation_tolerance_spinbox.setValue(0.1)

        self._option1_lineedit = QtWidgets.QLineEdit()
        self._option1_lineedit.setText("A")
        self._option2_lineedit = QtWidgets.QLineEdit()
        self._option2_lineedit.setText("B")
        self._option1_lineedit.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        self._option2_lineedit.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)

        generate_button = QtWidgets.QPushButton("Generate")
        generate_button.clicked.connect(self._generate)

        self._results_table = QtWidgets.QTableWidget()
        self._results_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self._results_table.horizontalHeader().setVisible(False)
        self._results_table.setMinimumHeight(200)

        self._results_widget = QtWidgets.QWidget()
        self._results_widget.setVisible(False)

        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.clicked.connect(self._clear)
        copy_button = QtWidgets.QPushButton("&Copy")
        copy_button.clicked.connect(self._copy)
        copy_button.setShortcut(QtGui.QKeySequence.Copy)
        save_button = QtWidgets.QPushButton("&Save...")
        save_button.clicked.connect(self._save)
        save_button.setShortcut(QtGui.QKeySequence.Save)
        self._selected_format = None

        input_layout = QtWidgets.QFormLayout()
        input_layout.addRow("Sequence &length:", self._sequence_length_spinbox)
        input_layout.addRow("&Number of sequences:", self._number_of_sequences_spinbox)
        input_layout.addRow("&Alternation tolerance:", self._alternation_tolerance_spinbox)
        input_layout.addRow("Choices:", self._option1_lineedit)
        input_layout.addRow("", self._option2_lineedit)
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

        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
    

    def closeEvent(self, event):
        if not self._check_unsaved_changes():
            event.ignore()
    

    def _check_unsaved_changes(self):
        if not self._series or self._was_saved:
            return True

        reply = QtWidgets.QMessageBox.question(self, "Unsaved changes", "These generated Gellermann series have not been saved yet. Do you want to save them?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Yes:
            return self._save()
        elif reply == QtWidgets.QMessageBox.No:
            return True
        else:
            return False


    def _generate(self):
        if not self._check_unsaved_changes():
            return

        n = self._sequence_length_spinbox.value()
        k = self._number_of_sequences_spinbox.value()
        alternation_tolerance = self._alternation_tolerance_spinbox.value()
        choices = (self._option1_lineedit.text(), self._option2_lineedit.text())

        progress_dialog = QtWidgets.QProgressDialog("Generating series...", "Cancel", 0, k, self)
        progress_dialog.setMinimumDuration(500)
        progress_dialog.setModal(True)

        self._series = []
        for s in gellermann.generate_gellermann_series(n, k, alternation_tolerance=alternation_tolerance, choices=choices):
            self._series.append(s)
            progress_dialog.setValue(len(self._series))
            if progress_dialog.wasCanceled():
                break
        
        if progress_dialog.wasCanceled():
            self._series = []
            self._results_table.clearContents()
            self._results_widget.setVisible(False)
            return

        self._results_table.setRowCount(len(self._series))
        self._results_table.setColumnCount(len(self._series[0]))
        for i, row in enumerate(self._series):
            for j, element in enumerate(row):
                item = QtWidgets.QTableWidgetItem(element)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self._results_table.setItem(i, j, item)
        self._results_table.resizeColumnsToContents()
        self._results_table.resizeRowsToContents()
        self._results_widget.setVisible(True)

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
        self._results_widget.setVisible(False)
        QtCore.QTimer.singleShot(0, self.adjustSize)


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
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
