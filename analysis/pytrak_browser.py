#!/usr/bin/env python

import sys, time
from PyQt4.QtCore import SIGNAL, Qt, QCoreApplication
from PyQt4 import QtGui

import numpy as np
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

import pytrak_data

class AppForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Pytrak Browser')

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.sensor_colours = ['g', 'b', 'm', 'c']
        self.data = None
        self.block_drawing = False
        self.velocity = None
        self.on_draw()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"

        path = unicode(QtGui.QFileDialog.getSaveFileName(self,
                        'Save file', '',
                        file_choices))
        if path:
            self._gui_canvas.print_figure(path, dpi=self._gui_dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)

    def on_about(self):
        msg = """
Pytrak Browser

(c) Oliver Lindemann
"""
        QtGui.QMessageBox.about(self, "About the demo", msg.strip())

    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        #
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points

        QtGui.QMessageBox.information(self, "Click!", msg)


    def on_convert_csv(self):
        diag = QtGui.QFileDialog()
        self.filename = unicode(diag.getOpenFileName(self,
                        'Get CSV file', "",
                        "*.csv"))
        pytrak_data.convert_data2npz(self.filename)

    def on_load_data(self):
        self.block_drawing = True
        self.filename = unicode(QtGui.QFileDialog.getOpenFileName(self,
                        'Load file', "",
                        "pytrak npz (*.npz)"))

        self.setWindowTitle("PyTrak browser: " + self.filename)
        self._gui_velocity_cb.setChecked(False)
        self.sensor_ids, self.data, self.timestamps, self.quality = \
            pytrak_data.load_npz(self.filename)
        self.x_position = 0
        self.reset_values()

        for i in self.sensor_ids:
            self._gui_sensor_cb[i-1].setChecked(True)

        self.block_drawing = False
        self.on_draw()

    def set_ylims(self):
        try:
            self.y_lim = map(lambda x:int(float(x)),
                             self._gui_txt_ylims.text().split(","))
            if len(self.y_lim) != 2:
                self.y_lim = [int(np.min(self.data)), int(np.max(self.data))]
        except:
                self.y_lim = [int(np.min(self.data)), int(np.max(self.data))]
        self._gui_txt_ylims.setText("{0}, {1}".format(self.y_lim[0], self.y_lim[1]))
        self.on_draw()

    def reset_values(self):
        self.window_width = 10000
        self.window_overlap = 500
        self.n_sensors = np.shape(self.data)[0]
        self.n_samples = np.shape(self.data)[1]
        self.velocity = None
        self.set_ylims()
        self._gui_slider.setRange(1, self.n_samples - self.window_width)


    def on_draw(self):
        """ Redraws the figure
        """
        # clear the axes and redraw the plot anew
        #
        if self.data is None or self.block_drawing:
            return
        self._gui_back.setDisabled(self.x_position == 0)
        self._gui_forward.setDisabled(self.x_position+self.window_width >= self.n_samples)
        self._gui_slider.setValue(self.x_position)
        xrange = range(self.x_position, self.x_position + self.window_width)
        for i in range(3):  # 3 parameter (xyz)
            ax = self._gui_axes[i]
            ax.clear()
            ax.grid(self._gui_grid_cb.isChecked())
            if i<2:
                ax.set_xticklabels([])
            if i==2 and self._gui_velocity_cb.isChecked():
                ylim_velocity = [np.min(self.velocity), np.max(self.velocity)]
                for s in range(self.n_sensors):
                    if self._gui_sensor_cb[s].isChecked():
                        ax.plot(self.timestamps[xrange],
                                self.velocity[xrange,s],
                                color = self.sensor_colours[s])
                        ax.set_ylim(ylim_velocity)

            else:
                for s in range(self.n_sensors):
                    if self._gui_sensor_cb[s].isChecked():
                        ax.plot(self.timestamps[xrange],
                                self.data[s, xrange,i],
                                color = self.sensor_colours[s])
                        ax.set_ylim(self.y_lim)
            # marker
            #for tmp in filter(lambda x: x >= self.x_position and\
            #                            x <= self.x_position + self.window_width,\
            #                               self.boarder_crossing[s]):
            #ax.axvline(tmp, color=self.sensor_colours[s])

        self._gui_canvas.draw()

    def on_velocity(self):
        if self._gui_velocity_cb.isChecked():
            if self.velocity is None:
                self.velocity = pytrak_data.velocity(self.data, self.timestamps)
        self.on_draw()

    def on_back(self):
        self.x_position -= (self.window_width - self.window_overlap)
        if self.x_position < 0:
            self.x_position = 0

        self.on_draw()

    def on_forward(self):
        self.x_position += (self.window_width - self.window_overlap)
        if self.x_position + self.window_width  > self.n_samples:
            self.x_position = self.n_samples - (self.window_width)
        self.on_draw()

    def on_slider(self):
        self.x_position =  self._gui_slider.value()
        self.on_draw()

    def create_main_frame(self):
        self._gui_main_frame = QtGui.QWidget()

        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        self._gui_dpi = 100
        self._gui_fig = Figure((15.0, 6.0), dpi=self._gui_dpi)
        self._gui_canvas = FigureCanvas(self._gui_fig)
        self._gui_canvas.setParent(self._gui_main_frame)

        # Since we have only one plot, we can use add_axes
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self._gui_axes = []
        self._gui_axes.append(self._gui_fig.add_subplot(311))
        self._gui_axes.append(self._gui_fig.add_subplot(312))
        self._gui_axes.append(self._gui_fig.add_subplot(313))
        matplotlib.rcParams.update({'font.size': 8})

        # Bind the 'pick' event for clicking on one of the bars
        #
        self._gui_canvas.mpl_connect('pick_event', self.on_pick)

        # Create the navigation toolbar, tied to the canvas
        #
        #self._gui_mpl_toolbar = NavigationToolbar(self._gui_canvas, self._gui_main_frame)

        # check boxes
        #
        self._gui_sensor_cb =[]
        for i in range(4):
            self._gui_sensor_cb.append(QtGui.QCheckBox("Sensor {0}".format(i+1)))
            self._gui_sensor_cb[-1].setChecked(False)
            self.connect(self._gui_sensor_cb[-1], SIGNAL('stateChanged(int)'),
                         self.on_draw)

        self._gui_txt_ylims = QtGui.QLineEdit()
        self._gui_txt_ylims.setMaximumWidth(100)
        self.connect(self._gui_txt_ylims, SIGNAL('editingFinished ()'),
                    self.set_ylims)
        self._gui_grid_cb = QtGui.QCheckBox("Show &Grid")
        self._gui_grid_cb.setChecked(False)
        self.connect(self._gui_grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)

        self._gui_velocity_cb = QtGui.QCheckBox("Velocity plot")
        self._gui_velocity_cb.setChecked(False)
        self.connect(self._gui_velocity_cb, SIGNAL('stateChanged(int)'), self.on_velocity)

        hbox1 = QtGui.QHBoxLayout()
        for w in self._gui_sensor_cb + [self._gui_velocity_cb, self._gui_grid_cb,
                            QtGui.QLabel('y_lim:'), self._gui_txt_ylims, ]:
            hbox1.addWidget(w)
            hbox1.setAlignment(w, Qt.AlignVCenter)


        # back, forward, slider
        #
        self._gui_back = QtGui.QPushButton("&<<")
        self.connect(self._gui_back, SIGNAL('clicked()'), self.on_back)
        self._gui_forward= QtGui.QPushButton("&>>")
        self.connect(self._gui_forward, SIGNAL('clicked()'), self.on_forward)


        self._gui_slider = QtGui.QSlider(Qt.Horizontal)
        self._gui_slider.setTracking(True)
        #self._gui_slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.connect(self._gui_slider, SIGNAL('valueChanged(int)'), self.on_slider)

        hbox2 = QtGui.QHBoxLayout()
        for w in [self._gui_back, self._gui_forward, self._gui_slider]:
            hbox2.addWidget(w)
            hbox2.setAlignment(w, Qt.AlignVCenter)


        # add all to main frame
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self._gui_canvas)
        # vbox.addWidget(self._gui_mpl_toolbar)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self._gui_main_frame.setLayout(vbox)
        self.setCentralWidget(self._gui_main_frame)

    def create_status_bar(self):
        self._gui_status_text = QtGui.QLabel("This is a demo")
        self.statusBar().addWidget(self._gui_status_text, 1)

    def create_menu(self):
        self._gui_data_menu = self.menuBar().addMenu("&Data")

        quit_action = self.create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")
        load_data_action = self.create_action("&Load data",
            shortcut="Ctrl+O", slot=self.on_load_data,
            tip="Load Pytrak Data")
        convert = self.create_action("&Convert csv to npz",
            slot=self.on_convert_csv,
            tip="Convert CSV data to npz file")
        self.add_actions(self._gui_data_menu,
            (load_data_action, None, convert, None, quit_action))


        self._gui_extras_menu = self.menuBar().addMenu("&Extras")
        save_plot = self.create_action("&Save plot",
            shortcut="Alt+Ctrl+S", slot=self.save_plot,
            tip="Load data")

        about_action = self.create_action("&About",
            shortcut='F1', slot=self.on_about,
            tip='About the demo')

        self.add_actions(self._gui_extras_menu, (save_plot, None, about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False,
                        signal="triggered()"):
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


def main():
    app = QtGui.QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
