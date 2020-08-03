import sys
from PyQt5 import QtWidgets # import PyQt5 before PyQtGraph
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot


class GraphCanvas(PlotWidget):
    def __init__(self):
        super(GraphCanvas, self).__init__()
        self.setBackground('w')
        self.model = None
        self.interval = 1000
        self.x = 0
        self.y = 1
        pen = pg.mkPen(color=(255, 0, 0))
        self.curve = plot(pen=pen)

    def setModel(self, model):
        self.model = model

    def setInterval(self, interval):
        self.interval = interval

    def setXY(self, x_str, y_str):
        self.x = x_str
        self.y = y_str

    def plot_last(self):
        data = self.model.df
        data_x = data[self.x][-self.interval:]
        data_y = data[self.y][-self.interval:]
        self.curve.setData(data_x.tolist(), data_y.tolist())
