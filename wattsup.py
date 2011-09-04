#!/usr/bin/env python
"""
record data from WattsUp power meter

Output format will be space sperated containing:
YYYY-MM-DD HH:MM:SS.ssssss n W V A
where n is sample number, W is power in watts, V volts, A current in amps

Usage: wattsup.py

Author: Kelsey Jordahl
Copyright: Kelsey Jordahl 2011
License: GPLv3
Time-stamp: <Sun Sep  4 12:51:27 EDT 2011>

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
import datetime
import argparse
from platform import uname
import numpy as np
import matplotlib.pyplot as plt


EXTERNAL_MODE = 'E'
INTERNAL_MODE = 'I'
TCPIP_MODE = 'T'
FULLHANDLING = 2


class WattsUp(object):
    def __init__(self, port, interval):
        self.s = serial.Serial(port, 115200 )
        self.logfile = None
        self.interval = interval
        # initialize lists for keeping data
        self.t = []
        self.power = []
        self.potential = []
        self.current = []

    def mode(self, runmode):
        self.s.write('#L,W,3,%s,,%d;' % (runmode, self.interval) )
        if runmode == INTERNAL_MODE:
            self.s.write('#O,W,1,%d' % FULLHANDLING)

    def fetch(self):
        for line in self.s:
            if line.startswith( '#d' ):
                fields = line.split(',')
                W = float(fields[3]) / 10;
                V = float(fields[4]) / 10;
                A = float(fields[5]) / 1000;
                print datetime.datetime.now(), W, V, A

    def log(self, logfile = None):
        print 'Logging...'
        self.mode(EXTERNAL_MODE)
        if logfile:
            self.logfile = logfile
            o = open(self.logfile,'w')
        line = self.s.readline()
        n = 0
        if args.plot:
            fig = plt.figure()
        #    ax = fig.add_subplot(111)
        #    line1, = ax.plot(0, 0, 'r-')
        while True:
            if line.startswith( '#d' ):
                if args.debug:
                    print line
                fields = line.split(',')
                W = float(fields[3]) / 10;
                V = float(fields[4]) / 10;
                A = float(fields[5]) / 1000;
                if args.verbose:
                    print datetime.datetime.now(), n, W, V, A
                if args.plot:
                    self.t.append(float(n))
                    if args.debug:
                        print self.t
                    self.power.append(W)
                    self.potential.append(V)
                    self.current.append(A)
                    fig.clear()
                    plt.plot(np.array(self.t)/60,np.array(self.power))
                    ax = plt.gca()
                    ax.set_xlabel('Time (minutes)')
                    ax.set_ylabel('Power (W)')
                    # show the plot
                    fig.canvas.draw()
                if self.logfile:
                    o.write('%s %d %3.1f %3.1f %5.3f\n' % (datetime.datetime.now(), n, W, V, A))
                n += self.interval
            line = self.s.readline()


def main(args):
    if not args.port:
        system = uname()[0]
        if system == 'Darwin':          # Mac OS X
            args.port = '/dev/tty.usbserial-A1000wT3'
        if system == 'Linux':
            args.port = '/dev/ttyUSB0'
    if not os.path.exists(args.port):
        print ''
        print 'Serial port %s does not exist.' % args.port
        print 'Please make sure FDTI drivers are installed'
        print ' (http://www.ftdichip.com/Drivers/VCP.htm)'
        print 'Default ports are /dev/ttyUSB0 for Linux'
        print ' and /dev/tty.usbserial-A1000wT3 for Mac OS X'
        exit()
    meter = WattsUp(args.port, args.interval)
    if args.log:
        meter.log(args.outfile)
    if args.fetch:
        print 'WARNING: Fetch mode not working!!!!'
        meter.fetch()
    if args.internal:
        meter.mode(INTERNAL_MODE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get data from Watts Up power meter.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='debuggin output')
    parser.add_argument('-i', '--internal-mode', dest='internal', action='store_true', help='Set meter to internal logging mode')
    parser.add_argument('-f', '--fetch', dest='fetch', action='store_true', help='Fetch data stored on the meter (NOT YET WORKING!)')
    parser.add_argument('-g', '--graphics-mode', dest='plot', action='store_true', help='Graphical output: plot the data (NOT YET WORKING!)')
    parser.add_argument('-l', '--log', dest='log', action='store_true', help='log data in real time')
    parser.add_argument('-o', '--outfile', dest='outfile', default='log.out', help='Output file')
    parser.add_argument('-s', '--sample-interval', dest='interval', default=1, help='Sample interval (default 1 s)')
    parser.add_argument('-p', '--port', dest='port', default=None, help='USB serial port')
    args = parser.parse_args()
    main(args)
