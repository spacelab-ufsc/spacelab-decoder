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
import csv
import threading
import socket

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

import matplotlib.pyplot as plt
from scipy.io import wavfile

import pyngham

import spacelab_decoder.version

from spacelab_decoder.time_sync import TimeSync
from spacelab_decoder.bit_buffer import BitBuffer, _BIT_BUFFER_LSB
from spacelab_decoder.sync_word import SyncWord, _SYNC_WORD_LSB
from spacelab_decoder.byte_buffer import ByteBuffer, _BYTE_BUFFER_LSB
from spacelab_decoder.packet import Packet, PacketCSP
from spacelab_decoder.ccsds import CCSDS_POLY
from spacelab_decoder.golay24 import Golay24

_UI_FILE_LOCAL                  = os.path.abspath(os.path.dirname(__file__)) + '/data/ui/spacelab_decoder.glade'
_UI_FILE_LINUX_SYSTEM           = '/usr/share/spacelab_decoder/spacelab_decoder.glade'

_ICON_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/spacelab_decoder_256x256.png'
_ICON_FILE_LINUX_SYSTEM         = '/usr/share/icons/spacelab_decoder_256x256.png'

_LOGO_FILE_LOCAL                = os.path.abspath(os.path.dirname(__file__)) + '/data/img/spacelab-logo-full-400x200.png'
_LOGO_FILE_LINUX_SYSTEM         = '/usr/share/spacelab_decoder/spacelab-logo-full-400x200.png'

_DIR_CONFIG_LINUX               = '.spacelab_decoder'
_DIR_CONFIG_WINDOWS             = 'spacelab_decoder'

_SAT_JSON_LOCAL_PATH            = os.path.abspath(os.path.dirname(__file__)) + '/data/satellites/'
_SAT_JSON_SYSTEM_PATH           = '/usr/share/spacelab_decoder/'

_DEFAULT_CALLSIGN               = 'PP5UF'
_DEFAULT_LOCATION               = 'Florianópolis'
_DEFAULT_COUNTRY                = 'Brazil'
_DEFAULT_MAX_PKT_LEN_BYTES      = 300

# Defining logfile default local
_DIR_CONFIG_LOGFILE_LINUX       = 'spacelab_decoder'
_DEFAULT_LOGFILE_PATH           = os.path.join(os.path.expanduser('~'), _DIR_CONFIG_LOGFILE_LINUX)
_DEFAULT_LOGFILE                = 'logfile.csv'

_SATELLITES                     = [["FloripaSat-1", "floripasat-1.json"],
                                   ["GOLDS-UFSC", "golds-ufsc.json"],
                                   ["Aldebaran-1", "aldebaran-1.json"],
                                   ["Catarina-A1", "catarina-a1.json"],
                                   ["Catarina-A2", "catarina-a2.json"],
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

        self.ngham = pyngham.PyNGHam()

        self._tcp_server_socket = None

        self.decoded_packets_index = list()

        self._run_udp_decode = False

        self._client_socket = None

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
        self.liststore_packet_type = self.builder.get_object("liststore_packet_type")
        self.combobox_packet_type = self.builder.get_object("combobox_packet_type")
        self.combobox_packet_type.pack_start(cell, True)
        self.combobox_packet_type.add_attribute(cell, "text", 0)

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

        if not os.path.exists(_DEFAULT_LOGFILE_PATH):
            os.mkdir(_DEFAULT_LOGFILE_PATH)

        with open(self.logfile_chooser_button.get_filename() + '/' + _DEFAULT_LOGFILE, 'a') as logfile:
            writer = csv.writer(logfile, delimiter='\t')
            writer.writerow(event)

    def run(self):
        self.window.show_all()

        Gtk.main()

    def destroy(window, self):
        if self._client_socket:
            self._client_socket.close()

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

                    baudrate, sync_word, protocol, link_name = self._get_link_info()

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
                    self.combobox_satellite.set_sensitive(False)
                    self.combobox_packet_type.set_sensitive(False)
                    self.filechooser_audio_file.set_sensitive(False)
                    self.entry_preferences_udp_address.set_sensitive(False)
                    self.entry_preferences_udp_port.set_sensitive(False)
                    self.switch_raw_bits.set_sensitive(False)
                    self.radiobutton_audio_file.set_sensitive(False)
                    self.radiobutton_udp.set_sensitive(False)

                    address = self.entry_preferences_udp_address.get_text()
                    port = self.entry_preferences_udp_port.get_text()

                    self.write_log("Listening port " + port + " from " + address)

                    baudrate, sync_word, protocol, link_name = self._get_link_info()

                    if self.switch_raw_bits.get_active():
                        thread_decode = threading.Thread(target=self._decode_stream, args=(address, int(port), baudrate, sync_word, protocol, link_name,))
                        thread_decode.start()
#                    self._decode_stream(address, int(port), baudrate, sync_word, protocol, link_name)
                    else:
                        self._tcp_server_socket = self._create_socket_server(address, int(port))

                        if self._tcp_server_socket:
                            # Monitor the socket for incoming connections using GLib's IO watch
                            self._tcp_socket_io_channel = GLib.IOChannel(self._tcp_server_socket.fileno())
                            GLib.io_add_watch(self._tcp_socket_io_channel, GLib.IO_IN, self._handle_tcp_new_connection)
            else:
                error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error decoding the satellite data!")
                error_dialog.format_secondary_text("No input selected!")
                error_dialog.run()
                error_dialog.destroy()

    def on_button_stop_clicked(self, button):
        self._run_udp_decode = False
        self.button_stop.set_sensitive(False)
        self.button_decode.set_sensitive(True)
        self.combobox_satellite.set_sensitive(True)
        self.combobox_packet_type.set_sensitive(True)
        self.filechooser_audio_file.set_sensitive(True)
        self.entry_preferences_udp_address.set_sensitive(True)
        self.entry_preferences_udp_port.set_sensitive(True)
        self.switch_raw_bits.set_sensitive(True)
        self.radiobutton_audio_file.set_sensitive(True)
        self.radiobutton_udp.set_sensitive(True)

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
        # Clear the list of packet types
        self.liststore_packet_type.clear()

        links_names = list()

        with open(self._get_json_filename_of_active_sat()) as f:
            sat_info = json.load(f)
            for i in range(len(sat_info['links'])):
                links_names.append(sat_info['links'][i]['name'])

        # Define the list of packet types from the JSON file of the given satellite
        for n in links_names:
            self.liststore_packet_type.append([n])

        # Sets the first packet type as the active packet type
        self.combobox_packet_type.set_active(0)

        self._get_link_info()

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

    def _load_preferences(self):
        home = os.path.expanduser('~')
        location = os.path.join(home, _DIR_CONFIG_LINUX)

    def _load_default_preferences(self):
        self.entry_preferences_general_callsign.set_text(_DEFAULT_CALLSIGN)
        self.entry_preferences_general_location.set_text(_DEFAULT_LOCATION)
        self.entry_preferences_general_country.set_text(_DEFAULT_COUNTRY)

    def _decode_audio(self, audio_file, baud, sync_word, protocol, link_name):
        sample_rate, data = wavfile.read(audio_file)

        samples = list()

        # Convert stereo to mono by reading only the first channel
        if data.ndim > 1:
            for i in range(len(data)):
                samples.append(data[i][0])
        else:
            samples = data

        mm = TimeSync()

        if protocol == _PROTOCOL_NGHAM:
            self._find_ngham_pkts(mm.get_bitstream(samples, sample_rate, baud), sync_word, link_name)
        elif protocol == _PROTOCOL_AX100MODE5:
            self._find_ax100mode5_pkts(mm.get_bitstream(samples, sample_rate, baud), sync_word, link_name)
        else:
            error_dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error decoding the audio file!")
            error_dialog.format_secondary_text("The protocol \"" + protocol + "\" is not supported!")
            error_dialog.run()
            error_dialog.destroy()

    def _decode_stream(self, address, port, baud, sync_word, protocol, link_name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.settimeout(1)
        sock.bind((address, port))

        mm = TimeSync()

        while self._run_udp_decode:
            try:
                samples, addr = sock.recvfrom(1024) # Buffer size is 1024 bytes
                if protocol == _PROTOCOL_NGHAM:
                    self._find_ngham_pkts(mm.get_bitstream(samples, 48000.0, baud), sync_word, link_name)
                elif protocol == _PROTOCOL_AX100MODE5:
                    self._find_ax100mode5_pkts(mm.get_bitstream(samples, 48000.0, baud), sync_word, link_name)
            except socket.timeout:
                pass

        sock.close()

    def _find_ngham_pkts(self, bitstream, s_word, link_name):
        sync_word_buf = BitBuffer(32, _BIT_BUFFER_LSB)

        s_word.reverse()
        sync_word = SyncWord(s_word, _SYNC_WORD_LSB)

        byte_buf = ByteBuffer(_BYTE_BUFFER_LSB)

        packet_detected = False
        packet_buf = list()

        for bit in bitstream:
            if packet_detected:
                byte_buf.push(bool(bit))
                if byte_buf.is_full():
                    if len(packet_buf) < _DEFAULT_MAX_PKT_LEN_BYTES:
                        pkt_byte = byte_buf.to_byte()
                        packet_buf.append(pkt_byte)

                        pl, err, err_loc = self.ngham.decode_byte(pkt_byte)
                        if len(pl) == 0:
                            if err == -1:
                                packet_detected = False
                                self.write_log("Error decoding a " + link_name + " packet from " + _SATELLITES[self.combobox_satellite.get_active()][0] + "!")
                        else:
                            packet_detected = False
                            tm_now = datetime.now()
                            self.decoded_packets_index.append(self.textbuffer_pkt_data.create_mark(str(tm_now), self.textbuffer_pkt_data.get_end_iter(), True))
                            self.write_log(link_name + " packet from " + _SATELLITES[self.combobox_satellite.get_active()][0] + " decoded!")
                            self._decode_packet(pl)
                        byte_buf.clear()
            sync_word_buf.push(bool(bit))
            if (sync_word_buf == sync_word):
                packet_buf = []
                packet_detected = True
                byte_buf.clear()

    def _find_ax100mode5_pkts(self, bitstream, s_word, link_name):
        sync_word_buf = BitBuffer(32, _BIT_BUFFER_LSB)

        s_word.reverse()
        sync_word = SyncWord(s_word, _SYNC_WORD_LSB)

        byte_buf = ByteBuffer(_BYTE_BUFFER_LSB)

        packet_detected = False
        packet_buf = list()

        packet_len = 255

        for bit in bitstream:
            if packet_detected:
                byte_buf.push(bool(bit))
                if byte_buf.is_full():
                    pkt_byte = byte_buf.to_byte()
                    packet_buf.append(pkt_byte)

                    if len(packet_buf) == 3:
                        # Decode lenght field
                        gol = Golay24()
                        packet_len = gol.decode(packet_buf)[1]
                    elif len(packet_buf) == packet_len + 3:
                        packet_detected = False
                        # Add padding with zeros
                        rs_pl = packet_buf[3:-32]
                        while len(rs_pl) < 223:
                            rs_pl.append(0)
                        # Reed-Solomon decoding
                        rs = pyngham.RS(8, 0x187, 112, 11, 16, 0)
                        csp_pkt, num_err, err_pos = rs.decode(rs_pl + packet_buf[-32:], [0], 0)
                        if len(csp_pkt) == 0:
                            self.write_log("Error decoding a " + link_name + " packet from " + _SATELLITES[self.combobox_satellite.get_active()][0] + "!")
                        else:
                            # Write event log
                            tm_now = datetime.now()
                            self.decoded_packets_index.append(self.textbuffer_pkt_data.create_mark(str(tm_now), self.textbuffer_pkt_data.get_end_iter(), True))
                            self.write_log(link_name + " packet from " + _SATELLITES[self.combobox_satellite.get_active()][0] + " decoded!")

                            # Decode Reed-Solomon payload
                            self._decode_packet(csp_pkt)
                    elif len(packet_buf) > 3:
                        # De-scramble
                        packet_buf[-1] = packet_buf[-1] ^ CCSDS_POLY[len(packet_buf) - 4]

                    byte_buf.clear()
            sync_word_buf.push(bool(bit))
            # Detect sync word
            if (sync_word_buf == sync_word):
                packet_buf = []
                packet_detected = True
                byte_buf.clear()

    def _decode_packet(self, pkt):
        try:
            pkt_data = str()
            pkt_json = str()
            sat_json = self._get_json_filename_of_active_sat()
            if sat_json[-16:] == _SATELLITES[4][1]: # Catarina-A2
                pkt_csp = PacketCSP(sat_json, pkt)
                pkt_data = str(pkt_csp)
                pkt_json = pkt_csp.get_data()
            else:
                pkt_sl = Packet(sat_json, pkt)
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

    def _get_link_info(self):
        with open(self._get_json_filename_of_active_sat()) as f:
            sat_info = json.load(f)
            link_name   = sat_info['links'][self.combobox_packet_type.get_active()]['name']
            baudrate    = sat_info['links'][self.combobox_packet_type.get_active()]['baudrate']
            sync_word   = sat_info['links'][self.combobox_packet_type.get_active()]['sync_word']
            protocol    = sat_info['links'][self.combobox_packet_type.get_active()]['protocol']

            return baudrate, sync_word, protocol, link_name

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
            GLib.io_add_watch(client_io_channel, GLib.IO_IN, self._handle_tcp_client_data, client_socket)

        return True  # Keep the handler active

    def _handle_tcp_client_data(self, source, condition, client_socket):
        """Handle incoming data from the client"""
        if condition == GLib.IO_IN:
            try:
                data = client_socket.recv(1024)  # Read incoming data (max 1024 bytes)
                if data:
                    baudrate, sync_word, protocol, link_name = self._get_link_info()

                    if protocol == _PROTOCOL_NGHAM:
                        pl, err, err_loc = self.ngham.decode(data)
                        self._decode_packet(pl)
                    elif protocol == _PROTOCOL_AX100MODE5:
                        # TODO
                        #self._decode_packet(pl)
                        pass
                    else:
                        self.write_log("Unknown protocol received from TCP port!")
                else:
                    # Connection closed by client
                    client_socket.close()
                    return False  # Stop the IO watch for this client
            except socket.error as e:
                client_socket.close()
                self.write_log("Error receiving data from TCP client: " + str(e))
                return False  # Stop the IO watch for this client
        return True  # Keep the handler active
