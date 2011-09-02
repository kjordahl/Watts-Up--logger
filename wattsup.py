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
Time-stamp: <Fri Sep  2 17:10:50 EDT 2011>

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

import datetime
import serial

EXTERNAL_MODE = 'E'
INTERNAL_MODE = 'I'
TCPIP_MODE = 'T'
FULLHANDLING = 2

#SERIAL_PORT = '/dev/ttyUSB0'            # Linux
SERIAL_PORT = '/dev/tty.usbserial-A1000wT3' # OS X

class WattsUp(object):
    def __init__(self):
        self.s = serial.Serial( SERIAL_PORT, 115200 )
        self.logfile = None
        self.interval = 1

    def mode(self, runmode, interval = 1):
        self.interval = interval
        self.s.write('#L,W,3,%s,,%d;' % (runmode, interval) )
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
        while True:
            if line.startswith( '#d' ):
                fields = line.split(',')
                W = float(fields[3]) / 10;
                V = float(fields[4]) / 10;
                A = float(fields[5]) / 1000;
                print datetime.datetime.now(), n, W, V, A
                if self.logfile:
                    o.write('%s %d %3.1f %3.1f %5.3f\n' % (datetime.datetime.now(), n, W, V, A))
                n += self.interval
            line = self.s.readline()


def main():
    meter = WattsUp()
    #    meter.log('log.out')
    meter.fetch()
    meter.mode(INTERNAL_MODE)

if __name__ == '__main__':
    main()
