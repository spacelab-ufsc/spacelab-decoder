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

import hashlib
import hmac

# Priorities
CSP_PRIO_CRITICAL   = 0
CSP_PRIO_HIGH       = 1
CSP_PRIO_NORM       = 2
CSP_PRIO_LOW        = 3

# Ports
_CSP_PORT_CMP       = 0
_CSP_PORT_PING      = 1
_CSP_PORT_PS        = 2
_CSP_PORT_MEMFREE   = 3
_CSP_PORT_REBOOT    = 4
_CSP_PORT_BUF_FREE  = 5
_CSP_PORT_UPTIME    = 6

# CMP Types
_CSP_CMP_REQUEST    = 0
_CSP_CMP_REPLY      = 255

# CMP Codes
_CSP_CMP_IDENT      = 1
_CSP_CMP_ROUTE_SET  = 2
_CSP_CMP_IF_STATS   = 3
_CSP_CMP_PEEK       = 4
_CSP_CMP_POKE       = 5
_CSP_CMP_CLOCK      = 6

class CSP:
    """
    CSP class.

    This class implements the CSP protocol.
    """

    def __init__(self, adr):
        """
        Class initialization.

        :param adr: Source address (must be between 0 and 31).
        :type: int

        :return: None
        :rtype: None
        """
        self.set_address(adr)

    def set_address(self, adr):
        """
        Sets the source address.

        :param adr: Source address (must be between 0 and 31).
        :type: int

        :return: None
        :rtype: None
        """
        if not (0 <= adr <= 31):
            raise ValueError('The source address must be between 0 and 31!')

        self._my_adr = adr

    def get_address(self):
        """
        Gets the source address.

        :return: The source address
        :rtype: int
        """
        return self._my_adr

    def encode(self, prio, dst_adr, src_port, dst_port, sfp, hmac, xtea, rdp, crc, pl, hmac_key=str()):
        """
        Encode a CSP packet.

        :param prio: Packet priority (must be between 0 and 3).
        :type: int

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :param src_port: Source port (must be between 0 and 63).
        :type: int

        :param dst_port: Destination port (must be between 0 and 63).
        :type: int

        :param sfp: SFP flag.
        :type: bool

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

        :param hmac_key: Is the HMAC key (optional, only used if the HMAC is enabled).
        :type: str

        :return: A list with the byte sequence of the CSP packet.
        :rtype: list[int]
        """
        if not (0 <= prio <= 3):
            raise ValueError('The priority must be between 0 and 3!')

        if not (0 <= dst_adr <= 31):
            raise ValueError('The destination address must be between 0 and 31!')

        if not (0 <= src_port <= 63):
            raise ValueError('The source port must be between 0 and 63!')

        if not (0 <= dst_port <= 63):
            raise ValueError('The destination port must be between 0 and 63!')

        pkt = list()

        # Header
        pkt.append((prio << 6) | (self.get_address() << 1) | ((dst_adr >> 4) & 1))

        pkt.append(((dst_adr & 15) << 4) | ((dst_port & 60) >> 2))

        pkt.append(((dst_port & 3) << 6) | src_port)

        pkt.append((int(sfp) << 4) | (int(hmac) << 3) | (int(xtea) << 2) | (int(rdp) << 2) | int(crc))

        # Payload
        pkt += pl

        # HMAC
        if hmac:
            pkt = self.append_hmac(pkt, hmac_key)

        return pkt

    def encode_cmp_ident(self, dst_adr):
        """
        Encodes a CSP CMP Ident Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :return: A list with the byte sequence of the CSP Ping Request packet.
        :rtype: list[int]
        """
        pl = [_CSP_CMP_REQUEST, _CSP_CMP_IDENT]

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_CMP, _CSP_PORT_CMP, False, False, False, False, False, pl)

    def encode_cmp_set_route(self, dst_adr, dest_node, next_hop_mac, ifc):
        """
        Encodes a CSP CMP Set Route Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :param dest_node: Is the destination node to set the route.
        :type: int

        :param next_hop_mac: Is the next hop MAC to set the route.
        :type: int

        :param ifc: Is the interface name to set the route.
        :type: str

        :return: A list with the byte sequence of the CSP Ping Request packet.
        :rtype: list[int]
        """
        if len(ifc) > 11:
            raise ValueError('The interface name must have up to 11 characters!')

        pl = [_CSP_CMP_REQUEST, _CSP_CMP_ROUTE_SET]

        pl.append(dest_node)
        pl.append(next_hop_mac)

        pl += [ord(c) for c in ifc]

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_CMP, _CSP_PORT_CMP, False, False, False, False, False, pl)

    def encode_cmp_if_stat(self, dst_adr, ifc):
        """
        Encodes a CSP CMP Interface Statistics Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :return: A list with the byte sequence of the CSP Ping Request packet.
        :rtype: list[int]
        """
        if len(ifc) > 11:
            raise ValueError('The interface name must have up to 11 characters!')

        pl = [_CSP_CMP_REQUEST, _CSP_CMP_IF_STATS]

        pl += [ord(c) for c in ifc]

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_CMP, _CSP_PORT_CMP, False, False, False, False, False, pl)

    def encode_cmp_peek(self, dst_adr, mem_adr, mem_len):
        """
        Encodes a CSP CMP Peek Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :param mem_adr: Memory address to peek.
        :type: int

        :param mem_len: Number of bytes to peek.
        :type: int

        :return: A list with the byte sequence of the CSP Ping Request packet.
        :rtype: list[int]
        """
        if mem_len > 200:
            raise ValueError('The number of bytes to read must be lesser than 200!')

        pl = [_CSP_CMP_REQUEST, _CSP_CMP_PEEK]

        pl += list(mem_adr.to_bytes(4, 'big'))

        pl.append(mem_len)

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_CMP, _CSP_PORT_CMP, False, False, False, False, False, pl)

    def encode_cmp_poke(self, dst_adr, mem_adr, mem_data):
        """
        Encodes a CSP CMP Poke Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :param mem_adr: Memory address to poke.
        :type: int

        :param mem_data: Data to write in the given address.
        :type: int

        :return: A list with the byte sequence of the CSP Ping Request packet.
        :rtype: list[int]
        """
        if len(mem_data) > 200:
            raise ValueError('The number of bytes to write must be lesser than 200!')

        pl = [_CSP_CMP_REQUEST, _CSP_CMP_POKE]

        pl += list(mem_adr.to_bytes(4, 'big'))

        pl.append(len(mem_data))

        pl += mem_data

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_CMP, _CSP_PORT_CMP, False, False, False, False, False, pl)

    def encode_cmp_set_clock(self, dst_adr, sec, ns):
        """
        Encodes a CSP CMP Set Clock Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :param sec: Seconds of the clock to set.
        :type: int

        :param ns: Nanoseconds of the clock to set.
        :type: int

        :return: A list with the byte sequence of the CSP Ping Request packet.
        :rtype: list[int]
        """
        pl = [_CSP_CMP_REQUEST, _CSP_CMP_CLOCK]

        pl.append((sec >> 24) & 0xFF)
        pl.append((sec >> 16) & 0xFF)
        pl.append((sec >> 8) & 0xFF)
        pl.append((sec >> 0) & 0xFF)

        pl.append((ns >> 24) & 0xFF)
        pl.append((ns >> 16) & 0xFF)
        pl.append((ns >> 8) & 0xFF)
        pl.append((ns >> 0) & 0xFF)

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_CMP, _CSP_PORT_CMP, False, False, False, False, False, pl)

    def encode_cmp_get_clock(self, dst_adr):
        """
        Encodes a CSP CMP Get Clock Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :return: A list with the byte sequence of the CSP Ping Request packet.
        :rtype: list[int]
        """
        pl = [_CSP_CMP_REQUEST, _CSP_CMP_CLOCK]

        pl += 8*[0]

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_CMP, _CSP_PORT_CMP, False, False, False, False, False, pl)

    def encode_ping(self, dst_adr, num_bytes=100):
        """
        Encodes a CSP Ping Request packet.

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

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_PING, _CSP_PORT_PING, False, False, False, False, False, pl)

    def encode_ps(self, dst_adr):
        """
        Encodes a CSP PS Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :return: A list with the byte sequence of the CSP Ping Request packet.
        :rtype: list[int]
        """
        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_PS, _CSP_PORT_PS, False, False, False, False, False, [0x55])

    def encode_memfree(self, dst_adr):
        """
        Encodes a CSP Mem Free Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :return: A list with the byte sequence of the CSP Mem Free Request packet.
        :rtype: list[int]
        """
        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_MEMFREE, _CSP_PORT_MEMFREE, False, False, False, False, False, [])

    def encode_reboot(self, dst_adr):
        """
        Encodes a CSP Reboot Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :return: A list with the byte sequence of the CSP Reboot Request packet.
        :rtype: list[int]
        """
        pl = [0x80, 0x07, 0x80, 0x07]   # Magic word

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_REBOOT, _CSP_PORT_REBOOT, False, False, False, False, False, pl)

    def encode_shutdown(self, dst_adr):
        """
        Encodes a CSP Shutdown Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :return: A list with the byte sequence of the CSP Shutdown Request packet.
        :rtype: list[int]
        """
        pl = [0xD1, 0xE5, 0x52, 0x9A]   # Magic word

        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_REBOOT, _CSP_PORT_REBOOT, False, False, False, False, False, pl)

    def encode_buf_free(self, dst_adr):
        """
        Encodes a CSP Buffer Free Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :return: A list with the byte sequence of the CSP Buffer Free Request packet.
        :rtype: list[int]
        """
        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_BUF_FREE, _CSP_PORT_BUF_FREE, False, False, False, False, False, [])

    def encode_uptime(self, dst_adr):
        """
        Encodes a CSP Uptime Request packet.

        :param dst_adr: Destination address (must be between 0 and 31).
        :type: int

        :return: A list with the byte sequence of the CSP Uptime Request packet.
        :rtype: list[int]
        """
        return self.encode(CSP_PRIO_NORM, dst_adr, _CSP_PORT_UPTIME, _CSP_PORT_UPTIME, False, False, False, False, False, [])

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

        header = self._decode_header(pkt[:4])
        pl = self._decode_pl(pkt[4:])

        return header | pl

    def _decode_header(self, header):
        """
        Decodes the CSP header into a dictionary of fields.

        :param header: The 4-byte CSP header.
        :type: list[int]

        :return: Decoded header fields.
        :rtype: dict
        """
        # CSP header bit layout:
        # Priority (2 bits) | Source (6 bits) | Destination (6 bits)
        # Reserved (3 bits) | SFP (1 bit) | HMAC (1 bit) | XTEA (1 bit)
        # RDP (1 bit) | CRC (1 bit)
        priority    = (header[0] >> 6) & 0b11
        src_adr     = (header[0] >> 1) & 0b11111
        dst_adr     = ((header[0] & 0b1) << 4) | ((header[1] >> 4) & 0b1111)
        dst_port    = ((header[1] & 0b1111) << 2) | ((header[2] >> 6) & 0b11)
        src_port    = header[2] & 0b111111
        sfp         = bool((header[3] >> 4) & 0b1)
        hmac        = bool((header[3] >> 3) & 0b1)
        xtea        = bool((header[3] >> 2) & 0b1)
        rdp         = bool((header[3] >> 1) & 0b1)
        crc         = bool(header[3] & 0b1)
        
        return {
            "priority": priority,
            "src_adr": src_adr,
            "dst_adr": dst_adr,
            "src_port": src_port,
            "dst_port": dst_port,
            "sfp": sfp,
            "hmac": hmac,
            "xtea": xtea,
            "rdp": rdp,
            "crc": crc,
        }

    def _decode_pl(self, pl):
        return {"payload": pl}

    def append_hmac(self, pkt, key, inc_header=False):
        """
        Enables the HMAC authentication to an existing packet.

        :param pkt: Is the CSP packet to add the HMAC hash.
        :type: list

        :param key: Is the HMAC key to compute the hash.
        :type: str

        :param inc_header: A flag to indicate if the HMAC must be computed considering the CSP header or not.
        :type: bool

        :return: The given CSP packet with the HMAC hash enabled.
        :rtype: list
        """
        # Enabling HMAC flag in header
        pkt[3] |= (1 << 3)

        # Defining if the HMAC will be computed considering the CSP header or not
        pkt4hmac = list()
        if inc_header:
            pkt4hmac = pkt.copy()
        else:
            pkt4hmac = pkt[4:].copy()

        # Compute the HMAC hash
        hashed = hmac.new(key.encode('utf-8'), bytes(pkt4hmac), hashlib.sha1)

        return pkt + list(hashed.digest())[:4]  # Only the four first bytes are used in the CSP implementation
