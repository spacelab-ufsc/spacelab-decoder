# -*- coding: utf-8 -*-

#
#  spacelab_decoder.py
#  
#  Copyright The SpaceLab-Decoder Contributors.
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
from datetime import datetime
import json
import threading
import socket

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np

import zmq

import pyngham

import spacelab_decoder.version

from spacelab_decoder.time_sync import TimeSync
from spacelab_decoder.bit_buffer import BitBuffer, _BIT_BUFFER_LSB
from spacelab_decoder.sync_word import SyncWord, _SYNC_WORD_LSB
from spacelab_decoder.byte_buffer import ByteBuffer, _BYTE_BUFFER_LSB
from spacelab_decoder.bit_decoder import BitDecoder
from spacelab_decoder.packet import PacketSLP, PacketCSP
from spacelab_decoder.ax100 import AX100Mode5
from spacelab_decoder.satellite import Satellite
from spacelab_decoder.log import Log

_UI_FILE_LOCAL                  = os.path.abspath(os.path.dirname(__file__)) + '/data/ui/spacelab_decoder.glade'
_UI_FILE_LINUX_SYSTEM           = '/usr/share/spacelab_decoder/spacelab_decoder.glade'

_ICON_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/spacelab_decoder_256x256.png'
_ICON_FILE_LINUX_SYSTEM         = '/usr/share/icons/spacelab_decoder_256x256.png'

_LOGO_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/spacelab-logo-full-400x200.png'
_LOGO_FILE_LINUX_SYSTEM         = '/usr/share/spacelab_decoder/spacelab-logo-full-400x200.png'

_DIR_CONFIG_LINUX               = '.config/spacelab_decoder'
_DIR_CONFIG_WINDOWS             = 'spacelab_decoder'

_SAT_JSON_LOCAL_PATH            = os.path.abspath(os.path.dirname(__file__)) + '/data/satellites/'
_SAT_JSON_SYSTEM_PATH           = '/usr/share/spacelab_decoder/'

_DEFAULT_CALLSIGN               = 'PP5UF'
_DEFAULT_LOCATION               = 'Florianópolis'
_DEFAULT_COUNTRY                = 'Brazil'
_DEFAULT_SYNC_WORD_BIT_ERROR    = 4
_DEFAULT_AX100_USE_LEN_ERR      = False
_DEFAULT_INPUT_SOCKET_TYPE_TCP  = True
_DEFAULT_INPUT_SOCKET_LINK_EN   = True

_DIR_CONFIG_DEFAULTJSON         = 'spacelab_decoder.json'

# Defining logfile default local
_DIR_CONFIG_LOGFILE_LINUX       = 'spacelab_decoder'
_DEFAULT_LOGFILE_PATH           = os.path.join(os.path.expanduser('~'), _DIR_CONFIG_LOGFILE_LINUX)
_DEFAULT_LOGFILE                = 'logfile.csv'

_SATELLITES                     = [["FloripaSat-1", "floripasat-1.json"],
                                   ["FloripaSat-2A", "floripasat-2a.json"],
                                   ["GOLDS-UFSC", "golds-ufsc.json"],
                                   ["Catarina-A1", "catarina-a1.json"],
                                   ["Catarina-A2", "catarina-a2.json"],
                                   ["Catarina-A3", "catarina-a3.json"],
                                   ["SpaceLab-Transmitter", "spacelab-transmitter.json"]]

_PROTOCOL_NGHAM                 = "NGHam"
_PROTOCOL_AX100MODE5            = "AX100-Mode5"

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

        self._tcp_server_socket = None

        self.decoded_packets_index = list()

        self._run_udp_decode = False

        self._client_socket = None
        self._tcp_new_conn_cb_id = None
        self._tcp_client_cb_id = None

        self._zmq_ctx = zmq.Context()
        self._zmq_sub = None
        self._zmq_new_conn_cb_id = None

        self._satellite = Satellite()

        self._log = Log(_DEFAULT_LOGFILE, _DEFAULT_LOGFILE_PATH)

        self._packet_csp_buf = PacketCSP()

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

        self.entry_preferences_max_bit_err = self.builder.get_object("entry_preferences_max_bit_err")

        self.checkbutton_preferences_protocols_ax100_len = self.builder.get_object("checkbutton_preferences_protocols_ax100_len")

        self.radiobutton_preferences_conn_tcp = self.builder.get_object("radiobutton_preferences_conn_tcp")
        self.radiobutton_preferences_conn_zmq = self.builder.get_object("radiobutton_preferences_conn_zmq")

        self.switch_preferences_conn_link_layer = self.builder.get_object("switch_preferences_conn_link_layer")

        self.entry_preferences_udp_address = self.builder.get_object("entry_preferences_udp_address")
        self.entry_preferences_udp_port = self.builder.get_object("entry_preferences_udp_port")
        self.switch_raw_bits = self.builder.get_object("switch_raw_bits")

        # About dialog
        self.aboutdialog = self.builder.get_object("aboutdialog_spacelab_decoder")
        self.aboutdialog.set_version(spacelab_decoder.version.__version__)
        if os.path.isfile(_LOGO_FILE_LOCAL):
            self.aboutdialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(_LOGO_FILE_LOCAL))
        else:
            self.aboutdialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(_LOGO_FILE_LINUX_SYSTEM))

        # Logfile chooser button
        self.logfile_chooser_button = self.builder.get_object("logfile_chooser_button")
        self.logfile_chooser_button.set_filename(_DEFAULT_LOGFILE_PATH)

        # Preferences button
        self.button_preferences = self.builder.get_object("button_preferences")
        self.button_preferences.connect("clicked", self.on_button_preferences_clicked)

        # Satellite combobox
        self.liststore_satellite = self.builder.get_object("liststore_satellite")
        for sat in _SATELLITES:
            self.liststore_satellite.append([sat[0]])
        self.combobox_satellite = self.builder.get_object("combobox_satellite")
        cell = Gtk.CellRendererText()
        self.combobox_satellite.pack_start(cell, True)
        self.combobox_satellite.add_attribute(cell, "text", 0)
        self.combobox_satellite.connect("changed", self.on_combobox_satellite_changed)

        # Packet type combobox
        self.liststore_link = self.builder.get_object("liststore_link")
        self.combobox_link = self.builder.get_object("combobox_link")
        self.combobox_link.pack_start(cell, True)
        self.combobox_link.add_attribute(cell, "text", 0)
        self.combobox_link.connect("changed", self.on_combobox_link_changed)

        # Signal source
        self.radiobutton_audio_file = self.builder.get_object("radiobutton_audio_file")
        self.radiobutton_udp        = self.builder.get_object("radiobutton_udp")
        self.filechooser_audio_file = self.builder.get_object("filechooser_audio_file")

        # Data output
        self.entry_output_address           = self.builder.get_object("entry_output_address")
        self.entry_output_port              = self.builder.get_object("entry_output_port")
        self.button_output_connect          = self.builder.get_object("button_output_connect")
        self.button_output_connect.connect("clicked", self.on_button_output_connect_clicked)
        self.button_output_disconnect       = self.builder.get_object("button_output_disconnect")
        self.button_output_disconnect.connect("clicked", self.on_button_output_disconnect_clicked)

        # Decode button
        self.button_decode = self.builder.get_object("button_decode")
        self.button_decode.connect("clicked", self.on_button_decode_clicked)

        # Stop button
        self.button_stop = self.builder.get_object("button_stop")
        self.button_stop.connect("clicked", self.on_button_stop_clicked)

        # Plot spectrum button
        self.button_plot_spectrum = self.builder.get_object("button_plot_spectrum")
        self.button_plot_spectrum.connect("clicked", self.on_button_plot_clicked)

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

    def write_log(self, msg):
        event = [str(datetime.now()), msg]

        self.listmodel_events.append(event)

        self._log.write(msg, event[0])

    def run(self):
        self.window.show_all()

        Gtk.main()

    def destroy(window, self):
        if self._client_socket:
            self._client_socket.close()

        if self._tcp_server_socket:
            self._tcp_server_socket.close()

        sele._zmq_ctx.term()

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
        if self.combobox_satellite.get_active() == -1:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error starting decoding!")
            error_dialog.format_secondary_text("No satellite selected!")
            error_dialog.run()
            error_dialog.destroy()
        else:
            if self.radiobutton_audio_file.get_active():
                if self.filechooser_audio_file.get_filename() is None:
                    error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error loading the audio file!")
                    error_dialog.format_secondary_text("No file selected!")
                    error_dialog.run()
                    error_dialog.destroy()
                else:
                    sample_rate, data = wavfile.read(self.filechooser_audio_file.get_filename())
                    wav_filename = self.filechooser_audio_file.get_filename()
                    self.write_log("Audio file opened with a sample rate of " + str(sample_rate) + " Hz")

                    baudrate = self._satellite.get_active_link().get_baudrate()
                    sync_word = self._satellite.get_active_link().get_sync_word()
                    protocol = self._satellite.get_active_link().get_link_protocol()
                    link_name = self._satellite.get_active_link().get_name()

                    self._decode_audio(self.filechooser_audio_file.get_filename(), baudrate, sync_word, protocol, link_name)
            elif self.radiobutton_udp.get_active():
                if (self.entry_preferences_udp_address.get_text() == "") or (self.entry_preferences_udp_port.get_text() == ""):
                    error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error opening the socket!")
                    error_dialog.format_secondary_text("No address or port provided!")
                    error_dialog.run()
                    error_dialog.destroy()
                else:
                    self._run_udp_decode = True
                    self.button_decode.set_sensitive(False)
                    self.button_stop.set_sensitive(True)
                    self.button_plot_spectrum.set_sensitive(False)
                    self.combobox_satellite.set_sensitive(False)
                    self.combobox_link.set_sensitive(False)
                    self.filechooser_audio_file.set_sensitive(False)
                    self.entry_preferences_udp_address.set_sensitive(False)
                    self.entry_preferences_udp_port.set_sensitive(False)
                    self.switch_raw_bits.set_sensitive(False)
                    self.radiobutton_audio_file.set_sensitive(False)
                    self.radiobutton_udp.set_sensitive(False)

                    address = self.entry_preferences_udp_address.get_text()
                    port = self.entry_preferences_udp_port.get_text()

                    self.write_log("Listening port " + port + " from " + address)

                    baudrate = self._satellite.get_active_link().get_baudrate()
                    sync_word = self._satellite.get_active_link().get_sync_word()
                    protocol = self._satellite.get_active_link().get_link_protocol()
                    link_name = self._satellite.get_active_link().get_name()

                    if self.switch_raw_bits.get_active():
                        thread_decode = threading.Thread(target=self._decode_stream, args=(address, int(port), baudrate, sync_word, protocol, link_name,))
                        thread_decode.start()
                    else:
                        if self.radiobutton_preferences_conn_tcp.get_active():
                            self._tcp_server_socket = self._create_socket_server(address, int(port))

                            if self._tcp_server_socket:
                                # Monitor the socket for incoming connections using GLib's IO watch
                                self._tcp_socket_io_channel = GLib.IOChannel(self._tcp_server_socket.fileno())
                                self._tcp_new_conn_cb_id = GLib.io_add_watch(self._tcp_socket_io_channel, GLib.IO_IN, self._handle_tcp_new_connection)
                        else:
                            # Create SUB socket
                            self._zmq_sub = self._zmq_ctx.socket(zmq.SUB)
                            self._zmq_sub.setsockopt(zmq.RCVTIMEO, 0)   # Non-blocking

                            self._zmq_sub.connect("tcp://" + address + ":" + port)

                            self._zmq_sub.setsockopt(zmq.SUBSCRIBE, bytes([10]))

                            # Add watch to GLib main loop
                            channel = GLib.IOChannel.unix_new(self._zmq_sub.getsockopt(zmq.FD))
                            self._zmq_new_conn_cb_id = GLib.io_add_watch(channel, GLib.IO_IN, self._handle_zmq_message)
            else:
                error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error decoding the satellite data!")
                error_dialog.format_secondary_text("No input selected!")
                error_dialog.run()
                error_dialog.destroy()

    def on_button_stop_clicked(self, button):
        self._stop_decoding()

    def _stop_decoding(self):
        self.button_stop.set_sensitive(False)
        self.button_decode.set_sensitive(True)
        self.button_plot_spectrum.set_sensitive(True)
        self.combobox_satellite.set_sensitive(True)
        self.combobox_link.set_sensitive(True)
        self.filechooser_audio_file.set_sensitive(True)
        self.entry_preferences_udp_address.set_sensitive(True)
        self.entry_preferences_udp_port.set_sensitive(True)
        self.switch_raw_bits.set_sensitive(True)
        self.radiobutton_audio_file.set_sensitive(True)
        self.radiobutton_udp.set_sensitive(True)

        if self.radiobutton_udp.get_active():
            if self.switch_raw_bits.get_active():
                self._run_udp_decode = False
            else:
                if self._tcp_new_conn_cb_id is not None:
                    GLib.source_remove(self._tcp_new_conn_cb_id)
                    self._tcp_new_conn_cb_id = None
                if self._tcp_client_cb_id is not None:
                    GLib.source_remove(self._tcp_client_cb_id)
                    self._tcp_client_cb_id = None
                if self._tcp_server_socket is not None:
                    self._tcp_server_socket.close()
                    self._tcp_server_socket = None
                if self._zmq_new_conn_cb_id is not None:
                    self._zmq_sub.close()
                    GLib.source_remove(self._zmq_new_conn_cb_id)
                    self._zmq_new_conn_cb_id = None

    def on_button_plot_clicked(self, button):
        if self.filechooser_audio_file.get_filename() is None:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error loading the audio file!")
            error_dialog.format_secondary_text("No file selected!")
            error_dialog.run()
            error_dialog.destroy()
        else:
            # Read the wav file (mono)
            sampling_frequency, data = wavfile.read(self.filechooser_audio_file.get_filename())

            samples = list()

            # Convert stereo to mono by reading only the first channel
            if data.ndim > 1:
                for i in range(len(data)):
                    samples.append(data[i][0])
            else:
                samples = data

            # Plot the signal read from wav file
            plt.figure(num='Spectrogram');
            plt.subplot(211)
            plt.title(self.filechooser_audio_file.get_filename())

            plt.plot(samples, linewidth=0.75)
            plt.xlabel('Sample')
            plt.ylabel('Amplitude')

            plt.subplot(212)
            plt.specgram(samples, Fs=sampling_frequency)
            plt.xlabel('Time [sec]')
            plt.ylabel('Frequency [Hz]')

            plt.tight_layout()
            plt.show()

    def on_events_selection_changed(self, widget):
        (model, iter) = self.selection_events.get_selected()
        if iter is not None:
            for pkt in self.decoded_packets_index:
                if pkt.get_name() == model[iter][0]:
                    self.textview_pkt_data.scroll_to_mark(pkt, 0, True, 0, 0)

        return True

    def on_button_clear_clicked(self, button):
        self.textbuffer_pkt_data.set_text("")
        self.decoded_packets_index = []

    def on_combobox_satellite_changed(self, combobox):
        try:
            self._satellite.load_from_file(self._get_json_filename_of_active_sat())

            self.liststore_link.clear()  # Clear the list of packet types

            for lk in self._satellite.get_links():
                self.liststore_link.append([lk.get_name()])
        except (FileNotFoundError, RuntimeError) as e:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error opening the satellite configuration file!")
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()

            self.combobox_link.set_active(-1)
        except:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error opening the satellite configuration file!")
            error_dialog.format_secondary_text("Is the configuration file correct?")
            error_dialog.run()
            error_dialog.destroy()
        finally:
            # Sets the first packet type as the active packet type
            self.combobox_link.set_active(0)

    def on_combobox_link_changed(self, combobox):
        self._satellite.set_active_link(self.combobox_link.get_active())

    def on_toolbutton_about_clicked(self, toolbutton):
        response = self.aboutdialog.run()

        if response == Gtk.ResponseType.DELETE_EVENT:
            self.aboutdialog.hide()

    def on_button_output_connect_clicked(self, button):
        try:
            adr = self.entry_output_address.get_text()
            port = int(self.entry_output_port.get_text())

            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client_socket.connect((adr, port))
            self.write_log("Connected to " + adr + ":" + str(port))

            self.entry_output_address.set_sensitive(False)
            self.entry_output_port.set_sensitive(False)
            self.button_output_connect.set_sensitive(False)
            self.button_output_disconnect.set_sensitive(True)
        except socket.error as e:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error connecting to visualizer server!")
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()

    def on_button_output_disconnect_clicked(self, button):
        self._client_socket.shutdown(socket.SHUT_RDWR)
        self._client_socket.close()

        self.write_log("Disconnected from " + self.entry_output_address.get_text() + ":" + self.entry_output_port.get_text())

        self.entry_output_address.set_sensitive(True)
        self.entry_output_port.set_sensitive(True)
        self.button_output_connect.set_sensitive(True)
        self.button_output_disconnect.set_sensitive(False)

    def _save_preferences(self):
        home = os.path.expanduser('~')
        location = os.path.join(home, _DIR_CONFIG_LINUX)

        if not os.path.exists(location):
            os.mkdir(location)

        with open(location + '/' + _DIR_CONFIG_DEFAULTJSON, 'w', encoding='utf-8') as f:
            json.dump({"callsign":                          self.entry_preferences_general_callsign.get_text(),
                       "location":                          self.entry_preferences_general_location.get_text(),
                       "country":                           self.entry_preferences_general_country.get_text(),
                       "sync_word_max_sync_error":          self.entry_preferences_max_bit_err.get_text(),
                       "ax100_use_len_field_with_err":      self.checkbutton_preferences_protocols_ax100_len.get_active(),
                       "input_socket_type_tcp":             self.radiobutton_preferences_conn_tcp.get_active(),
                       "input_socket_link_layer_enabled":   self.switch_preferences_conn_link_layer.get_active(),
                       "logfile_path":                      self.logfile_chooser_button.get_filename()}, f, ensure_ascii=False, indent=4)

    def _load_preferences(self):
        home = os.path.expanduser('~')
        location = os.path.join(home, _DIR_CONFIG_LINUX)

        if not os.path.isfile(location + "/" + _DIR_CONFIG_DEFAULTJSON):
            self._load_default_preferences()
            self._save_preferences()

        f = open(location + "/" + _DIR_CONFIG_DEFAULTJSON, "r")
        config = json.loads(f.read())
        f.close()

        try:
            self.entry_preferences_general_callsign.set_text(config["callsign"])
            self.entry_preferences_general_location.set_text(config["location"])
            self.entry_preferences_general_country.set_text(config["country"])
            self.entry_preferences_max_bit_err.set_text(config["sync_word_max_sync_error"])
            self.checkbutton_preferences_protocols_ax100_len.set_active(config["ax100_use_len_field_with_err"])
            if config["input_socket_type_tcp"]:
                self.radiobutton_preferences_conn_tcp.set_active(True)
            else:
                self.radiobutton_preferences_conn_zmq.set_active(True)
            self.switch_preferences_conn_link_layer.set_active(config["input_socket_link_layer_enabled"])
            self.logfile_chooser_button.set_filename(config["logfile_path"])
        except:
            self._load_default_preferences()
            self._save_preferences()

    def _load_default_preferences(self):
        self.entry_preferences_general_callsign.set_text(_DEFAULT_CALLSIGN)
        self.entry_preferences_general_location.set_text(_DEFAULT_LOCATION)
        self.entry_preferences_general_country.set_text(_DEFAULT_COUNTRY)
        self.entry_preferences_max_bit_err.set_text(str(_DEFAULT_SYNC_WORD_BIT_ERROR))
        self.checkbutton_preferences_protocols_ax100_len.set_active(_DEFAULT_AX100_USE_LEN_ERR)
        self.radiobutton_preferences_conn_tcp.set_active(_DEFAULT_INPUT_SOCKET_TYPE_TCP)
        self.switch_preferences_conn_link_layer.set_active(_DEFAULT_INPUT_SOCKET_LINK_EN)
        self.logfile_chooser_button.set_filename(_DEFAULT_LOGFILE_PATH)

    def _decode_audio(self, audio_file, baud, sync_word, protocol, link_name):
        sample_rate, data = wavfile.read(audio_file)

        samples = list()

        # Convert stereo to mono by reading only the first channel
        if data.ndim > 1:
            for i in range(len(data)):
                samples.append(data[i][0])
        else:
            samples = data

        mm = TimeSync(sample_rate, baud)

        try:
            if protocol == _PROTOCOL_NGHAM:
                self._find_ngham_pkts(mm.get_bitstream(samples), sync_word, link_name)
            elif protocol == _PROTOCOL_AX100MODE5:
                self._find_ax100mode5_pkts(mm.get_bitstream(samples), sync_word, link_name)
            else:
                raise RuntimeError("The protocol \"" + protocol + "\" is not supported!")
        except RuntimeError as err:
            self.write_log("Error decoding audio file: " + str(err))

    def _decode_stream(self, address, port, baud, sync_word, protocol, link_name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.settimeout(1)
        sock.bind((address, port))

        mm = TimeSync(48000, baud)

        sync_word.reverse()

        bit_decoder = BitDecoder(sync_word, int(self.entry_preferences_max_bit_err.get_text()))

        ngham = pyngham.PyNGHam()
        ax100 = AX100Mode5()

        if self.checkbutton_preferences_protocols_ax100_len.get_active():
            ax100.set_ignore_golay_error(True)

        samples_buf = list()
        while self._run_udp_decode:
            try:
                samples_raw, addr = sock.recvfrom(1024)    # Buffer size is 1024 bytes
                samples_buf += np.frombuffer(bytes(samples_raw), dtype=np.int16).tolist()    # Convert the input bytes to int16 samples

                if len(samples_buf) >= 300*(48000/baud)*8*2:    # Approximately 300 bytes in samples
                    bitstream = mm.decode_stream(samples_buf)
                    samples_buf.clear()
                    for b in bitstream:
                        decoded_byte = bit_decoder.decode_bit(b)
                        if type(decoded_byte) is int:
                            if protocol == _PROTOCOL_NGHAM:
                                pl, err, err_loc = ngham.decode_byte(decoded_byte)
                                if len(pl) == 0:
                                    if err == -1:
                                        bit_decoder.reset()
                                        self.write_log("Error decoding a " + link_name + " packet from " + _SATELLITES[self.combobox_satellite.get_active()][0] + "!")
                                else:
                                    bit_decoder.reset()

                                    tm_now = datetime.now()
                                    self.decoded_packets_index.append(self.textbuffer_pkt_data.create_mark(str(tm_now), self.textbuffer_pkt_data.get_end_iter(), True))
                                    self.write_log(link_name + " packet from " + self._satellite.get_name() + " decoded!")

                                    self._decode_packet(pl)
                            elif protocol == _PROTOCOL_AX100MODE5:
                                pl = ax100.decode_byte(decoded_byte)
                                if type(pl) is list:
                                    bit_decoder.reset()

                                    tm_now = datetime.now()
                                    self.decoded_packets_index.append(self.textbuffer_pkt_data.create_mark(str(tm_now), self.textbuffer_pkt_data.get_end_iter(), True))
                                    self.write_log(link_name + " packet from " + self._satellite.get_name() + " decoded!")

                                    self._decode_packet(pl)

                                    ax100.reset_decoder()
            except RuntimeError as e:
                bit_decoder.reset()
                ax100.reset_decoder()
                self.write_log("Error decoding a " + link_name + " packet from " + self._satellite.get_name() + ": " + str(e))
            except socket.timeout:
                pass

        sock.close()

    def _find_ngham_pkts(self, bitstream, sync_word, link_name):
        sync_word.reverse()

        bit_decoder = BitDecoder(sync_word, int(self.entry_preferences_max_bit_err.get_text()))

        ngham = pyngham.PyNGHam()

        for b in bitstream:
            decoded_byte = bit_decoder.decode_bit(b)
            if type(decoded_byte) is int:
                pl, err, err_loc = ngham.decode_byte(decoded_byte)
                if len(pl) == 0:
                    if err == -1:
                        bit_decoder.reset()
                        self.write_log("Error decoding a " + link_name + " packet from " + _SATELLITES[self.combobox_satellite.get_active()][0] + "!")
                else:
                    bit_decoder.reset()
                    tm_now = datetime.now()
                    self.decoded_packets_index.append(self.textbuffer_pkt_data.create_mark(str(tm_now), self.textbuffer_pkt_data.get_end_iter(), True))
                    self.write_log(link_name + " packet from " + _SATELLITES[self.combobox_satellite.get_active()][0] + " decoded!")
                    self._decode_packet(pl)

    def _find_ax100mode5_pkts(self, bitstream, sync_word, link_name):
        sync_word.reverse()

        bit_decoder = BitDecoder(sync_word, int(self.entry_preferences_max_bit_err.get_text()))

        ax100 = AX100Mode5()

        if self.checkbutton_preferences_protocols_ax100_len.get_active():
            ax100.set_ignore_golay_error(True)

        for b in bitstream:
            decoded_byte = bit_decoder.decode_bit(b)
            if type(decoded_byte) is int:
                pl = ax100.decode_byte(decoded_byte)
                if type(pl) is list:
                    self._decode_packet(pl)

                    # Write event log
                    tm_now = datetime.now()
                    self.decoded_packets_index.append(self.textbuffer_pkt_data.create_mark(str(tm_now), self.textbuffer_pkt_data.get_end_iter(), True))
                    self.write_log(link_name + " packet from " + _SATELLITES[self.combobox_satellite.get_active()][0] + " decoded!")

                    ax100.reset_decoder()

    def _decode_packet(self, pkt):
        try:
            pkt_data = str()
            pkt_json = str()
            sat_json = self._get_json_filename_of_active_sat()
            if self._satellite.get_active_link().get_network_protocol() == "CSP":
                self._packet_csp_buf.set_config(sat_json)
                self._packet_csp_buf.set_pkt(pkt)
                pkt_data = str(self._packet_csp_buf)
                pkt_json = self._packet_csp_buf.get_data()
            elif self._satellite.get_active_link().get_network_protocol() == "SLP":
                pkt_sl = PacketSLP(sat_json, pkt)
                pkt_data = str(pkt_sl)
                pkt_json = pkt_sl.get_data()
        except RuntimeError as e:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error decoding a packet!")
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()
        else:
            pkt_txt = str()
            if self.radiobutton_audio_file.get_active():
                pkt_txt = "Decoded packet from \"" + self.filechooser_audio_file.get_filename() + "\":\n"
            else:
                pkt_txt = "Decoded packet from " + self.entry_preferences_udp_address.get_text()  + ":" + self.entry_preferences_udp_port.get_text() + ":\n"

            pkt_txt = pkt_txt + pkt_data
            pkt_txt = pkt_txt + "========================================================\n"
            self.textbuffer_pkt_data.insert(self.textbuffer_pkt_data.get_end_iter(), pkt_txt)

            if self._client_socket and not self.button_output_connect.get_sensitive():
                try:
                    self._client_socket.send(pkt_json.encode('utf-8'))  # Send message to server
                except socket.error as e:
                    error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error transmitting the decoded data!")
                    error_dialog.format_secondary_text(str(e))
                    error_dialog.run()
                    error_dialog.destroy()

    def _get_json_filename_of_active_sat(self):
        sat_config_file = str()

        for i in range(len(_SATELLITES)):
            if self.combobox_satellite.get_active() == i:
                if os.path.isfile(_SAT_JSON_LOCAL_PATH + _SATELLITES[i][1]):
                    sat_config_file = _SAT_JSON_LOCAL_PATH + _SATELLITES[i][1]
                else:
                    sat_config_file = _SAT_JSON_SYSTEM_PATH + _SATELLITES[i][1]

        return sat_config_file

    def _create_socket_server(self, adr, port):
        """Create a TCP/IP socket server"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((adr, port))
            server_socket.listen(1)
            return server_socket
        except socket.error as e:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error creating a socket server!")
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()
            return None

    def _handle_tcp_new_connection(self, source, condition):
        """Handle incoming connections"""
        if condition == GLib.IO_IN:
            client_socket, address = self._tcp_server_socket.accept()
            self.write_log("TCP client connected!")

            # Create an IOChannel for the client socket to handle incoming data
            client_io_channel = GLib.IOChannel(client_socket.fileno())
            client_io_channel.set_encoding(None)  # Binary mode (important for raw data)

            # Monitor the client socket for incoming data
            self._tcp_client_cb_id = GLib.io_add_watch(client_io_channel, GLib.IO_IN, self._handle_tcp_client_data, client_socket)

        return True  # Keep the handler active

    def _handle_tcp_client_data(self, source, condition, client_socket):
        """Handle incoming data from the client"""
        if condition == GLib.IO_IN:
            try:
                data = client_socket.recv(1024)  # Read incoming data (max 1024 bytes)
                if data:
                    protocol = self._satellite.get_active_link().get_link_protocol()
                    if protocol == _PROTOCOL_NGHAM:
                        try:
                            ngham = pyngham.PyNGHam()
                            pl, err, err_loc = ngham.decode(data)
                            self._decode_packet(pl)
                        except:
                            self.write_log("Error decoding NGHam packet from TCP socket!")
                    elif protocol == _PROTOCOL_AX100MODE5:
                        try:
                            ax100 = AX100Mode5()
                            pl = ax100.decode(list(data))
                            self._decode_packet(pl)
                        except:
                            self.write_log("Error decoding AX100-Mode5 packet from TCP socket!")
                    else:
                        self.write_log("Unknown protocol received from TCP client!")
                else:
                    # Connection closed by client
                    self.write_log("TCP connection closed by client!")
                    client_socket.close()
                    self._tcp_server_socket.close()
                    self._stop_decoding()
                    return False  # Stop the IO watch for this client
            except socket.error as e:
                self.write_log("Error receiving data from TCP client: " + str(e))
                client_socket.close()
                self._tcp_server_socket.close()
                self._stop_decoding()
                return False    # Stop the IO watch for this client

        return True  # Keep the handler active

    def _handle_zmq_message(self, source, condition):
        """Callback for ZMQ messages"""
        protocol = self._satellite.get_active_link().get_link_protocol()

        while True:
            try:
                data = self._zmq_sub.recv(flags=zmq.NOBLOCK)

                pl = list(data)[1:].copy()

                if protocol == _PROTOCOL_NGHAM:
                    if self.switch_preferences_conn_link_layer.get_active():
                        ngham = pyngham.PyNGHam()
                        pl, err, err_loc = ngham.decode(list(data))
                    self._decode_packet(pl)
                elif protocol == _PROTOCOL_AX100MODE5:
                    if self.switch_preferences_conn_link_layer.get_active():
                        ax100 = AX100Mode5()
                        pl = ax100.decode(list(data)[len(self._satellite.get_active_link().get_preamble()) + 4:])
                    self._decode_packet(pl)
                else:
                    self.write_log("Unknown protocol received from ZMQ socket!")
            except zmq.Again:
                break;
            except Exception as e:
                self.write_log("Error receiving data from ZMQ socket: " + str(e))
                return False    # Return False to remove the watch if there's a critical error

        return True # Keep the handler active
