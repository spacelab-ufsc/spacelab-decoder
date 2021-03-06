# -*- coding: utf-8 -*-

#
#  spacelab_decoder.py
#  
#  Copyright (C) 2021, Universidade Federal de Santa Catarina
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


import os
import threading
import sys
import signal
from datetime import datetime
import ctypes
import pathlib

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GdkPixbuf

from scipy.io import wavfile
import zmq

from spacelab_decoder.mm_decoder import mm_decoder
import spacelab_decoder.version

from spacelab_decoder.bit_buffer import BitBuffer, _BIT_BUFFER_LSB
from spacelab_decoder.sync_word import SyncWord, _SYNC_WORD_LSB
from spacelab_decoder.byte_buffer import ByteBuffer, _BYTE_BUFFER_LSB
from spacelab_decoder.packet import Packet

_UI_FILE_LOCAL                  = os.path.abspath(os.path.dirname(__file__)) + '/data/ui/spacelab_decoder.glade'
_UI_FILE_LINUX_SYSTEM           = '/usr/share/spacelab_decoder/spacelab_decoder.glade'

_ICON_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/spacelab_decoder_256x256.png'
_ICON_FILE_LINUX_SYSTEM         = '/usr/share/icons/spacelab_decoder_256x256.png'

_LOGO_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/spacelab-logo-full-400x200.png'
_LOGO_FILE_LINUX_SYSTEM         = '/usr/share/spacelab_decoder/spacelab-logo-full-400x200.png'

_NGHAM_LIB_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/libngham.so'
_NGHAM_LIB_LINUX_SYSTEM         = '/usr/lib/libngham.so'
_NGHAM_LIB_LINUX_64_SYSTEM      = '/usr/lib64/libngham.so'

_NGHAM_FSAT_LIB_LOCAL           = os.path.abspath(os.path.dirname(__file__)) + '/libngham_fsat.so'
_NGHAM_FSAT_LIB_LINUX_SYSTEM    = '/usr/lib/libngham_fsat.so'
_NGHAM_FSAT_LIB_LINUX_64_SYSTEM = '/usr/lib64/libngham_fsat.so'

_DIR_CONFIG_LINUX               = '.spacelab_decoder'
_DIR_CONFIG_WINDOWS             = 'spacelab_decoder'

_SAT_JSON_FLORIPASAT_I_LOCAL    = os.path.abspath(os.path.dirname(__file__)) + '/data/satellites/floripasat-i.json'
_SAT_JSON_FLORIPASAT_I_SYSTEM   = '/usr/share/spacelab_decoder/floripasat-i.json'
_SAT_JSON_GOLDS_UFSC_LOCAL      = os.path.abspath(os.path.dirname(__file__)) + '/data/satellites/golds-ufsc.json'
_SAT_JSON_GOLDS_UFSC_SYSTEM     = '/usr/share/spacelab_decoder/golds-ufsc.json'

_DEFAULT_CALLSIGN               = 'PP5UF'
_DEFAULT_LOCATION               = 'Florianópolis'
_DEFAULT_COUNTRY                = 'Brazil'
_DEFAULT_BEACON_BAUDRATE        = 1200
_DEFAULT_DOWNLINK_BAUDRATE      = 2400
_DEFAULT_BEACON_SYNC_WORD       = '0x7E2AE65D'
_DEFAULT_DOWNLINK_SYNC_WORD     = '0x7E2AE65D'
_DEFAULT_MAX_PKT_LEN_BYTES      = 300

_ZMQ_PUSH_PULL_ADDRESS          = "tcp://127.0.0.1:8023"

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

        if os.path.isfile(_NGHAM_LIB_LOCAL):
            self.ngham = ctypes.CDLL(_NGHAM_LIB_LOCAL)
        elif os.path.isfile(_NGHAM_LIB_LINUX_64_SYSTEM):
            self.ngham = ctypes.CDLL(_NGHAM_LIB_LINUX_64_SYSTEM)
        else:
            self.ngham = ctypes.CDLL(_NGHAM_LIB_LINUX_SYSTEM)

        self.ngham.ngham_init_arrays()

        self.ngham.ngham_init()

        if os.path.isfile(_NGHAM_FSAT_LIB_LOCAL):
            self.ngham_fsat = ctypes.CDLL(_NGHAM_FSAT_LIB_LOCAL)
        elif os.path.isfile(_NGHAM_FSAT_LIB_LINUX_64_SYSTEM):
            self.ngham_fsat = ctypes.CDLL(_NGHAM_FSAT_LIB_LINUX_64_SYSTEM)
        else:
            self.ngham_fsat = ctypes.CDLL(_NGHAM_FSAT_LIB_LINUX_SYSTEM)

        self.ngham_fsat.ngham_init_arrays()

        self.ngham_fsat.ngham_init()

    def _build_widgets(self):
        # Main window
        self.window = self.builder.get_object("window_main")
        if os.path.isfile(_ICON_FILE_LOCAL):
            self.window.set_icon_from_file(_ICON_FILE_LOCAL)
        else:
            self.window.set_icon_from_file(_ICON_FILE_LINUX_SYSTEM)
        self.window.set_wmclass(self.window.get_title(), self.window.get_title())
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
        self.aboutdialog.set_version(spacelab_decoder.version.__version__)
        if os.path.isfile(_LOGO_FILE_LOCAL):
            self.aboutdialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(_LOGO_FILE_LOCAL))
        else:
            self.aboutdialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(_LOGO_FILE_LINUX_SYSTEM))

        # Preferences button
        self.button_preferences = self.builder.get_object("button_preferences")
        self.button_preferences.connect("clicked", self.on_button_preferences_clicked)

        # Satellite combobox
        self.liststore_satellite = self.builder.get_object("liststore_satellite")
        self.liststore_satellite.append(["FloripaSat-I"])
        self.liststore_satellite.append(["GOLDS-UFSC"])
        self.combobox_satellite = self.builder.get_object("combobox_satellite")
        cell = Gtk.CellRendererText()
        self.combobox_satellite.pack_start(cell, True)
        self.combobox_satellite.add_attribute(cell, "text", 0)

        # Packet type combobox
        self.combobox_packet_type = self.builder.get_object("combobox_packet_type")

        # Audio file Filechooser
        self.filechooser_audio_file = self.builder.get_object("filechooser_audio_file")

        # Play audio checkbutton
        self.checkbutton_play_audio = self.builder.get_object("checkbutton_play_audio")

        # Decode button
        self.button_decode = self.builder.get_object("button_decode")
        self.button_decode.connect("clicked", self.on_button_decode_clicked)

        # Clears button
        self.button_clear = self.builder.get_object("button_clean")
        self.button_clear.connect("clicked", self.on_button_clear_clicked)

        # About toolbutton
        self.toolbutton_about = self.builder.get_object("toolbutton_about")
        self.toolbutton_about.connect("clicked", self.on_toolbutton_about_clicked)

        # Packet data textview
        self.textbuffer_pkt_data = Gtk.TextBuffer()
        self.textview_pkt_data = self.builder.get_object("textview_pkt_data")
        self.textview_pkt_data.set_buffer(self.textbuffer_pkt_data)

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
            if self.combobox_satellite.get_active() == -1:
                error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error decoding the audio file!")
                error_dialog.format_secondary_text("No satellite selected!")
                error_dialog.run()
                error_dialog.destroy()
            else:
                sample_rate, data = wavfile.read(self.filechooser_audio_file.get_filename())
                self.listmodel_events.append([str(datetime.now()), "Audio file opened with a sample rate of " + str(sample_rate) + " Hz"])

                x = threading.Thread(target=self._decode_audio, args=(self.filechooser_audio_file.get_filename(), sample_rate, 1200, self.checkbutton_play_audio.get_active()))
                z = threading.Thread(target=self._zmq_receiver)
                x.start()
                z.start()

    def on_events_selection_changed(self, widget):
        (model, iter) = self.selection_events.get_selected()
        if iter is not None:
            print(model[iter][0])

        return True

    def on_button_clear_clicked(self, button):
        self.textbuffer_pkt_data.set_text("")

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

    def _decode_audio(self, audio_file, sample_rate, baud, play):
        tb = mm_decoder(input_file=audio_file, samp_rate=sample_rate, baudrate=baud, zmq_adr=_ZMQ_PUSH_PULL_ADDRESS, play_audio=play)

        tb.start()
        tb.wait()

    def _zmq_receiver(self):
        context = zmq.Context()
        bits_receiver = context.socket(zmq.PULL)
        bits_receiver.connect(_ZMQ_PUSH_PULL_ADDRESS)

        poller = zmq.Poller()
        poller.register(bits_receiver, zmq.POLLIN)

        sync_word_buf = BitBuffer(32, _BIT_BUFFER_LSB)

        sync_word_str = list()

        if self.combobox_packet_type.get_active() == 0:
            sync_word_str = [int(self.entry_preferences_beacon_s0.get_text(), 0),
                             int(self.entry_preferences_beacon_s1.get_text(), 0),
                             int(self.entry_preferences_beacon_s2.get_text(), 0),
                             int(self.entry_preferences_beacon_s3.get_text(), 0)]
        elif self.combobox_packet_type.get_active() == 1:
            sync_word_str = [int(self.entry_preferences_downlink_s0.get_text(), 0),
                             int(self.entry_preferences_downlink_s1.get_text(), 0),
                             int(self.entry_preferences_downlink_s2.get_text(), 0),
                             int(self.entry_preferences_downlink_s3.get_text(), 0)]
        else:
            sync_word_str = [0, 1, 2, 3]

        sync_word = SyncWord(sync_word_str, _SYNC_WORD_LSB)

        byte_buf = ByteBuffer(_BYTE_BUFFER_LSB)

        packet_detected = False
        packet_buf = list()

        ngham_decode_func = self.ngham.ngham_decode
        ngham_decode_func.argtypes = [ctypes.c_ubyte, ctypes.POINTER(ctypes.c_ubyte)]
        ngham_decode_func.restype = ctypes.c_int

        if self.combobox_satellite.get_active() == 0:
            ngham_decode_func = self.ngham_fsat.ngham_decode
            ngham_decode_func.argtypes = [ctypes.c_ubyte, ctypes.POINTER(ctypes.c_ubyte)]
            ngham_decode_func.restype = ctypes.c_int
        elif self.combobox_satellite.get_active() == 1:
            ngham_decode_func = self.ngham.ngham_decode
            ngham_decode_func.argtypes = [ctypes.c_ubyte, ctypes.POINTER(ctypes.c_ubyte)]
            ngham_decode_func.restype = ctypes.c_int

        while True:
            socks = dict(poller.poll(1000))
            if socks:
                if socks.get(bits_receiver) == zmq.POLLIN:
                    bits = bits_receiver.recv(zmq.NOBLOCK)

                    for bit in bits:
                        if packet_detected:
                            byte_buf.push(bool(bit))
                            if byte_buf.is_full():
                                if len(packet_buf) < _DEFAULT_MAX_PKT_LEN_BYTES:
                                    pkt_byte = byte_buf.to_byte()
                                    packet_buf.append(pkt_byte)

                                    ArrayType = ctypes.c_ubyte * _DEFAULT_MAX_PKT_LEN_BYTES # Dynamically declare the array type
                                    array = ArrayType()                                     # The array type instance

                                    res = ngham_decode_func(pkt_byte, ctypes.cast(array, ctypes.POINTER(ctypes.c_ubyte)))
                                    if res == -1:
                                        packet_detected = False
                                        if self.combobox_packet_type.get_active() == 0:
                                            self.listmodel_events.append([str(datetime.now()), "Error decoding a Beacon packet!"])
                                        elif self.combobox_packet_type.get_active() == 1:
                                            self.listmodel_events.append([str(datetime.now()), "Error decoding a Downlink packet!"])
                                        else:
                                            self.listmodel_events.append([str(datetime.now()), "Error decoding a Packet!"])
                                    elif res > 0:
                                        packet_detected = False
                                        if self.combobox_packet_type.get_active() == 0:
                                            self.listmodel_events.append([str(datetime.now()), "Beacon packet decoded!"])
                                        elif self.combobox_packet_type.get_active() == 1:
                                            self.listmodel_events.append([str(datetime.now()), "Downlink packet decoded!"])
                                        else:
                                            self.listmodel_events.append([str(datetime.now()), "Packet decoded!"])

                                        pkt_list = list()
                                        for i in range(res):
                                            pkt_list.append(int(array[i]))
                                        self._decode_packet(pkt_list)
                                    byte_buf.clear()
                        sync_word_buf.push(bool(bit))
                        if (sync_word_buf == sync_word):
                            packet_buf = []
                            packet_detected = True
                            byte_buf.clear()

            else:
                break

    def _decode_packet(self, pkt):
        pkt_txt = "Decoded packet from \"" + self.filechooser_audio_file.get_filename() + "\":\n"
        sat_json = str()
        if self.combobox_satellite.get_active() == 0:
            if os.path.isfile(_SAT_JSON_FLORIPASAT_I_LOCAL):
                sat_json = _SAT_JSON_FLORIPASAT_I_LOCAL
            else:
                sat_json = _SAT_JSON_FLORIPASAT_I_SYSTEM
        elif self.combobox_satellite.get_active() == 1:
            if os.path.isfile(_SAT_JSON_GOLDS_UFSC_LOCAL):
                sat_json = _SAT_JSON_GOLDS_UFSC_LOCAL
            else:
                sat_json = _SAT_JSON_GOLDS_UFSC_SYSTEM
        p = Packet(sat_json, pkt)
        pkt_txt = pkt_txt + str(p)
        pkt_txt = pkt_txt + "========================================================\n"
        self.textbuffer_pkt_data.insert(self.textbuffer_pkt_data.get_end_iter(), pkt_txt)
