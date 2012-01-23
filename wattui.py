#!/usr/bin/env python
"""
display data from WattsUp power meter

Usage: wattui.py

Based on a TraitsUI tutorial by Gael Varoquaux
http://github.enthought.com/traitsui/tutorials/traits_ui_scientific_app.html

Author: Kelsey Jordahl
Copyright: Kelsey Jordahl 2011
License: GPLv3
Time-stamp: <Mon Jan 23 10:18:47 EST 2012>

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.  A copy of the GPL
    version 3 license can be found in the file COPYING or at
    <http://www.gnu.org/licenses/>.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

"""

# file to read as simulated serial port data
SIMFILE = 'samples/iphone4.raw'

import os, serial
import datetime, time
import argparse
import curses
from platform import uname
import numpy as np

import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from threading import Thread
from time import sleep
from traits.api import HasTraits, Instance, Int, Bool, Float, Enum, String, Button, Event
from traitsui.api import View, Item, ButtonEditor, Group, Handler, UIInfo, HSplit, spring
from traitsui.wx.editor import Editor
from traitsui.wx.basic_editor_factory import BasicEditorFactory
from traitsui.wx.extra.led_editor import LEDEditor

EXTERNAL_MODE = 'E'
INTERNAL_MODE = 'I'
TCPIP_MODE = 'T'
FULLHANDLING = 2

SIM = True                              # TODO: set this in UI (or guess it)

class _MPLFigureEditor(Editor):

    scrollable  = True

    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()

    def update_editor(self):
        pass

    def _create_canvas(self, parent):
        """ Create the MPL canvas. """
        # The panel lets us add additional controls.
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        # matplotlib commands to create a canvas
        mpl_control = FigureCanvas(panel, -1, self.value)
        sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)
        toolbar = NavigationToolbar2Wx(mpl_control)
        sizer.Add(toolbar, 0, wx.EXPAND)
        self.value.canvas.SetMinSize((400,300))
        return panel

class MPLFigureEditor(BasicEditorFactory):

    klass = _MPLFigureEditor

class LoggingThread(Thread):
    def run(self):
        if SIM:
            self.s = open(SIMFILE, 'r')     # not a serial port, but a file
        else:
            self.s = serial.Serial(port, 115200 )
        print 'Logging started\n'
        n = 0
        p = []
        while not self.wants_abort:
            line = self.s.readline()
            if line.startswith( '#d' ):
                fields = line.split(',')
                if len(fields)>5:
                    W = float(fields[3]) / 10;
                    p.append(W)
                    V = float(fields[4]) / 10;
                    A = float(fields[5]) / 1000;
                    self.update_data(W, V, A)
                    self.plot_power(p)
                    #print n, W, V, A
                    n += 1
            if SIM:
                time.sleep(1 / args.speedup)
            #self.display.string = '%d \n' % n
        self.s.close()
        print 'Logging stopped\n'


class WattsUp( HasTraits ):
    
    power = Float(0.0,
                  label = 'Watts',height = -40,
                  editor = LEDEditor( format_str = '%5.1f') )
    voltage = Float(0.0,
                  label = 'Volts',height = -40,
                  editor = LEDEditor( format_str = '%5.1f') )
    current = Float(0.0,
                  label = 'Amps',height = -40,
                  editor = LEDEditor( format_str = '%5.3f') )

    interval = Int(1,
                   desc = 'Sample interval in seconds',
                   label = 'Sample interval (s)')
    mode = Enum('Simulated', 'External', 'Internal',
                desc = 'Meter logging mode',
                label = 'Mode')
    port = String('/dev/tty.usbserial-A1000wT3',
                  desc = 'Serial port location',
                  label = 'Serial port')
    button_label = String('Start')
    start = Event
    logging_thread = Instance(LoggingThread)
    figure = Instance(Figure, ())

    def update_data(self, W, V, A):
        self.power = W
        self.voltage = V
        self.current = A

    def _figure_default(self):
        figure = Figure()
        figure.add_axes([0.1, 0.15, 0.5, 0.75])
        return figure
    
    def _start_fired(self):
        if self.logging_thread and self.logging_thread.isAlive():
            self.logging_thread.wants_abort = True
            self.button_label = 'Start'
        else:
            self.logging_thread = LoggingThread()
            self.logging_thread.wants_abort = False
            self.logging_thread.update_data = self.update_data
            self.logging_thread.plot_power = self.plot_power
            self.logging_thread.figure = self.figure
            self.logging_thread.start()
            self.button_label = 'Stop'

    def plot_power(self,p):
        t = np.linspace(0,len(p)/60.0,len(p)) # should multiply by interval
        # print t.size, len(p)
        self.figure.axes[0].clear()
        self.figure.axes[0].plot(t,p,'r')
        self.figure.axes[0].set_xlabel('Time (minutes)')
        self.figure.axes[0].set_ylabel('Power (W)')
        wx.CallAfter(self.figure.canvas.draw)

    view = View(HSplit(Group(Item('power', height = -40), Item('voltage', height = -40),
                Item('current', height = -40),
                'interval', 'mode', 'port',
                Item('start', label = 'Logging',
                     editor = ButtonEditor(label_value = 'button_label'))),
                Item('figure', editor=MPLFigureEditor(),
                            dock='vertical', height = -400, width = -800,
                            resizable=True),
                            show_labels=False))

def main(args):
    WattsUp().configure_traits()
    wx.PySimpleApp().MainLoop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get data from Watts Up power meter.')
    parser.add_argument('-s', '--speedup', dest='speedup', default=1, type=float, help='Speed up simulation by factor (default 1)')
    args = parser.parse_args()
    main(args)
