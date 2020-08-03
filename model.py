from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import pandas as pd


class DataModel(QtCore.QAbstractTableModel):
    """
    Pandas DataFrame Model
    """

    def __init__(self, header):
        super(DataModel, self).__init__()
        self.header = header
        self._data = pd.DataFrame(columns=self.header)
        self.captured = False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def headerData(self, col, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[col])
            if orientation == Qt.Vertical:
                return str(self._data.index[col])

    def append(self, dct):
        if self.captured:
            self._data = self._data.append(dct, ignore_index=True)
            self.layoutChanged.emit()

    def enable(self):
        self.captured = True

    def disable(self):
        self.captured = False

    @property
    def df(self):
        return self._data

    def load(self, df):
        self._data = pd.DataFrame(columns=self.header)
        self._data = self._data.append(df, ignore_index=True)
        self.layoutChanged.emit()

    def clear(self):
        self._data = pd.DataFrame(columns=self.header)
        self.layoutChanged.emit()
