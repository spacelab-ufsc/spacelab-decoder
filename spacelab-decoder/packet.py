#
#  packet.py
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

__author__      = "Gabriel Mariano Marcelino - PU5GMA"
__copyright__   = "Copyright (C) 2021, Universidade Federal de Santa Catarina"
__credits__     = ["Gabriel Mariano Marcelino - PU5GMA"]
__license__     = "GPL3"
__version__     = "0.2.12"
__maintainer__  = "Gabriel Mariano Marcelino - PU5GMA"
__email__       = "gabriel.mm8@gmail.com"
__status__      = "Development"


import json

class Packet:

    def __init__(self, sat_config, pkt_raw):
        with open(sat_config) as f:
            self.sat_packet = json.load(f)

        self.packet = pkt_raw

    def __str__(self):
        buf = str()

        pkt = self.packet

        link_idx = int()
        type_idx = int()
        for i in range(len(self.sat_packet['links'])):
            for j in range(len(self.sat_packet['links'][i]['types'])):
                if pkt[0] == self.sat_packet['links'][i]['types'][j]['fields'][0]['value']:
                    link_idx = i
                    type_idx = j
                    break

        buf = buf + "\t" + "Satellite" + ": " + self.sat_packet['name'] + "\n"
        buf = buf + "\t" + "Link" + ": " + self.sat_packet['links'][link_idx]['name'] + "\n"
        buf = buf + "\t" + "Data Source" + ": " + self.sat_packet['links'][link_idx]['types'][type_idx]['name'] + "\n"
        buf = buf + "\t" + "Source Address" + ": " + self._decode_callsign(pkt[1:8]) + "\n"
        buf = buf + "\t" + "Data" + ":" + "\n"

        for i in range(2, len(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'])):
            buf = buf + "\t\t" + self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['name'] + ": " + str(eval(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['conversion'])) + " " + self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['unit'] + "\n"

        return buf

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
