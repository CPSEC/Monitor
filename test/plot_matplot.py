

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.model = None
        self.interval = 1000
        self.x = 0
        self.y = 1
        self._plot_ref = None
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

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
        # if self._plot_ref is None:
        #     plot_refs = self.axes.plot(data_x, data_y)
        #     self._plot_ref = plot_refs[0]
        # else:
        #     self._plot_ref.set_xdata(data_x)
        #     self._plot_ref.set_ydata(data_y)
        self.axes.cla()
        self.axes.plot(data_x, data_y)
        self.draw()




