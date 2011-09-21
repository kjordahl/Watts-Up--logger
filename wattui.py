#!/usr/bin/env python
"""
display data from WattsUp power meter

Usage: wattui.py

Based on a TraitsUI tutorial by Gael Varoquaux
http://github.enthought.com/traitsui/tutorials/traits_ui_scientific_app.html

Author: Kelsey Jordahl
Copyright: Kelsey Jordahl 2011
License: GPLv3
Time-stamp: <Tue Sep 20 21:54:15 EDT 2011>

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

import os, serial
import datetime, time
import argparse
import curses
from platform import uname
import numpy as np
#import matplotlib.pyplot as plt

import wx
import matplotlib
# We want matplotlib to use a wxPython backend
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from threading import Thread
from time import sleep
from traits.api import HasTraits, Instance, Int, Bool, Float, Enum, String, Button, Event
from traitsui.api import View, Item, ButtonEditor, HGroup, Handler, UIInfo, spring
from traitsui.wx.extra.led_editor import LEDEditor

EXTERNAL_MODE = 'E'
INTERNAL_MODE = 'I'
TCPIP_MODE = 'T'
FULLHANDLING = 2

SIM = True                              # TODO: set this in UI (or guess it)

class LoggingThread(Thread):
    def run(self):
        if SIM:
            self.s = open('samples/iphone4.raw','r')     # not a serial port, but a file
        else:
            self.s = serial.Serial(port, 115200 )
        print 'Logging started\n'
        n = 0
        while not self.wants_abort:
            line = self.s.readline()
            if line.startswith( '#d' ):
                fields = line.split(',')
                if len(fields)>5:
                    W = float(fields[3]) / 10;
                    V = float(fields[4]) / 10;
                    A = float(fields[5]) / 1000;
                    self.update_data(W, V, A)
                    #print n, W, V, A
                    n += 1
            if SIM:
                time.sleep(1)
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
    mode = Enum('External', 'Internal',
                desc = 'Meter logging mode',
                label = 'Mode')
    port = String('/dev/tty.usbserial-A1000wT3',
                  desc = 'Serial port location',
                  label = 'Serial port')
    button_label = String('Start')
    start = Event
    logging_thread = Instance(LoggingThread)

    def update_data(self, W, V, A):
        self.power = W
        self.voltage = V
        self.current = A
        
    def _start_fired(self):
        #self.interval +=1
        if self.logging_thread and self.logging_thread.isAlive():
            self.logging_thread.wants_abort = True
            self.button_label = 'Start'
        else:
            self.logging_thread = LoggingThread()
            self.logging_thread.wants_abort = False
            self.logging_thread.update_data = self.update_data
            self.logging_thread.start()
            self.button_label = 'Stop'

    view = View(Item('power', height = -40), Item('voltage', height = -40),
                Item('current', height = -40),
                'interval', 'mode', 'port',
                Item('start', label = 'Logging',
                     editor = ButtonEditor(label_value = 'button_label')))

def main(args):
    WattsUp().configure_traits()
    wx.PySimpleApp().MainLoop()

if __name__ == '__main__':
    # args not currently used in GUI program
    parser = argparse.ArgumentParser(description='Get data from Watts Up power meter.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='debugging output')
    parser.add_argument('-m', '--simulation-mode', dest='sim', action='store_true', help='simulate logging by reading serial data from disk with delay of sample interval between lines')
    parser.add_argument('-i', '--internal-mode', dest='internal', action='store_true', help='Set meter to internal logging mode')
    parser.add_argument('-f', '--fetch', dest='fetch', action='store_true', help='Fetch data stored on the meter (NOT YET WORKING!)')
    parser.add_argument('-g', '--graphics-mode', dest='plot', action='store_true', help='Graphical output: plot the data (NOT YET WORKING!)')
    parser.add_argument('-l', '--log', dest='log', action='store_true', help='log data in real time')
    parser.add_argument('-r', '--raw', dest='raw', action='store_true', help='output raw file')
    parser.add_argument('-o', '--outfile', dest='outfile', default='log.out', help='Output file')
    parser.add_argument('-s', '--sample-interval', dest='interval', default=1, help='Sample interval (default 1 s)')
    parser.add_argument('-p', '--port', dest='port', default=None, help='USB serial port')
    args = parser.parse_args()
    main(args)
