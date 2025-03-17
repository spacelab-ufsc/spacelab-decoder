#
#  test_csp.py
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

import random
import string
import hashlib
import hmac
import time

from csp import CSP, CSP_PRIO_NORM

def test_address_config():
    adr1 = random.randint(0, 31)

    csp = CSP(adr1)

    assert csp.get_address() == adr1

    adr2 = random.randint(0, 31)

    csp.set_address(adr2)

    assert csp.get_address() == adr2

def test_encode_cmp_ident():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    csp = CSP(src_adr)

    pkt = csp.encode_cmp_ident(dst_adr)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 0        # CMP port
    assert pkt[2] & 63 == 0                                         # CMP port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4:] == [0, 1]                                        # Payload

def test_encode_cmp_set_route():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)
    dest_node = random.randint(0, 255)
    next_hop_mac = random.randint(0, 255)
    if_name = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=random.randint(1, 11)))

    csp = CSP(src_adr)

    pkt = csp.encode_cmp_set_route(dst_adr, dest_node, next_hop_mac, if_name)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 0        # CMP port
    assert pkt[2] & 63 == 0                                         # CMP port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4] == 0                                              # CMP Type
    assert pkt[5] == 2                                              # CMP Code
    assert pkt[6] == dest_node                                      # Destination node
    assert pkt[7] == next_hop_mac                                   # Next hop MAC
    assert pkt[8:] == [ord(c) for c in if_name]                     # Interface

def test_encode_cmp_if_stat():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)
    if_name = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=random.randint(1, 11)))

    csp = CSP(src_adr)

    pkt = csp.encode_cmp_if_stat(dst_adr, if_name)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 0        # CMP port
    assert pkt[2] & 63 == 0                                         # CMP port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4] == 0                                              # CMP Type
    assert pkt[5] == 3                                              # CMP Code
    assert pkt[6:] == [ord(c) for c in if_name]                     # Payload

def test_encode_cmp_peek():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)
    mem_adr = random.randint(0, (2**32) - 1)
    mem_len = random.randint(0, 200)

    csp = CSP(src_adr)

    pkt = csp.encode_cmp_peek(dst_adr, mem_adr, mem_len)

    pl = [0, 4]

    pl += list(mem_adr.to_bytes(4, 'big'))

    pl.append(mem_len)

    mem_adr_list = list()
    mem_adr_list.append((mem_adr >> 24) & 0xFF)
    mem_adr_list.append((mem_adr >> 16) & 0xFF)
    mem_adr_list.append((mem_adr >> 8) & 0xFF)
    mem_adr_list.append((mem_adr >> 0) & 0xFF)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 0        # CMP port
    assert pkt[2] & 63 == 0                                         # CMP port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4] == 0                                              # CMP Type
    assert pkt[5] == 4                                              # CMP Code
    assert pkt[6:10] == mem_adr_list                                # Memory address
    assert pkt[10] == mem_len                                       # Memory length

def test_encode_cmp_poke():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)
    mem_adr = random.randint(0, (2**32) - 1)
    mem_len = random.randint(0, 200)
    mem_data = list()
    for i in range(mem_len):
        mem_data.append(random.randint(0, 255))

    csp = CSP(src_adr)

    pkt = csp.encode_cmp_poke(dst_adr, mem_adr, mem_data)

    pl = [0, 5]

    pl += list(mem_adr.to_bytes(4, 'big'))

    pl.append(mem_len)

    mem_adr_list = list()
    mem_adr_list.append((mem_adr >> 24) & 0xFF)
    mem_adr_list.append((mem_adr >> 16) & 0xFF)
    mem_adr_list.append((mem_adr >> 8) & 0xFF)
    mem_adr_list.append((mem_adr >> 0) & 0xFF)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 0        # CMP port
    assert pkt[2] & 63 == 0                                         # CMP port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4] == 0                                              # CMP Type
    assert pkt[5] == 5                                              # CMP Code
    assert pkt[6:10] == mem_adr_list                                # Payload
    assert pkt[10] == mem_len                                       # Payload
    assert pkt[11:] == mem_data                                     # Memory data

def test_encode_cmp_set_clock():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)
    ts = int(time.time())
    ns = random.randint(0, 2**32-1)

    ts_list = list()
    ts_list.append((ts >> 24) & 0xFF)
    ts_list.append((ts >> 16) & 0xFF)
    ts_list.append((ts >> 8) & 0xFF)
    ts_list.append((ts >> 0) & 0xFF)

    ns_list = list()
    ns_list.append((ns >> 24) & 0xFF)
    ns_list.append((ns >> 16) & 0xFF)
    ns_list.append((ns >> 8) & 0xFF)
    ns_list.append((ns >> 0) & 0xFF)

    csp = CSP(src_adr)

    pkt = csp.encode_cmp_set_clock(dst_adr, ts ,ns)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 0        # CMP port
    assert pkt[2] & 63 == 0                                         # CMP port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4] == 0                                              # CMP Type
    assert pkt[5] == 6                                              # CMP Code
    assert pkt[6:10] == ts_list                                     # Seconds
    assert pkt[10:14] == ns_list                                    # Nanoseconds

def test_encode_cmp_get_clock():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    csp = CSP(src_adr)

    pkt = csp.encode_cmp_get_clock(dst_adr)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 0        # CMP port
    assert pkt[2] & 63 == 0                                         # CMP port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4] == 0                                              # CMP Type
    assert pkt[5] == 6                                              # CMP Code
    assert pkt[6:15] == 8*[0]                                       # Payload

def test_encode_ping():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)
    num_bytes = random.randint(1, 2**16)

    ping_pl = list()

    for i in range(num_bytes):
        ping_pl.append(i)

    csp = CSP(src_adr)

    pkt = csp.encode_ping(dst_adr, num_bytes)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 1        # Ping port
    assert pkt[2] & 63 == 1                                         # Ping port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4:] == ping_pl                                       # Payload

def test_encode_memfree():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    csp = CSP(src_adr)

    pkt = csp.encode_ps(dst_adr)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 2        # PS port
    assert pkt[2] & 63 == 2                                         # PS port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4:] == [0x55]                                        # Payload

def test_encode_memfree():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    csp = CSP(src_adr)

    pkt = csp.encode_memfree(dst_adr)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 3        # Memfree port
    assert pkt[2] & 63 == 3                                         # Memfree port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert len(pkt) == 4                                            # Payload

def test_encode_reboot():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    csp = CSP(src_adr)

    pkt = csp.encode_reboot(dst_adr)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 4        # Reboot port
    assert pkt[2] & 63 == 4                                         # Reboot port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4:] == [0x80, 0x07, 0x80, 0x07]                      # Payload

def test_encode_shutdown():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    csp = CSP(src_adr)

    pkt = csp.encode_shutdown(dst_adr)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 4        # Reboot port
    assert pkt[2] & 63 == 4                                         # Reboot port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4:] == [0xD1, 0xE5, 0x52, 0x9A]                      # Payload

def test_encode_buf_free():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    csp = CSP(src_adr)

    pkt = csp.encode_buf_free(dst_adr)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 5        # Buffer free port
    assert pkt[2] & 63 == 5                                         # Buffer free port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert len(pkt) == 4                                            # Payload

def test_encode_uptime():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    csp = CSP(src_adr)

    pkt = csp.encode_uptime(dst_adr)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 6        # Uptime port
    assert pkt[2] & 63 == 6                                         # Uptime port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert len(pkt) == 4                                            # Payload

def test_encode():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    src_port = random.randint(0, 31)
    dst_port = random.randint(0, 31)

    pl = list()
    for i in range(random.randint(0, 2**16-1)):
        pl.append(random.randint(0, 2**8-1))

    csp = CSP(src_adr)

    pkt = csp.encode(CSP_PRIO_NORM, dst_adr, src_port, dst_port, False, False, False, False, False, pl)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == dst_port # Destination port
    assert pkt[2] & 63 == src_port                                  # Source port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4:] == pl                                            # Payload

def test_encode_with_hmac():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    src_port = random.randint(0, 31)
    dst_port = random.randint(0, 31)

    pl = list()
    for i in range(random.randint(0, 2**16-1)):
        pl.append(random.randint(0, 2**8-1))

    key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))
    hashed = hmac.new(key.encode('utf-8'), bytes(pl), hashlib.sha1)
    pl_hash = list(hashed.digest())

    csp = CSP(src_adr)

    pkt = csp.encode(CSP_PRIO_NORM, dst_adr, src_port, dst_port, False, True, False, False, False, pl, key)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == dst_port # Destination port
    assert pkt[2] & 63 == src_port                                  # Source port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 1                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4:-20] == pl                                         # Payload
    assert pkt[-20:] == pl_hash                                     # HMAC hash

def test_decode():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    src_port = random.randint(0, 31)
    dst_port = random.randint(0, 31)

    pl = list()
    for i in range(random.randint(0, 2**16-1)):
        pl.append(random.randint(0, 2**8-1))

    csp = CSP(src_adr)

    pkt = csp.encode(CSP_PRIO_NORM, dst_adr, src_port, dst_port, False, False, False, False, False, pl)
    pkt_dec = csp.decode(pkt)

    assert pkt_dec["priority"] == 2         # Priority
    assert pkt_dec["src_adr"] == src_adr    # Source address
    assert pkt_dec["dst_adr"] == dst_adr    # Destination address
    assert pkt_dec["src_port"] == src_port  # Source port
    assert pkt_dec["dst_port"] == dst_port  # Destination port
    assert pkt_dec["sfp"] == False          # SFP
    assert pkt_dec["hmac"] == False         # HMAC
    assert pkt_dec["xtea"] == False         # XTEA
    assert pkt_dec["rdp"] == False          # RDP
    assert pkt_dec["crc"] == False          # CRC
    assert pkt_dec["payload"] == pl         # Payloadlist

def test_append_hmac():
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)

    src_port = random.randint(0, 31)
    dst_port = random.randint(0, 31)

    pl = list()
    for i in range(random.randint(0, 2**16-1)):
        pl.append(random.randint(0, 2**8-1))

    key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16))
    hashed = hmac.new(key.encode('utf-8'), bytes(pl), hashlib.sha1)
    pl_hash = list(hashed.digest())

    csp = CSP(src_adr)

    pkt = csp.encode(CSP_PRIO_NORM, dst_adr, src_port, dst_port, False, False, False, False, False, pl)

    pkt = csp.append_hmac(pkt, key)

    assert (pkt[0] >> 6) == 2                                       # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == dst_port # Source port
    assert pkt[2] & 63 == src_port                                  # Destination port
    assert ((pkt[3] >> 4) & 1) == 0                                 # SFP
    assert ((pkt[3] >> 3) & 1) == 1                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4:-20] == pl                                         # Payload
    assert pkt[-20:] == pl_hash                                     # HMAC hash
