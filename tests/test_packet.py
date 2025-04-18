#
#  test_packet.py
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

import pytest

from packet import PacketSLP, PacketCSP

# Sample satellite configuration JSON for testing
SAMPLE_SAT_CONFIG = {
    "id": "spacelab-transmitter",
    "name": "SpaceLab-Transmitter",
    "links": [
        {
            "id": "uplink_ngham",
            "name": "Uplink (NGHam)",
            "baudrate": 1200,
            "direction": "up",
            "frequency": 145.9e6,
            "modulation": "GMSK",
            "preamble": [170, 170, 170, 170],
            "sync_word": [93, 230, 42, 126],
            "protocol_link": "NGHam",
            "protocol_network": "SLP",
            "types": [
                {
                    "name": "Ping request",
                    "fields": [
                        {
                            "id": "pkt_id",
                            "name": "ID",
                            "initial_pos": 0,
                            "final_pos": 0,
                            "value": 64,
                            "conversion": "int(pkt[0])",
                            "unit": ""
                        },
                        {
                            "id": "pkt_src_adr",
                            "name": "Source callsign",
                            "initial_pos": 1,
                            "final_pos": 7,
                            "value": 0,
                            "conversion": "\"\".join([chr(val) for val in pkt[1:8]])",
                            "unit": ""
                        }
                    ]
                },
                {
                    "name": "Broadcast message",
                    "fields": [
                        {
                            "id": "pkt_id",
                            "name": "ID",
                            "initial_pos": 0,
                            "final_pos": 0,
                            "value": 66,
                            "conversion": "int(pkt[0])",
                            "unit": ""
                        },
                        {
                            "id": "pkt_src_adr",
                            "name": "Source callsign",
                            "initial_pos": 1,
                            "final_pos": 7,
                            "value": 0,
                            "conversion": "\"\".join([chr(val) for val in pkt[1:8]])",
                            "unit": ""
                        },
                        {
                            "id": "pkt_dst_adr",
                            "name": "Destination callsign",
                            "initial_pos": 8,
                            "final_pos": 14,
                            "value": 0,
                            "conversion": "\"\".join([chr(val) for val in pkt[8:15]])",
                            "unit": ""
                        },
                        {
                            "id": "txt_msg",
                            "name": "Message",
                            "initial_pos": 15,
                            "final_pos": 52,
                            "value": 0,
                            "conversion": "\"\".join([chr(val) for val in pkt[15:53]])",
                            "unit": ""
                        }
                    ]
                }
            ]
        },
        {
            "id": "uplink_csp",
            "name": "Uplink (CSP)",
            "baudrate": 4800,
            "direction": "up",
            "frequency": 402.9e6,
            "modulation": "GMSK",
            "preamble": [170, 170, 170, 170, 170, 170, 170, 170],
            "sync_word": [147, 11, 81, 222],
            "protocol_link": "AX100-Mode5",
            "protocol_network": "CSP",
            "types": [
                {
                    "name": "CMP ident request",
                    "fields": [
                        {
                            "id": "csp_prio",
                            "name": "Priority",
                            "initial_pos": 0,
                            "final_pos": 0,
                            "value": 2,
                            "conversion": "int(pkt[0] >> 6)",
                            "unit": ""
                        },
                        {
                            "id": "csp_src_adr",
                            "name": "Source Address",
                            "initial_pos": 0,
                            "final_pos": 0,
                            "value": 10,
                            "conversion": "int((pkt[0] >> 1) & 31)",
                            "unit": ""
                        },
                        {
                            "id": "csp_dst_adr",
                            "name": "Destination Address",
                            "initial_pos": 0,
                            "final_pos": 1,
                            "value": 1,
                            "conversion": "int(((pkt[0] & 1) << 4) | (pkt[1] >> 4))",
                            "unit": ""
                        },
                        {
                            "id": "csp_dst_port",
                            "name": "Destination Port",
                            "initial_pos": 1,
                            "final_pos": 2,
                            "value": 0,
                            "conversion": "int(((pkt[1] & 15) << 2) | (pkt[2] >> 6))",
                            "unit": ""
                        },
                        {
                            "id": "csp_src_port",
                            "name": "Source Port",
                            "initial_pos": 2,
                            "final_pos": 2,
                            "value": 0,
                            "conversion": "int(pkt[2] & 63)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_sfp",
                            "name": "SFP Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 4) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_hmac",
                            "name": "HMAC Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 3) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_xtea",
                            "name": "XTEA Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 2) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_rdp",
                            "name": "RDP Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 1) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_crc",
                            "name": "CRC Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool(pkt[3] & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_cmp_type",
                            "name": "CMP Type",
                            "initial_pos": 4,
                            "final_pos": 4,
                            "value": 255,
                            "conversion": "pkt[4]",
                            "unit": ""
                        },
                        {
                            "id": "csp_cmp_code",
                            "name": "CMP Code",
                            "initial_pos": 5,
                            "final_pos": 5,
                            "value": 1,
                            "conversion": "pkt[5]",
                            "unit": ""
                        }
                    ]
                },
                {
                    "name": "CMP route set request",
                    "fields": [
                        {
                            "id": "csp_prio",
                            "name": "Priority",
                            "initial_pos": 0,
                            "final_pos": 0,
                            "value": 2,
                            "conversion": "int(pkt[0] >> 6)",
                            "unit": ""
                        },
                        {
                            "id": "csp_src_adr",
                            "name": "Source Address",
                            "initial_pos": 0,
                            "final_pos": 0,
                            "value": 10,
                            "conversion": "int((pkt[0] >> 1) & 31)",
                            "unit": ""
                        },
                        {
                            "id": "csp_dst_adr",
                            "name": "Destination Address",
                            "initial_pos": 0,
                            "final_pos": 1,
                            "value": 1,
                            "conversion": "int(((pkt[0] & 1) << 4) | (pkt[1] >> 4))",
                            "unit": ""
                        },
                        {
                            "id": "csp_dst_port",
                            "name": "Destination Port",
                            "initial_pos": 1,
                            "final_pos": 2,
                            "value": 0,
                            "conversion": "int(((pkt[1] & 15) << 2) | (pkt[2] >> 6))",
                            "unit": ""
                        },
                        {
                            "id": "csp_src_port",
                            "name": "Source Port",
                            "initial_pos": 2,
                            "final_pos": 2,
                            "value": 0,
                            "conversion": "int(pkt[2] & 63)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_sfp",
                            "name": "SFP Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 4) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_hmac",
                            "name": "HMAC Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 3) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_xtea",
                            "name": "XTEA Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 2) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_rdp",
                            "name": "RDP Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 1) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_crc",
                            "name": "CRC Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool(pkt[3] & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_cmp_type",
                            "name": "CMP Type",
                            "initial_pos": 4,
                            "final_pos": 4,
                            "value": 255,
                            "conversion": "pkt[4]",
                            "unit": ""
                        },
                        {
                            "id": "csp_cmp_code",
                            "name": "CMP Code",
                            "initial_pos": 5,
                            "final_pos": 5,
                            "value": 2,
                            "conversion": "pkt[5]",
                            "unit": ""
                        },
                        {
                            "id": "csp_cmp_route_dst_node",
                            "name": "Route Destination Node",
                            "initial_pos": 6,
                            "final_pos": 6,
                            "value": 0,
                            "conversion": "pkt[6]",
                            "unit": ""
                        },
                        {
                            "id": "csp_cmp_route_next_hop_mac",
                            "name": "Route Next Hop MAC",
                            "initial_pos": 7,
                            "final_pos": 7,
                            "value": 0,
                            "conversion": "pkt[7]",
                            "unit": ""
                        },
                        {
                            "id": "csp_cmp_route_if",
                            "name": "Route Interface",
                            "initial_pos": 8,
                            "final_pos": 18,
                            "value": 0,
                            "conversion": "\"\".join([chr(val) for val in pkt[8:19]])",
                            "unit": ""
                        }
                    ]
                },
                {
                    "name": "Ping request",
                    "fields": [
                        {
                            "id": "csp_prio",
                            "name": "Priority",
                            "initial_pos": 0,
                            "final_pos": 0,
                            "value": 2,
                            "conversion": "int(pkt[0] >> 6)",
                            "unit": ""
                        },
                        {
                            "id": "csp_src_adr",
                            "name": "Source Address",
                            "initial_pos": 0,
                            "final_pos": 0,
                            "value": 10,
                            "conversion": "int((pkt[0] >> 1) & 31)",
                            "unit": ""
                        },
                        {
                            "id": "csp_dst_adr",
                            "name": "Destination Address",
                            "initial_pos": 0,
                            "final_pos": 1,
                            "value": 1,
                            "conversion": "int(((pkt[0] & 1) << 4) | (pkt[1] >> 4))",
                            "unit": ""
                        },
                        {
                            "id": "csp_dst_port",
                            "name": "Destination Port",
                            "initial_pos": 1,
                            "final_pos": 2,
                            "value": 1,
                            "conversion": "int(((pkt[1] & 15) << 2) | (pkt[2] >> 6))",
                            "unit": ""
                        },
                        {
                            "id": "csp_src_port",
                            "name": "Source Port",
                            "initial_pos": 2,
                            "final_pos": 2,
                            "value": 1,
                            "conversion": "int(pkt[2] & 63)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_sfp",
                            "name": "SFP Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 4) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_hmac",
                            "name": "HMAC Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 3) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_xtea",
                            "name": "XTEA Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 2) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_rdp",
                            "name": "RDP Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool((pkt[3] >> 1) & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_flag_crc",
                            "name": "CRC Enabled",
                            "initial_pos": 3,
                            "final_pos": 3,
                            "value": 0,
                            "conversion": "bool(pkt[3] & 1)",
                            "unit": ""
                        },
                        {
                            "id": "csp_ping_pl",
                            "name": "Payload",
                            "initial_pos": 4,
                            "final_pos": 103,
                            "value": 0,
                            "conversion": "pkt[4:9]",
                            "unit": ""
                        }
                    ]
                }
            ]
        }
    ]
}

# Save the sample satellite configuration to a temporary file
@pytest.fixture
def sat_config_file(tmp_path):
    config_file = tmp_path / "sat_config.json"
    with open(config_file, 'w') as f:
        json.dump(SAMPLE_SAT_CONFIG, f)
    return config_file

@pytest.fixture
def slp_packet(sat_config_file):
    # Create a PacketSLP object with a sample SLP packet
    pkt_raw = [0x40, 0x20, 0x20, 0x50, 0x50, 0x35, 0x55, 0x46]  # Sample SLP packet
    return PacketSLP(sat_config_file, pkt_raw)

@pytest.fixture
def csp_packet(sat_config_file):
    # Create a PacketCSP object with a sample CSP packet
    pkt_raw = [148, 16, 65, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
    return PacketCSP(sat_config_file, pkt_raw)

def test_packet_slp_init(slp_packet):
    # Test initialization of PacketSLP
    assert slp_packet.sat_packet == SAMPLE_SAT_CONFIG
    assert slp_packet.packet == [0x40, 0x20, 0x20, 0x50, 0x50, 0x35, 0x55, 0x46]

def test_packet_csp_init(csp_packet):
    # Test initialization of PacketCSP
    assert csp_packet.sat_packet == SAMPLE_SAT_CONFIG
    assert csp_packet.packet == [148, 16, 65, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]

def test_packet_slp_str(slp_packet):
    # Test __str__ method for PacketSLP
    expected_output = (
        "\tSatellite: SpaceLab-Transmitter\n"
        "\tLink: Uplink (NGHam)\n"
        "\tData Source: Ping request\n"
        "\tLink Protocol: NGHam\n"
        "\tNetwork Protocol: SLP\n"
        "\tData:\n"
        "\t\tID: 64 \n"
        "\t\tSource callsign:   PP5UF \n"
    )
    assert str(slp_packet) == expected_output

def test_packet_csp_str(csp_packet):
    # Test __str__ method for PacketCSP
    expected_output = (
        "\tSatellite: SpaceLab-Transmitter\n"
        "\tLink: Uplink (CSP)\n"
        "\tData Source: Ping request\n"
        "\tLink Protocol: AX100-Mode5\n"
        "\tNetwork Protocol: CSP\n"
        "\tData:\n"
        "\t\tPriority: 2 \n"
        "\t\tSource Address: 10 \n"
        "\t\tDestination Address: 1 \n"
        "\t\tDestination Port: 1 \n"
        "\t\tSource Port: 1 \n"
        "\t\tSFP Enabled: False \n"
        "\t\tHMAC Enabled: False \n"
        "\t\tXTEA Enabled: False \n"
        "\t\tRDP Enabled: False \n"
        "\t\tCRC Enabled: False \n"
        "\t\tPayload: [0, 1, 2, 3, 4] \n"
    )
    assert str(csp_packet) == expected_output

def test_packet_slp_get_data(slp_packet):
    # Test get_data method for PacketSLP
    expected_data = {
        "pkt_id": "64",
        "pkt_src_adr": "  PP5UF"
    }

    assert json.loads(slp_packet.get_data()) == expected_data

def test_packet_csp_get_data(csp_packet):
    # Test get_data method for PacketCSP
    expected_data = {
        "csp_prio": "2",
        "csp_src_adr": "10",
        "csp_dst_adr": "1",
        "csp_dst_port": "1",
        "csp_src_port": "1",
        "csp_flag_sfp": "False",
        "csp_flag_hmac": "False",
        "csp_flag_xtea": "False",
        "csp_flag_rdp": "False",
        "csp_flag_crc": "False",
        "csp_ping_pl": "[0, 1, 2, 3, 4]",
    }

    assert json.loads(csp_packet.get_data()) == expected_data

def test_packet_slp_unknown_packet_id(sat_config_file):
    # Test PacketSLP with an unknown packet ID
    pkt_raw = [0xFF, 0x04]  # Unknown packet ID
    with pytest.raises(RuntimeError):
        x = str(PacketSLP(sat_config_file, pkt_raw))

def test_packet_csp_unknown_dst_port(sat_config_file):
    # Test PacketCSP with an unknown destination port
    pkt_raw = [0x00, 0x80, 0xFF, 0x40, 0xFF]  # Unknown destination port
    with pytest.raises(RuntimeError):
        x = str(PacketCSP(sat_config_file, pkt_raw))
