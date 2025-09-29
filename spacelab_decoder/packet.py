#
#  packet.py
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


import json

# Used inside `eval()` calls
import numpy as np
import struct
import datetime

class PacketSLP:

    def __init__(self, sat_config, pkt_raw):
        with open(sat_config) as f:
            self.sat_packet = json.load(f)

        self.packet = pkt_raw

    def set_config(self, sat_config):
        with open(sat_config) as f:
            self.sat_packet = json.load(f)

    def set_pkt(self, pkt_raw):
        self.packet = pkt_raw.copy()

    def __str__(self):
        buf = str()

        pkt = self.packet

        link_idx = int()
        type_idx = int()
        pkt_type_found = False
        for i in range(len(self.sat_packet['links'])):
            if self.sat_packet['links'][i]['protocol_network'] == "SLP":    # Check if the link uses SLP
                for j in range(len(self.sat_packet['links'][i]['types'])):
                    if pkt[0] == self.sat_packet['links'][i]['types'][j]['fields'][0]['value']:
                        link_idx = i
                        type_idx = j
                        pkt_type_found = True
                        break

        if pkt_type_found:
            buf = buf + "\t" + "Satellite" + ": " + self.sat_packet['name'] + "\n"
            buf = buf + "\t" + "Link" + ": " + self.sat_packet['links'][link_idx]['name'] + "\n"
            buf = buf + "\t" + "Data Source" + ": " + self.sat_packet['links'][link_idx]['types'][type_idx]['name'] + "\n"
            buf = buf + "\t" + "Link Protocol" + ": " + self.sat_packet['links'][link_idx]['protocol_link'] + "\n"
            buf = buf + "\t" + "Network Protocol" + ": " + self.sat_packet['links'][link_idx]['protocol_network'] + "\n"
            buf = buf + "\t" + "Data" + ":" + "\n"

            for i in range(len(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'])):
                buf = buf + "\t\t" + self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['name'] + ": " + str(eval(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['conversion'])) + " " + self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['unit'] + "\n"
        else:
            raise RuntimeError("Unknown packet ID!")

        return buf

    def get_data(self):
        pkt = self.packet

        link_idx = int()
        type_idx = int()
        pkt_type_found = False
        for i in range(len(self.sat_packet['links'])):
            if self.sat_packet['links'][i]['protocol_network'] == "SLP":    # Check if the link uses SLP
                for j in range(len(self.sat_packet['links'][i]['types'])):
                    if pkt[0] == self.sat_packet['links'][i]['types'][j]['fields'][0]['value']:
                        link_idx = i
                        type_idx = j
                        pkt_type_found = True
                        break

        data = dict()

        if pkt_type_found:
            for i in range(len(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'])):
                data[self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['id']] = str(eval(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['conversion']))
        else:
            raise RuntimeError("Unknown packet ID!")

        return json.dumps(data)

    def _decode_callsign(self, cs_raw):
        found = False
        buf = str()
        for char in cs_raw:
            if found:
                buf = buf + chr(char)
            else:
                if char != ord('0'):
                    buf = buf + chr(char)
                    found = True

        return buf


class PacketCSP(PacketSLP):

    def __init__(self):
        self._pkt_buf = list()
        self._pkt_counter = 0
        self._data_request_pkt_received = False

    def __str__(self):
        buf = str()

        pkt = self.packet

        link_idx = int()
        type_idx = int()
        pkt_type_found = False
        dst_port = int(((pkt[1] & 15) << 2) | (pkt[2] >> 6))
        for i in range(len(self.sat_packet['links'])):
            if self.sat_packet['links'][i]['protocol_network'] == "CSP":    # Check if the link uses CSP
                for j in range(len(self.sat_packet['links'][i]['types'])):
                    if dst_port == self.sat_packet['links'][i]['types'][j]['fields'][3]['value']: # Search for the destination port
                        if dst_port == 0:   # CSP CMP packets
                            if pkt[5] != self.sat_packet['links'][i]['types'][j]['fields'][11]['value']:    # 11 = CMP Code field
                                continue
                        if dst_port == 46:  # Set parameter packets
                            if pkt[6] != self.sat_packet['links'][i]['types'][j]['fields'][12]['value']:    # 12 = Parameter size field
                                continue
                        if dst_port == 38:  # Data request
                            if self._data_request_pkt_received == False:
                                if struct.unpack('>H', bytes(pkt[9:11]))[0] > 200:
                                    self._pkt_buf = pkt.copy()
                                    self._pkt_counter = struct.unpack('>H', bytes(pkt[6:8]))[0]
                                    self._data_request_pkt_received = True
                                    return str()
                            else:
                                if self._pkt_counter == struct.unpack('>H', bytes(pkt[6:8]))[0]:
                                    if pkt[4] < pkt[5]-1:
                                        self._pkt_buf += pkt[11:]
                                        return str()
                                    elif pkt[4] == pkt[5]-1:
                                        self._pkt_buf += pkt[11:]
                                        self._pkt_counter = 0
                                        self._data_request_pkt_received = False
                                        pkt.clear()
                                        pkt = self._pkt_buf.copy()
                                        self.packet = pkt.copy()
                                        self._pkt_buf.clear()
                                else:
                                    self._pkt_buf.clear()
                                    self._pkt_counter = 0
                                    self._data_request_pkt_received = False
                                    raise RuntimeError("Data request packet lost!")
                        link_idx = i
                        type_idx = j
                        pkt_type_found = True
                        break

        if pkt_type_found:
            buf = buf + "\t" + "Satellite" + ": " + self.sat_packet['name'] + "\n"
            buf = buf + "\t" + "Link" + ": " + self.sat_packet['links'][link_idx]['name'] + "\n"
            buf = buf + "\t" + "Data Source" + ": " + self.sat_packet['links'][link_idx]['types'][type_idx]['name'] + "\n"
            buf = buf + "\t" + "Link Protocol" + ": " + self.sat_packet['links'][link_idx]['protocol_link'] + "\n"
            buf = buf + "\t" + "Network Protocol" + ": " + self.sat_packet['links'][link_idx]['protocol_network'] + "\n"
            buf = buf + "\t" + "Data" + ":" + "\n"

            for i in range(len(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'])):
                buf = buf + "\t\t" + self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['name'] + ": " + str(eval(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['conversion'])) + " " + self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['unit'] + "\n"
        else:
            raise RuntimeError("Unknown destination port!")

        return buf

    def get_data(self):
        pkt = self.packet

        link_idx = int()
        type_idx = int()
        pkt_type_found = False
        dst_port = int(((pkt[1] & 15) << 2) | (pkt[2] >> 6))
        for i in range(len(self.sat_packet['links'])):
            if self.sat_packet['links'][i]['protocol_network'] == "CSP":    # Check if the link uses CSP
                for j in range(len(self.sat_packet['links'][i]['types'])):
                    if dst_port == self.sat_packet['links'][i]['types'][j]['fields'][3]['value']:   # Search for the destination port
                        if dst_port == 0:   # CSP CMP packets
                            if pkt[5] != self.sat_packet['links'][i]['types'][j]['fields'][11]['value']:    # 11 = CMP Code field
                                continue
                        link_idx = i
                        type_idx = j
                        pkt_type_found = True
                        break

        data = dict()

        if pkt_type_found:
            for i in range(len(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'])):
                data[self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['id']] = str(eval(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['conversion']))
        else:
            raise RuntimeError("Unknown destination port!")

        return json.dumps(data)
