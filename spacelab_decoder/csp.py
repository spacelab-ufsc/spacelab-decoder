#
#  csp.py
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

# Priorities
_CSP_PRIO_CRITICAL  = 0
_CSP_PRIO_HIGH      = 1
_CSP_PRIO_NORM      = 2
_CSP_PRIO_LOW       = 3

# Ports
_CSP_PORT_CMP       = 0
_CSP_PORT_PING      = 1
_CSP_PORT_PS        = 2
_CSP_PORT_MEMFREE   = 3
_CSP_PORT_REBOOT    = 4
_CSP_PORT_BUF_FREE  = 5
_CSP_PORT_UPTIME    = 6
_CSP_PORT_BEACON    = 10

class CSP:
    """
    CSP class.

    This class implements the CSP protocol.
    """

    def __init__(self):
        """
        Class initialization.

        :return: None
        :rtype: None
        """
        pass

    def encode(self, prio, src_adr, dst_adr, src_port, dst_port, hmac, xtea, rdp, crc, pl):
        """
        Encode a CSP packet.

        :param prio: Packet priority (must be between 0 and 3).
        :type: int

        :param src_adr: Source address (must be between 0 and 31).
        :type: int

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :param src_port: Source port (must be between 0 and 63).
        :type: int

        :param dst_port: Destination port (must be between 0 and 63).
        :type: int

        :param hmac: HMAC flag.
        :type: bool

        :param xtea: XTEA flag.
        :type: bool

        :param rdp: RDP flag.
        :type: bool

        :param crc: CRC flag.
        :type: bool

        :param pl: Is the payload of the CSP packet.
        :type: list[int]

        :return: A list with the byte sequence of the CSP packet.
        :rtype: list[int]
        """
        if not (0 <= prio <= 3):
            raise ValueError('The priority must be between 0 and 3!')

        if not (0 <= src_adr <= 31):
            raise ValueError('The source address must be between 0 and 31!')

        if not (0 <= dst_adr <= 31):
            raise ValueError('The destination address must be between 0 and 31!')

        if not (0 <= src_port <= 63):
            raise ValueError('The source port must be between 0 and 63!')

        if not (0 <= dst_port <= 63):
            raise ValueError('The destination port must be between 0 and 63!')

        pkt = list()

        # Header
        pkt.append((prio << 6) | (src_adr << 1) | ((dst_adr >> 4) & 1))

        pkt.append(((dst_adr & 15) << 4) | ((dst_port & 60) >> 2))

        pkt.append((dst_port << 6) | src_port)

        pkt.append((int(hmac) << 3) | (int(xtea) << 2) | (int(rdp) << 2) | int(crc))

        # Payload
        pkt += pl

        return pkt

    def encode_ping(self, prio, src_adr, dst_adr, num_bytes=100):
        """
        Encodes a CSP Ping Request packet.

        :param prio: Packet priority (must be between 0 and 3).
        :type: int

        :param src_adr: Source address (must be between 0 and 31).
        :type: int

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :param num_bytes: Number of bytes in the payload of the ping request.
        :type: int

        :return: A list with the byte sequence of the CSP Ping Request packet.
        :rtype: list[int]
        """
        pl = list()

        for i in range(num_bytes):
            pl.append(i)

        return self.encode(prio, src_adr, dst_adr, _CSP_PORT_PING, _CSP_PORT_PING, False, False, False, False, pl)

    def decode(self, pkt):
        """
        Decodes a CSP packet.

        :param data: Is the list of bytes to decode.
        :type: list[int]

        :return: The decoded data as a list with two bytes.
        :rtype: list[int]
        """
        if len(pkt) < 4:
            raise ValueError("Invalid CSP packet: Header too short!")
        else:
            header = self._decode_header(pkt[:4])
            pl = self._decode_pl(pkt[4:])

    def _decode_header(self, header):
        """
        Decodes the CSP header into a dictionary of fields.

        Args:
            header (bytes): The 4-byte CSP header.

        Returns:
            dict: Decoded header fields.
        """
        # CSP header bit layout:
        # Priority (2 bits) | Source (6 bits) | Destination (6 bits)
        # Reserved (4 bits) | HMAC (1 bit) | XTEA (1 bit)
        # RDP (1 bit) | CRC (1 bit)
        priority    = (header[0] >> 6) & 0b11
        src_adr     = (header[0] >> 1) & 0b11111
        dst_adr     = ((header[0] & 0b1) << 4) | ((header[1] >> 4) & 0b1111)
        dst_port    = ((header[1] & 0b1111) << 2) | ((header[2] >> 6) & 0b11)
        src_port    = header[2] & 0b111111
        hmac        = (header[3] >> 3) & 0b1
        xtea        = (header[3] >> 2) & 0b1
        rdp         = (header[3] >> 1) & 0b1
        crc         = header[3] & 0b1
        
        return {
            "priority": priority,
            "src_adr": src_adr,
            "dst_adr": dst_adr,
            "src_port": src_port,
            "dst_port": dst_port,
            "hmac": hmac,
            "xtea": xtea,
            "rdp": rdp,
            "crc": crc,
        }

    def _decode_pl(self, pl):
        pass
