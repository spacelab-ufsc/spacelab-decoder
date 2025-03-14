#
#  test_satellite.py
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

import os
import json

import pytest

from satellite import Satellite
from link import Link

# Sample JSON data for testing
SAMPLE_JSON = {
    "name": "TestSatellite",
    "links": [
        {
            "id": "link1",
            "name": "Link1",
            "direction": "up",
            "frequency": 435000000,
            "modulation": "GFSK",
            "baudrate": 9600,
            "preamble": [0xAA],
            "sync_word": [0x55],
            "protocol_link": "AX.25",
            "protocol_network": "IP"
        },
        {
            "id": "link2",
            "name": "Link2",
            "direction": "down",
            "frequency": 145000000,
            "modulation": "BPSK",
            "baudrate": 4800,
            "preamble": [0xBB],
            "sync_word": [0x66],
            "protocol_link": "AX.25",
            "protocol_network": "IP"
        }
    ]
}

@pytest.fixture
def sample_satellite():
    """Fixture to create a Satellite instance with sample data."""
    # Create a temporary JSON file
    file = os.path.abspath(os.getcwd()) + "/sample.json"
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_JSON, f, indent=4)
    satellite = Satellite()
    satellite.load_from_file('sample.json')
    return satellite

def test_load_from_file(sample_satellite):
    """Test loading satellite data from a JSON file."""
    # Load the satellite data from the file
    satellite = sample_satellite

    # Verify the satellite name
    assert satellite.get_name() == "TestSatellite"

    # Verify the links
    links = satellite.get_links()
    assert len(links) == 2

    # Verify the first link
    link1 = links[0]
    assert link1.get_id() == "link1"
    assert link1.get_name() == "Link1"
    assert link1.get_direction() == "up"
    assert link1.get_frequency() == 435000000
    assert link1.get_modulation() == "GFSK"
    assert link1.get_baudrate() == 9600
    assert link1.get_preamble() == [0xAA]
    assert link1.get_sync_word() == [0x55]
    assert link1.get_link_protocol() == "AX.25"
    assert link1.get_network_protocol() == "IP"

    # Verify the second link
    link2 = links[1]
    assert link2.get_id() == "link2"
    assert link2.get_name() == "Link2"
    assert link2.get_direction() == "down"
    assert link2.get_frequency() == 145000000
    assert link2.get_modulation() == "BPSK"
    assert link2.get_baudrate() == 4800
    assert link2.get_preamble() == [0xBB]
    assert link2.get_sync_word() == [0x66]
    assert link2.get_link_protocol() == "AX.25"
    assert link2.get_network_protocol() == "IP"

def test_set_active_link(sample_satellite):
    """Test setting the active link."""
    satellite = sample_satellite

    # Set the first link as active
    satellite.set_active_link(0)
    active_link = satellite.get_active_link()
    assert active_link.get_id() == "link1"
    assert active_link.get_name() == "Link1"

    # Set the second link as active
    satellite.set_active_link(1)
    active_link = satellite.get_active_link()
    assert active_link.get_id() == "link2"
    assert active_link.get_name() == "Link2"

def test_str_method(sample_satellite):
    """Test the string representation of the Satellite class."""
    satellite = sample_satellite
    expected_output = "Satellite: TestSatellite\n\rLinks:\n\r" + str(satellite.get_links()[0]) + str(satellite.get_links()[1])
    assert str(satellite) == expected_output

def test_set_name():
    """Test setting the satellite name."""
    satellite = Satellite()
    satellite.set_name("NewSatellite")
    assert satellite.get_name() == "NewSatellite"

def test_set_links():
    """Test setting the links."""
    satellite = Satellite()
    link1 = Link()
    link1.set_id(1)
    link1.set_name("TestLink1")
    link2 = Link()
    link2.set_id(2)
    link2.set_name("TestLink2")
    satellite.set_links([link1, link2])
    links = satellite.get_links()
    assert len(links) == 2
    assert links[0].get_name() == "TestLink1"
    assert links[1].get_name() == "TestLink2"
