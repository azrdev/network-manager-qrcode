#!/usr/bin/env python
#    Copyright 2015 Tobias Mueller <tobiasmue@gnome.org>
#
#    This file is part of NetworkManager Barcode.
#
#    NetworkManager Barcode is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    NetworkManager Barcode is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with NetworkManager Barcode.  If not, see <http://www.gnu.org/licenses/>.

import logging

from scan_barcode import BarcodeReaderGTK
from parse_barcode import parse

from gi.repository import GLib, Gtk
from gi.repository import Gst

class Scanner(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(*args, **kwargs)
        self.connect("activate", self.on_activate)


    def on_activate(self, data=None):
        window = Gtk.ApplicationWindow(type=Gtk.WindowType.TOPLEVEL)
        window.set_title("WiFi QRCode scanner")
        scanner = BarcodeReaderGTK()
        scanner.connect("barcode", self.on_barcode)
        window.add(scanner)

        window.show_all()
        self.add_window(window)

    def on_barcode(self, reader, barcode, message):
        logging.debug('Received barcode! %s', barcode)
        parsed = parse(barcode)
        logging.info('Parsed %s into %s', barcode, parsed)
        
        

def main():
    Gst.init()
    app = Scanner()
    app.run(None)

if __name__ == '__main__':
    main()
