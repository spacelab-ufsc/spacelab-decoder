# -*- coding: utf-8 -*-

#
#  spacelab_decoder.py
#  
#  Copyright (C) 2020, Universidade Federal de Santa Catarina
#  
#  This file is part of SpaceLab-Decoder.
#
#  SpaceLab-Decoder is free software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  SpaceLab-Decoder is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public
#  License along with SpaceLab-Decoder; if not, see <http://www.gnu.org/licenses/>.
#  
#

__author__      = "Gabriel Mariano Marcelino - PU5GMA"
__copyright__   = "Copyright (C) 2020, Universidade Federal de Santa Catarina"
__credits__     = ["Gabriel Mariano Marcelino - PU5GMA"]
__license__     = "GPL3"
__version__     = "0.2.1"
__maintainer__  = "Gabriel Mariano Marcelino - PU5GMA"
__email__       = "gabriel.mm8@gmail.com"
__status__      = "Development"


import os
import threading
import sys
import signal
from datetime import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from scipy.io import wavfile
import zmq

from mm_decoder import mm_decoder
import _version

_UI_FILE_LOCAL              = 'gui/spacelab_decoder.glade'
_UI_FILE_LINUX_SYSTEM       = '/usr/share/spacelab-decoder/gui/spacelab_decoder.glade'

_ICON_FILE_LOCAL            = 'icon/spacelab_decoder_256x256.png'
_ICON_FILE_LINUX_SYSTEM     = '/usr/share/icons/spacelab_decoder_256x256.png'

_DIR_CONFIG_LINUX           = '.spacelab-decoder'
_DIR_CONFIG_WINDOWS         = 'spacelab-decoder'

_DEFAULT_CALLSIGN           = 'PP5UF'
_DEFAULT_LOCATION           = 'Florianópolis'
_DEFAULT_COUNTRY            = 'Brazil'
_DEFAULT_BEACON_BAUDRATE    = 1200
_DEFAULT_DOWNLINK_BAUDRATE  = 2400
_DEFAULT_BEACON_SYNC_WORD   = '0x7E2AE65D'
_DEFAULT_DOWNLINK_SYNC_WORD = '0x7E2AE65D'


class SpaceLabDecoder:

    def __init__(self):
        self.builder = Gtk.Builder()

        # UI file from Glade
        if os.path.isfile(_UI_FILE_LOCAL):
            self.builder.add_from_file(_UI_FILE_LOCAL)
        else:
            self.builder.add_from_file(_UI_FILE_LINUX_SYSTEM)

        self.builder.connect_signals(self)

        self._build_widgets()

        self._load_preferences()

    def _build_widgets(self):
        # Main window
        self.window = self.builder.get_object("window_main")
        if os.path.isfile(_ICON_FILE_LOCAL):
            self.window.set_icon_from_file(_ICON_FILE_LOCAL)
        else:
            self.window.set_icon_from_file(_ICON_FILE_LINUX_SYSTEM)
        self.window.connect("destroy", Gtk.main_quit)

        # Preferences dialog
        self.dialog_preferences = self.builder.get_object("dialog_preferences")
        self.button_preferences_ok = self.builder.get_object("button_preferences_ok")
        self.button_preferences_ok.connect("clicked", self.on_button_preferences_ok_clicked)
        self.button_preferences_default = self.builder.get_object("button_preferences_default")
        self.button_preferences_default.connect("clicked", self.on_button_preferences_default_clicked)
        self.button_preferences_cancel = self.builder.get_object("button_preferences_cancel")
        self.button_preferences_cancel.connect("clicked", self.on_button_preferences_cancel_clicked)

        self.entry_preferences_general_callsign = self.builder.get_object("entry_preferences_general_callsign")
        self.entry_preferences_general_location = self.builder.get_object("entry_preferences_general_location")
        self.entry_preferences_general_country = self.builder.get_object("entry_preferences_general_country")

        self.entry_preferences_beacon_baudrate = self.builder.get_object("entry_preferences_beacon_baudrate")
        self.entry_preferences_beacon_s0 = self.builder.get_object("entry_preferences_beacon_s0")
        self.entry_preferences_beacon_s1 = self.builder.get_object("entry_preferences_beacon_s1")
        self.entry_preferences_beacon_s2 = self.builder.get_object("entry_preferences_beacon_s2")
        self.entry_preferences_beacon_s3 = self.builder.get_object("entry_preferences_beacon_s3")

        self.entry_preferences_downlink_baudrate = self.builder.get_object("entry_preferences_downlink_baudrate")
        self.entry_preferences_downlink_s0 = self.builder.get_object("entry_preferences_downlink_s0")
        self.entry_preferences_downlink_s1 = self.builder.get_object("entry_preferences_downlink_s1")
        self.entry_preferences_downlink_s2 = self.builder.get_object("entry_preferences_downlink_s2")
        self.entry_preferences_downlink_s3 = self.builder.get_object("entry_preferences_downlink_s3")

        # About dialog
        self.aboutdialog = self.builder.get_object("aboutdialog_spacelab_decoder")
        self.aboutdialog.set_version(_version.__version__)

        # Preferences button
        self.button_preferences = self.builder.get_object("button_preferences")
        self.button_preferences.connect("clicked", self.on_button_preferences_clicked)

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

    def on_button_preferences_clicked(self, button):
        response = self.dialog_preferences.run()

        if response == Gtk.ResponseType.DELETE_EVENT:
            self._load_preferences()
            self.dialog_preferences.hide()

    def on_button_preferences_ok_clicked(self, button):
        self._save_preferences()
        self.dialog_preferences.hide()

    def on_button_preferences_default_clicked(self, button):
        self._load_default_preferences()

    def on_button_preferences_cancel_clicked(self, button):
        self._load_preferences()
        self.dialog_preferences.hide()

    def on_button_decode_clicked(self, button):
        if self.filechooser_audio_file.get_filename() is None:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error loading the audio file!")
            error_dialog.format_secondary_text("No file selected!")
            error_dialog.run()
            error_dialog.destroy()
        else:
            sample_rate, data = wavfile.read(self.filechooser_audio_file.get_filename())
            self.listmodel_events.append([str(datetime.now()), "Audio file opened with a sample rate of " + str(sample_rate) + " Hz"])

            x = threading.Thread(target=self._decode_audio, args=(self.filechooser_audio_file.get_filename(),sample_rate,))
            z = threading.Thread(target=self._zmq_receiver)
            x.start()
            z.start()

    def on_events_selection_changed(self, widget):
        (model, iter) = self.selection_events.get_selected()
        if iter is not None:
            print(model[iter][0])

        return True

    def on_toolbutton_about_clicked(self, toolbutton):
        response = self.aboutdialog.run()

        if response == Gtk.ResponseType.DELETE_EVENT:
            self.aboutdialog.hide()

    def _save_preferences(self):
        home = os.path.expanduser('~')
        location = os.path.join(home, _DIR_CONFIG_LINUX)

        if not os.path.exists(location):
            os.mkdir(location)

    def _load_preferences(self):
        home = os.path.expanduser('~')
        location = os.path.join(home, _DIR_CONFIG_LINUX)

    def _load_default_preferences(self):
        self.entry_preferences_general_callsign.set_text(_DEFAULT_CALLSIGN)
        self.entry_preferences_general_location.set_text(_DEFAULT_LOCATION)
        self.entry_preferences_general_country.set_text(_DEFAULT_COUNTRY)

        self.entry_preferences_beacon_baudrate.set_text(str(_DEFAULT_BEACON_BAUDRATE))
        self.entry_preferences_beacon_s0.set_text('0x' + _DEFAULT_BEACON_SYNC_WORD[2:4])
        self.entry_preferences_beacon_s1.set_text('0x' + _DEFAULT_BEACON_SYNC_WORD[4:6])
        self.entry_preferences_beacon_s2.set_text('0x' + _DEFAULT_BEACON_SYNC_WORD[6:8])
        self.entry_preferences_beacon_s3.set_text('0x' + _DEFAULT_BEACON_SYNC_WORD[8:10])

        self.entry_preferences_downlink_baudrate.set_text(str(_DEFAULT_DOWNLINK_BAUDRATE))
        self.entry_preferences_downlink_s0.set_text('0x' + _DEFAULT_DOWNLINK_SYNC_WORD[2:4])
        self.entry_preferences_downlink_s1.set_text('0x' + _DEFAULT_DOWNLINK_SYNC_WORD[4:6])
        self.entry_preferences_downlink_s2.set_text('0x' + _DEFAULT_DOWNLINK_SYNC_WORD[6:8])
        self.entry_preferences_downlink_s3.set_text('0x' + _DEFAULT_DOWNLINK_SYNC_WORD[8:10])

    def _decode_audio(self, audio_file, sample_rate):
        tb = mm_decoder(baudrate=1200, samp_rate=sample_rate, input_file=audio_file, play_audio=True)

        tb.start()
        tb.wait()

    def _zmq_receiver(self):
        context = zmq.Context()
        bits_receiver = context.socket(zmq.PULL)
        bits_receiver.connect("tcp://127.0.0.1:8023")

        poller = zmq.Poller()
        poller.register(bits_receiver, zmq.POLLIN)

        while True:
            socks = dict(poller.poll(1000))
            if socks:
                if socks.get(bits_receiver) == zmq.POLLIN:
                    bits = bits_receiver.recv(zmq.NOBLOCK)
            else:
                break
