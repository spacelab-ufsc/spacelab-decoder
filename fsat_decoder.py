#
#  fsat_decoder.py
#  
#  Copyright (C) 2019, Universidade Federal de Santa Catarina
#  
#  This file is part of FloripaSat-Decoder.
#
#  FloripaSat-Decoder is free software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  FloripaSat-Decoder is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public
#  License along with FloripaSat-Decoder; if not, see <http://www.gnu.org/licenses/>.
#  
#

__author__      = "Gabriel Mariano Marcelino - PU5GMA"
__copyright__   = "Copyright (C) 2019, Universidade Federal de Santa Catarina"
__credits__     = ["Gabriel Mariano Marcelino - PU5GMA"]
__license__     = "GPL3"
__version__     = "0.1.1"
__maintainer__  = "Gabriel Mariano Marcelino - PU5GMA"
__email__       = "gabriel.marcelino@gmail.com"
__status__      = "Development"


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import os
from scipy.io import wavfile
from datetime import datetime

import _version

_UI_FILE_LOCAL          = 'gui/fsat_decoder.glade'
_UI_FILE_LINUX_SYSTEM   = '/usr/share/fsat-decoder/gui/fsat_decoder.glade'

_ICON_FILE_LOCAL        = 'icon/fsat_decoder_256x256.png'
_ICON_FILE_LINUX_SYSTEM = '/usr/share/icons/fsat_decoder_256x256.png'

class FSatDecoder:

    def __init__(self):
        self.builder = Gtk.Builder()

        # UI file from Glade
        if os.path.isfile(_UI_FILE_LOCAL):
            self.builder.add_from_file(_UI_FILE_LOCAL)
        else:
            self.builder.add_from_file(_UI_FILE_LINUX_SYSTEM)

        self.builder.connect_signals(self)

        self._build_widgets()

    def _build_widgets(self):
        # Main window
        self.window = self.builder.get_object("window_main")
        if os.path.isfile(_ICON_FILE_LOCAL):
            self.window.set_icon_from_file(_ICON_FILE_LOCAL)
        else:
            self.window.set_icon_from_file(_ICON_FILE_LINUX_SYSTEM)
        self.window.connect("destroy", Gtk.main_quit)

        # About dialog
        self.aboutdialog = self.builder.get_object("aboutdialog_fsat_decoder")
        self.aboutdialog.set_version(_version.__version__)

        # Preferences button
        self.button_preferences = self.builder.get_object("button_preferences")

        # Packet type combobox
        self.combobox_packet_type = self.builder.get_object("combobox_packet_type")

        # Audio file Filechooser
        self.filechooser_audio_file = self.builder.get_object("filechooser_audio_file")

        # Sample rate entry
        self.entry_sample_rate = self.builder.get_object("entry_sample_rate")

        # Decode button
        self.button_decode = self.builder.get_object("button_decode")
        self.button_decode.connect("clicked", self.on_button_decode_clicked)

        # Clears button
        self.button_clear = self.builder.get_object("button_clean")

        # About toolbutton
        self.toolbutton_about = self.builder.get_object("toolbutton_about")
        self.toolbutton_about.connect("clicked", self.on_toolbutton_about_clicked)

        # Events treeview
        self.treeview_events = self.builder.get_object("treeview_events")
        self.listmodel_events = Gtk.ListStore(str, str)
        self.treeview_events.set_model(self.listmodel_events)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Datetime", cell, text=0)
        column.set_fixed_width(250)
        self.treeview_events.append_column(column)
        column = Gtk.TreeViewColumn("Event", cell, text=1)
        self.treeview_events.append_column(column)
        self.selection_events = self.treeview_events.get_selection()
        self.selection_events.connect("changed", self.on_events_selection_changed)

    def run(self):
        self.window.show_all()

        Gtk.main()

    def destroy(window, self):
        Gtk.main_quit()

    def on_button_decode_clicked(self, button):
        if self.filechooser_audio_file.get_filename() is None:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error loading the audio file!")
            error_dialog.format_secondary_text("No file selected!")
            error_dialog.run()
            error_dialog.destroy()
        else:
            sample_rate, data = wavfile.read(self.filechooser_audio_file.get_filename())
            self.listmodel_events.append([str(datetime.now()), "Audio file opened with a sample rate of " + str(sample_rate) + " Hz"])

    def on_events_selection_changed(self, widget):
        (model, iter) = self.selection_events.get_selected()
        if iter is not None:
            print(model[iter][0])

        return True

    def on_toolbutton_about_clicked(self, toolbutton):
        response = self.aboutdialog.run()

        if response == Gtk.ResponseType.DELETE_EVENT:
            self.aboutdialog.hide()
