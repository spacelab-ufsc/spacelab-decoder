#
#  beacon.py
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
__version__     = "0.2.0"
__maintainer__  = "Gabriel Mariano Marcelino - PU5GMA"
__email__       = "gabriel.mm8@gmail.com"
__status__      = "Development"


BEACON_PACKET_NGHAM_OBDH    = 0x00
BEACON_PACKET_NGHAM_EPS     = 0x01
BEACON_PACKET_NGHAM_TTC     = 0x02
BEACON_PACKET_AX25_OBDH     = 0x03
BEACON_PACKET_AX25_EPS      = 0x04
BEACON_PACKET_AX25_TTC      = 0x05

class Beacon:

    def __init__(self, packet=None):
        self.process_packet(packet)

    def process_packet(self, packet):
        self.pkt_id = packet[0]
        self.pkt_src = str(packet[1:7])
#        self.battery_temperature = self._get_battery_voltage(packet[])

    def print_data(self):
        data = str()

        data = 'Beacon packet with '
        if (self.pkt_id == BEACON_PACKET_NGHAM_OBDH) or (self.pkt_id == BEACON_PACKET_AX25_OBDH):
            data = data + 'OBDH'
        elif (self.pkt_id == BEACON_PACKET_NGHAM_EPS) or (self.pkt_id == BEACON_PACKET_AX25_OBDH):
            data = data + 'EPS'
        elif (self.pkt_id == BEACON_PACKET_NGHAM_TTC) or (self.pkt_id == BEACON_PACKET_AX25_OBDH):
            data = data + 'TTC'
        else:
            data = data + 'UNKNOWN'

        data = data + ' data from ' + self.pkt_src + '\n\n'
        data = data + 'Protocol: \n'
        data = data + 'Battery voltage: ' + str(self._get_battery_voltage(self.battery_voltage)) + ' V\n'
        data = data + 'Battery temperature: ' + str(self._get_battery_temperature(self.battery_temperature)) + ' oC\n'

        return data

    def _get_battery_voltage(self, raw):
        return (raw/32.0)*4.883e-3

    def _get_battery_temperature(self, raw):
        return (raw*0.125)/32.0

    def _get_battery_charge(self, raw):
        return raw*6.25*1e-4

    def _get_solar_panel_current(self, raw):
        return raw*(2.5/4095)*(1/(0.05*0.025*3300))

    def _get_solar_panel_voltage(self, raw):
        return raw*(2.5/4095)*(100e3 + 93.1e3)/100e3

    def _get_imu_accelerometer(self, raw):
        return int(raw)*16.0/32768.0

    def _get_imu_gyroscope(self, raw):
        return int(val)*250.0/32768.0
