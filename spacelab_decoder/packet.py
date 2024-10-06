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
        pkt_type_found = False
        for i in range(len(self.sat_packet['links'])):
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
            buf = buf + "\t" + "Protocol" + ": " + self.sat_packet['links'][link_idx]['protocol'] + "\n"
            buf = buf + "\t" + "Data" + ":" + "\n"

            for i in range(len(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'])):
                buf = buf + "\t\t" + self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['name'] + ": " + str(eval(self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['conversion'])) + " " + self.sat_packet['links'][link_idx]['types'][type_idx]['fields'][i]['unit'] + "\n"
        else:
            raise RuntimeError("Unknown packet ID!")

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
