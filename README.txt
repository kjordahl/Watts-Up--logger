                                README
                                ======

Author: Kelsey Jordahl <kjordahl@pequin.local>
Date: 2012-01-23 10:22:38 EST


Table of Contents
=================
1 INTRODUCTION 
2 USAGE 
3 FILES 
4 TO DO 
5 LICENSE 


1 INTRODUCTION 
~~~~~~~~~~~~~~~

This is a simple Python utility for logging data from a [Watts Up? Pro]
power meter.  Documentation for the serial port interface for the
meter is available in [this PDF file].

Other software capable of logging data on the Watts Up? meter are
available for [download from watts up?], and they sell a [realtime version for Windows] for $72.95. One example I found of reading from the Watts
Up? Pro in Python was [this script].

The program will by default assume the most common device name for
Linux and OS X platforms, but the serial port device can also be
specified with the command line option `-p'.

The Watts Up? Pro uses an FTDI serial to USB adapter internally.  If
the driver is not already installed on your operating system, download
the latest driver from the [FTDI website].


[Watts Up? Pro]: https://www.wattsupmeters.com/secure/products.php?pn=0&wai=384&more=4
[this PDF file]: https://www.wattsupmeters.com/secure/downloads/CommunicationsProtocol090824.pdf
[download from watts up?]: https://www.wattsupmeters.com/secure/support.php
[realtime version for Windows]: https://orders.wattsupmeters.com/store/home.php?cat=26
[this script]: http://www.wattzon.com/forums/posts/80
[FTDI website]: http://www.ftdichip.com/Drivers/VCP.htm

2 USAGE 
~~~~~~~~

Basic usage from the command line:

To log realtime data at the default sample rate (1 s) to the file
`sample.log', use
wattsup.py -l -o sample.log

A basic realtime plot can be added to the above with
wattsup.py -l -g -o sample.log
(requires numpy and matplotlib).

Full description of options will be given by
wattsup -h

3 FILES 
~~~~~~~~

`wattsup.py': Program to log, display data to console, and
                  generate a simple real time plot
`plot.py': Simple plotting program for files already logged.
`wattui.py': Experimental [TraitsUI] interface to power meter
                 logging (only does simulated logging for now)

In the `samples' subdirectory, there are several raw data logs that
can be used as sample input with the `--simulation-mode' option.  Note
that they may not be interesting to watch in real time.  These files
log the data as it comes from the serial port, with the `--raw' option.
`ac.raw': Sample data from a small window air conditioner
`fan.raw': Sample data from a two-motor, 3-speed fan
`iphone3gs.raw': Charging an iPhone 3gs
`iphone4.raw': Charging an iPhone 4


[TraitsUI]: http://code.enthought.com/projects/traits_ui/

4 TO DO 
~~~~~~~~

- Fetching data from internal storage is not yet working
- Plotting is currently very rudimentary.  Some things to add include:
  - Better autoranging
  - Options for plotting power, current, or both
  - Cumulative display or plot of energy used

5 LICENSE 
~~~~~~~~~~

These programs are free software: you can redistribute them and/or
modify them under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.  A copy of the GPL
version 3 license can be found in the file COPYING or at
[http://www.gnu.org/licenses].

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
