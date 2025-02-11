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

import sys
import random

sys.path.append(".")

from spacelab_decoder.csp import CSP

def test_encode_ping():
    prio = random.randint(0, 3)
    src_adr = random.randint(0, 31)
    dst_adr = random.randint(0, 31)
    num_bytes = random.randint(1, 2**16)

    ping_pl = list()

    for i in range(num_bytes):
        ping_pl.append(i)

    csp = CSP()

    pkt = csp.encode_ping(prio, src_adr, dst_adr, num_bytes)

    assert (pkt[0] >> 6) == prio                                    # Priority
    assert ((pkt[0] >> 1) & 31) == src_adr                          # Source address
    assert (((pkt[0] & 1) << 4) | ((pkt[1] >> 4) & 15)) == dst_adr  # Destination address
    assert (((pkt[1] & 15) << 2) | ((pkt[2] >> 6) & 3)) == 1        # Ping port
    assert pkt[2] & 63 == 1                                         # Ping port
    assert ((pkt[3] >> 3) & 1) == 0                                 # HMAC
    assert ((pkt[3] >> 2) & 1) == 0                                 # XTEA
    assert ((pkt[3] >> 1) & 1)== 0                                  # RDP
    assert (pkt[3] & 1) == 0                                        # CRC
    assert pkt[4:] == ping_pl                                       # Payload
