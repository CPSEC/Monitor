import json
import os
import random
import socket
import sys
import time
from datetime import datetime
import pandas as pd
import numpy as np

import pyqtgraph as pg
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog, QCheckBox, QVBoxLayout

from config import header, port, sep, x_1, y_1, interv_1
from model import DataModel
from server import Server
from ui.main import Ui_MainWindow
from ui.adjust import Ui_Dialog


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.control_panel = ControlPanel()
        self.control_panel.updated.connect(self.send_data)

        # for table
        self.model = DataModel(header)
        self.tableView.setModel(self.model)
        self.vbar = self.scrollArea.verticalScrollBar()

        # for server thread
        self.thread_pool = QThreadPool()
        self.server = None
        self.message_queues = {}

        # for plot_1
        self.canvas_1 = pg.PlotWidget()
        self.canvas_1.setBackground("w")
        self.canvas_1.addLegend()
        self.plot_1_canvas.addWidget(self.canvas_1)
        self.Slider_1.setValue(99)
        self.Slider_1.valueChanged.connect(self.slider_handle_1)
        self.lines = []
        self.y_1 = y_1
        self.init_plot_1()

        # checkbox for plot 1
        self.plot_1_items = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.checkboxes = []
        for i in header:
            if i in x_1:
                continue
            checkbox = QCheckBox(i)
            if i in y_1:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.check1state)
            self.plot_1_items.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        # live video
        win = pg.GraphicsLayoutWidget()
        win.setBackground("w")
        self.video.addWidget(win)
        view = win.addViewBox()
        self.imv = pg.ImageItem()
        view.addItem(self.imv)
        self.vcount = 0

        # ACTIONS
        self.actionListening.triggered.connect(self.start_server)
        self.actionClose.triggered.connect(self.stop_server)
        self.actionStart.triggered.connect(self.enable_recording)
        self.actionStop.triggered.connect(self.disable_recording)
        self.actionNew.triggered.connect(self.reset_data)
        self.actionOpen.triggered.connect(self.file_open)
        self.actionSave.triggered.connect(self.file_save)
        self.actionTest.triggered.connect(self.send_data)
        self.actionAdjust.triggered.connect(self.show_control_panel)

    def check1state(self, state):
        self.y_1 = [c.text() for c in self.checkboxes if c.isChecked()]
        self.statusbar.showMessage('plot '+str(self.y_1))
        self.init_plot_1()

    def init_plot_1(self):
        self.canvas_1.clear()
        self.lines = []
        for y in self.y_1:
            # plot each line
            r = random.randrange(256)
            g = random.randrange(256)
            b = random.randrange(256)
            pen = pg.mkPen(color=(r, g, b))
            line = self.canvas_1.plot(name=y, pen=pen)
            self.lines.append(line)


    def start_server(self):
        self.server = Server(self.message_queues, port=port, sep=sep)
        self.server.signals.connected.connect(self.client_connect)
        self.server.signals.closed.connect(self.client_close)
        self.server.signals.result.connect(self.client_data)
        self.thread_pool.start(self.server)
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        msg = 'IP:' + IPAddr + '  Server is listening at port ' + str(port) + '!'
        self.statusbar.showMessage(msg)
        # availability
        self.actionListening.setEnabled(False)
        self.actionClose.setEnabled(True)
        self.actionStart.setEnabled(True)
        self.actionOpen.setEnabled(False)

    def stop_server(self):
        self.server.kill()
        self.model.disable()
        self.statusbar.showMessage('Server stopped listening.')
        # availability
        self.actionListening.setEnabled(True)
        self.actionClose.setEnabled(False)
        self.actionStart.setEnabled(False)
        self.actionStop.setEnabled(False)
        self.actionOpen.setEnabled(True)

    def client_connect(self, s):
        msg = 'Connected from ' + s + '!'
        self.statusbar.showMessage(msg)
        self.actionAdjust.setEnabled(True)

    def client_close(self, s):
        msg = 'Closed from ' + s + '!'
        self.statusbar.showMessage(msg)
        self.actionAdjust.setEnabled(False)
        self.control_panel.close()

    def plot_last(self):
        data = self.model.df
        for i, y in enumerate(self.y_1):
            data_x = data[x_1][-interv_1:].tolist()
            data_y = data[y][-interv_1:].tolist()
            self.lines[i].setData(x=data_x, y=data_y)

    def plot_range(self, a, b):
        data = self.model.df
        for i, y in enumerate(self.y_1):
            data_x = data[x_1][a:b].tolist()
            data_y = data[y][a:b].tolist()
            self.lines[i].setData(x=data_x, y=data_y)

    def client_data(self, s):
        data_dict = json.loads(s)
        if 'sensor' in data_dict:
            sensor_dict = data_dict['sensor']
            self.model.append(sensor_dict)
            self.tableView.scrollToBottom()
            self.plot_last()
        if 'parameter' in data_dict:
            self.control_panel.parameters = data_dict['parameter']
            data_print = json.dumps(data_dict['parameter'], indent=4)
            self.plainTextEdit.setPlainText(data_print)
        if 'image' in data_dict:
            self.vcount += 1
            # for performance
            if self.vcount % 5 == 0:
                img_lst = data_dict['image']
                img_np = np.array(img_lst)
                self.imv.setImage(img_np)

    def slider_handle_1(self, val):
        # val 0-99
        row_count = self.model.rowCount()
        if row_count <= interv_1:
            a = 0
            b = row_count
            self.plot_range(a, b)
        else:
            total = row_count - interv_1 + 1
            a = int(total * val / 99)
            b = a + interv_1
            self.plot_range(a, b)

    def enable_recording(self):
        self.model.enable()
        self.statusbar.showMessage('Start recording.')
        # availability
        self.actionStart.setEnabled(False)
        self.actionStop.setEnabled(True)

    def disable_recording(self):
        self.model.disable()
        self.statusbar.showMessage('Stop recording.')
        # availability
        self.actionStop.setEnabled(False)
        self.actionStart.setEnabled(True)

    def reset_data(self):
        self.model.clear()
        self.init_plot_1()
        # self.data_line_1.setData([], [])

    def file_save(self):
        path = os.path.split(os.path.realpath(__file__))[0]
        expected_filename = 'data_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.csv'
        expected_filepath = os.path.join(path, 'data')
        if not os.path.exists(expected_filepath):
            os.makedirs(expected_filepath)
        filename = QFileDialog.getSaveFileName(self, 'Save CSV file',
                                               os.path.join(expected_filepath, expected_filename),
                                               'CSV files (*.csv)')
        if filename[0]:
            self.model.df.to_csv(filename[0], index=False)
            self.statusbar.showMessage('Save data to ' + filename[0])

    def file_open(self):
        path = os.path.split(os.path.realpath(__file__))[0]
        expected_filepath = os.path.join(path, 'data')
        if not os.path.exists(expected_filepath):
            os.makedirs(expected_filepath)
        filename = QFileDialog.getOpenFileName(self, 'Open CSV file',
                                               expected_filepath, 'CSV files (*.csv)')
        if filename[0]:
            df = pd.read_csv(filename[0])
            self.model.load(df)
            self.tableView.scrollToBottom()
            self.plot_last()
            self.Slider_1.setValue(99)
            self.statusbar.showMessage('Load data from ' + filename[0])

    def send_data(self, d_dict):
        # print(d_dict)
        d_str = json.dumps(d_dict)+sep
        for i in self.message_queues:
            self.message_queues[i].put(d_str.encode())

    def closeEvent(self, event):
        if self.server is None:
            pass
        else:
            self.stop_server()
        del self.control_panel
        self.statusbar.showMessage('Quiting...')
        time.sleep(0.5)
        event.accept()

    def show_control_panel(self):
        self.control_panel.show()


class ControlPanel(QDialog, Ui_Dialog):

    updated = pyqtSignal(dict)

    def __init__(self, *args, obj=None, **kwargs):
        super(QDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.parameters = None
        self.reset_button.clicked.connect(self.reset)
        self.autocontrol.stateChanged.connect(self.auto_check)
        self.update_button.clicked.connect(self.update_data)
        self.data_sent = {'auto': 'false',
                          "servo": 1.5,
                          "throttle": 1.5,
                          "speed": 40,
                          "servo-PID": {"P": 0, "I": 0, "D": 0},
                          "throttle-PID": {"P": 0, "I": 0, "D": 0}
                          }

    def reset(self):
        if self.parameters:
            if 'rspeed' in self.parameters:
                self.rspeed.setText(str(self.parameters['rspeed']))
            if 'mp' in self.parameters:
                self.mp.setText(str(self.parameters['mp']))
            if 'mi' in self.parameters:
                self.mi.setText(str(self.parameters['mi']))
            if 'md' in self.parameters:
                self.md.setText(str(self.parameters['md']))
            if 'sp' in self.parameters:
                self.sp.setText(str(self.parameters['sp']))
            if 'si' in self.parameters:
                self.si.setText(str(self.parameters['si']))
            if 'sd' in self.parameters:
                self.sd.setText(str(self.parameters['sd']))
        if self.mpulse.text() == "":
            self.mpulse.setText(str(1.5))
        if self.spulse.text() == "":
            self.spulse.setText(str(1.5))
        self.update_button.setEnabled(True)

    def auto_check(self, state):
        if state == Qt.Checked:
            self.groupBox.setEnabled(True)
            self.groupBox_2.setEnabled(False)
            self.data_sent['auto'] = 'true'
        else:
            self.groupBox.setEnabled(False)
            self.groupBox_2.setEnabled(True)
            self.data_sent['auto'] = 'false'

    def update_data(self):
        try:
            self.data_sent['servo'] = float(self.spulse.text())
            self.data_sent['throttle'] = float(self.mpulse.text())
            self.data_sent['speed'] = float(self.rspeed.text())
            self.data_sent['servo-PID']['P'] = float(self.sp.text())
            self.data_sent['servo-PID']['I'] = float(self.si.text())
            self.data_sent['servo-PID']['D'] = float(self.sd.text())
            self.data_sent['throttle-PID']['P'] = float(self.mp.text())
            self.data_sent['throttle-PID']['I'] = float(self.mi.text())
            self.data_sent['throttle-PID']['D'] = float(self.md.text())
            self.updated.emit(self.data_sent)
        except:
            self.reset()


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # enable high_dpi scaling
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # use high_dpi icons
app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
