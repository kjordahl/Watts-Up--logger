#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
Plot data from WattsUp power meter

Format is assumed to be space sperated containing:
YYYY-MM-DD HH:MM:SS.ssssss n W V A
where n is sample number, W is power in Watts, V volts, A current in amps

Usage: plot.py log.out [plot.png]

Requires numpy and matplotlib

Author: Kelsey Jordahl
Copyright: Kelsey Jordahl 2011
License: GPLv3
Time-stamp: <Fri Sep  2 17:11:38 EDT 2011>

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

import sys, os
import numpy as np
from matplotlib import dates, pyplot

def main():
    if len(sys.argv) < 2:
        logfilename = 'log.out'         # use default filename
	print 'No input filename specified: using %s' % logfilename
    else:
        logfilename = sys.argv[1]
    if not os.path.exists(logfilename):
        print '%s does not exist!' % logfilename
        sys.exit()
    else:
        print 'Reading file %s' % logfilename
    if len(sys.argv) < 3:
        pngfilename = None
	print 'No output filename specified: will not write output file for plot'
    else:
        pngfilename = sys.argv[2]
        print 'Plot will be saved as %s' % pngfilename
    data = np.genfromtxt(logfilename, usecols = (2, 3, 4, 5))
    t = data[:,0]
    w = data[:,1]
    i = data[:,3]
    pyplot.plot(t/60,w)
    ax = pyplot.gca()
    ax.set_xlabel('Time (minutes)')
    ax.set_ylabel('Power (W)')
    ax2 = ax.twinx()
    clim = pyplot.get(ax,'ylim')
    ax2.set_ylim(clim[0]*1000/120,clim[1]*1000/120)
    ax2.set_ylabel('Current (mA)')
    # generate a PNG file
    if pngfilename:
        pyplot.savefig(pngfilename)
    # show the plot
    pyplot.show()

    # cumulative plot
    pyplot.plot(t/60,np.cumsum(w)/1000)
    ax = pyplot.gca()
    ax.set_xlabel('Time (minutes)')
    ax.set_ylabel('Energy (kJ)')
    ax2 = ax.twinx()
    clim = pyplot.get(ax,'ylim')
    ax2.set_ylim(clim[0]/3.6,clim[1]/3.6)
    ax2.set_ylabel('Energy (Wh)')
    if pngfilename:
        pyplot.savefig('energy.png')
    # show the plot
    pyplot.show()
    
    # open interactive shell
    #ipshell()

if __name__ == '__main__':
    main()
