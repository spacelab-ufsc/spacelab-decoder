#
#  test_ui.py
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


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def test_ui():
    builder = Gtk.Builder()
    builder.add_from_file("spacelab_decoder/data/ui/spacelab_decoder.glade")

    # Main window
    window                  = builder.get_object("window_main")
    button_preferences      = builder.get_object("button_preferences")
    button_decode           = builder.get_object("button_decode")
    button_stop             = builder.get_object("button_stop")
    button_plot_spectrum    = builder.get_object("button_plot_spectrum")
    button_clean            = builder.get_object("button_clean")
    toolbutton_about        = builder.get_object("toolbutton_about")
    combobox_satellite      = builder.get_object("combobox_satellite")
    combobox_packet_type    = builder.get_object("combobox_packet_type")
    filechooser_audio_file  = builder.get_object("filechooser_audio_file")
    textview_pkt_data       = builder.get_object("textview_pkt_data")
    treeview_events         = builder.get_object("treeview_events")
    filefilter_audio        = builder.get_object("filefilter_audio")
    liststore_satellite     = builder.get_object("liststore_satellite")
    liststore_packet_type   = builder.get_object("liststore_packet_type")
    radiobutton_audio_file  = builder.get_object("radiobutton_audio_file")
    radiobutton_udp         = builder.get_object("radiobutton_udp")

    assert window                   != None
    assert button_preferences       != None
    assert button_decode            != None
    assert button_plot_spectrum     != None
    assert button_clean             != None
    assert toolbutton_about         != None
    assert combobox_satellite       != None
    assert combobox_packet_type     != None
    assert filechooser_audio_file   != None
    assert textview_pkt_data        != None
    assert treeview_events          != None
    assert filefilter_audio         != None
    assert liststore_satellite      != None
    assert liststore_packet_type    != None
    assert radiobutton_audio_file   != None
    assert radiobutton_udp          != None

    assert window.get_title()       == "SpaceLab Decoder"

    # About dialog
    aboutdialog_spacelab_decoder    = builder.get_object("aboutdialog_spacelab_decoder")

    assert aboutdialog_spacelab_decoder != None

    assert aboutdialog_spacelab_decoder.get_website()       == "https://github.com/spacelab-ufsc/spacelab-decoder"
    assert aboutdialog_spacelab_decoder.get_website_label() == "https://github.com/spacelab-ufsc/spacelab-decoder"
    assert aboutdialog_spacelab_decoder.get_title()         == "About SpaceLab Decoder"

    # Preferences dialog
    dialog_preferences                  = builder.get_object("dialog_preferences")
    entry_preferences_general_callsign  = builder.get_object("entry_preferences_general_callsign")
    entry_preferences_general_location  = builder.get_object("entry_preferences_general_location")
    entry_preferences_general_country   = builder.get_object("entry_preferences_general_country")
    button_preferences_ok               = builder.get_object("button_preferences_ok")
    button_preferences_default          = builder.get_object("button_preferences_default")
    button_preferences_cancel           = builder.get_object("button_preferences_cancel")
    entry_preferences_udp_address       = builder.get_object("entry_preferences_udp_address")
    entry_preferences_udp_port          = builder.get_object("entry_preferences_udp_port")

    assert dialog_preferences                   != None
    assert entry_preferences_general_callsign   != None
    assert entry_preferences_general_location   != None
    assert entry_preferences_general_country    != None
    assert button_preferences_ok                != None
    assert button_preferences_default           != None
    assert button_preferences_cancel            != None
    assert entry_preferences_udp_address        != None
    assert entry_preferences_udp_port           != None

    assert dialog_preferences.get_title()       == "Preferences"
